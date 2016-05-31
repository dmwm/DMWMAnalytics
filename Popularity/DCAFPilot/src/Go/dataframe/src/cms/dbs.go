/*
 *
 * Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
 * Description: part of cms package responsible for DBS calls
 * Created    : Wed Feb 10 19:31:44 EST 2016
 */
package cms

import (
	"encoding/json"
	"fmt"
	"math"
	"regexp"
	"strings"
	"utils"
)

// helper function to load DBS data stream
func loadDBSData(furl string, data []byte) []Record {
	var out []Record
	err := json.Unmarshal(data, &out)
	if err != nil {
		if utils.VERBOSE > 1 {
			msg := fmt.Sprintf("DBS unable to unmarshal the data, furl=%s, data=%s, error=%v", furl, string(data), err)
			fmt.Println(msg)
		}
		return out
	}
	return out
}

// helper function to get all datasets from DBS instance
func dbsTiers(dbsinst string) []string {
	var tiers []string
	api := "datatiers"
	for _, dbsinst := range dbsInstances() {
		furl := fmt.Sprintf("%s/%s", dbsUrl(dbsinst), api)
		response := utils.FetchResponse(furl, "")
		if response.Error == nil {
			records := loadDBSData(furl, response.Data)
			if utils.VERBOSE > 1 {
				fmt.Println("furl", furl, records)
			}
			for _, rec := range records {
				tiers = append(tiers, rec["data_tier_name"].(string))
			}
		}
	}
	return tiers
}

// helper function to get all datasets from DBS instance
func dbsDatasets(dbsinst string) []string {
	var datasets []string
	api := "datasets"
	for _, dbsinst := range dbsInstances() {
		furl := fmt.Sprintf("%s/%s", dbsUrl(dbsinst), api)
		response := utils.FetchResponse(furl, "")
		if response.Error == nil {
			records := loadDBSData(furl, response.Data)
			if utils.VERBOSE > 1 {
				fmt.Println("furl", furl, records)
			}
			for _, rec := range records {
				datasets = append(datasets, rec["dataset"].(string))
			}
		}
	}
	return datasets
}
func allDatasets() Record {
	rdict := make(Record)
	for _, dbsinst := range dbsInstances() {
		rdict[dbsinst] = dbsDatasets(dbsinst)
	}
	return rdict
}

// helper function to get DBS datasets for given time interval
func datasetsInTimeWindow(start, stop string) []string {
	var out []string
	api := "datasets"
	mint := utils.UnixTime(start)
	maxt := utils.UnixTime(stop)
	for _, dbsinst := range dbsInstances() {
		furl := fmt.Sprintf("%s/%s/?min_cdate=%d&max_cdate=%d&dataset_access_type=VALID", dbsUrl(dbsinst), api, mint, maxt)
		response := utils.FetchResponse(furl, "")
		if response.Error == nil {
			records := loadDBSData(furl, response.Data)
			for _, rec := range records {
				dataset := rec["dataset"].(string)
				out = append(out, dataset)
			}
		}
	}
	return out
}

// helper function to get release information about dataset
func datasetReleases(dataset string, ch chan Record) {
	api := "releaseversions"
	records, _ := dbsInfo(dataset, api, "")
	series := make(map[string]int)
	majors := make(map[string]int)
	minors := make(map[string]int)
	var totFull, totPatch, totPre int
	for _, drec := range records {
		val := drec["release_version"]
		if val == nil {
			continue
		}
		for _, ver := range val.([]interface{}) {
			rel := ver.(string)
			arr := strings.Split(rel, "_") // CMSSW_X_Y_Z_...
			if len(arr) >= 4 {
				series[arr[1]] = 1 // series number X
				majors[arr[2]] = 1 // majors number Y
				minors[arr[3]] = 1 // minors number Z
				//                 utils.IncDictValue(&series, arr[1]) // series number X
				//                 utils.IncDictValue(&majors, arr[2]) // majors number Y
				//                 utils.IncDictValue(&minors, arr[3]) // minors number Z
			}
			full, patch, pre := relType(rel)
			totFull += full
			totPatch += patch
			totPre += pre
		}
	}
	rec := make(Record)
	for k, v := range series {
		rec[fmt.Sprintf("rel1_%s", k)] = v
	}
	for k, v := range majors {
		rec[fmt.Sprintf("rel2_%s", k)] = v
	}
	for k, v := range minors {
		rec[fmt.Sprintf("rel3_%s", k)] = v
	}
	rec[fmt.Sprintf("relt_0")] = totFull
	rec[fmt.Sprintf("relt_1")] = totPatch
	rec[fmt.Sprintf("relt_2")] = totPre
	rec["nrel"] = len(records)
	ch <- rec
}

// helper function to determine release type
func relType(rel string) (int, int, int) {
	full := 1
	var patch, pre int
	match, err := regexp.MatchString("_patch", rel)
	if err != nil {
		return 0, 0, 0
	}
	if match {
		patch = 1
		full = 0
	}
	match, err = regexp.MatchString("_pre", rel)
	if match {
		pre = 1
		full = 0
	}
	return full, patch, pre
}

// helper function to get release information about dataset
func datasetSummary(dataset string, ch chan Record) {
	api := "filesummaries"
	records, dbsinst := dbsInfo(dataset, api, "")
	dbsId := 0
	for idx, dbs := range dbsInstances() {
		if dbs == dbsinst {
			dbsId = idx
			break
		}
	}
	size_norm := math.Pow(2, 30) // normalization factor for file size
	for _, rec := range records {
		if rec != nil {
			rec["dataset"] = utils.Hash2(dbsinst, dataset)
			primds, procds, tier := datasetParts(dataset)
			rec["primds"] = primds
			rec["procds"] = procds
			rec["tier"] = tier
			rec["dbsinst"] = dbsId
			rec["file_size"] = rec["file_size"].(float64) / size_norm
			ch <- rec
			return
		}
	}
	rec := make(Record)
	ch <- rec // we must send at least empty record
}

// helper function to get release information about dataset
func datasetParent(dataset string, ch chan Record) {
	api := "datasetparents"
	records, _ := dbsInfo(dataset, api, "")
	for _, rec := range records {
		if rec != nil {
			//             dataset := rec["parent_dataset"].(string)
			//             rec["parent"] = utils.Hash2(dbsinst, dataset)
			ch <- rec
			return
		}
	}
	rec := make(Record)
	ch <- rec // we must send at least empty record
}

// helper function to get release information about dataset
func datasetDetails(dataset string, ch chan Record) {
	api := "datasets"
	records, _ := dbsInfo(dataset, api, "True")
	for _, rec := range records {
		if rec != nil {
			rec["acquisition_era_name"] = utils.GetValue(rec["acquisition_era_name"])
			rec["create_by"] = utils.GetValue(rec["create_by"])
			rec["physics_group_name"] = utils.GetValue(rec["physics_group_name"])
			rec["primary_ds_type"] = utils.GetValue(rec["primary_ds_type"])
			rec["prep_id"] = utils.GetValue(rec["prep_id"])
			rec["processing_version"] = utils.GetFloatValue(rec["processing_version"])
			rec["xtcrosssection"] = utils.GetFloatValue(rec["xtcrosssection"])
			ch <- rec
			return
		}
	}
	rec := make(Record)
	ch <- rec // we must send at least empty record
}

// helper function to get release information about dataset
func dbsInfo(dataset, api, details string) ([]Record, string) {
	var out []Record
	dbsinst := findDBSInstance(dataset)
	if dbsinst == "" {
		return out, ""
	}
	furl := fmt.Sprintf("%s/%s/?dataset=%s", dbsUrl(dbsinst), api, dataset)
	if len(details) > 0 {
		furl += "&detail=True"
	}
	response := utils.FetchResponse(furl, "")
	if response.Error == nil {
		records := loadDBSData(furl, response.Data)
		if utils.VERBOSE > 1 {
			fmt.Println("furl", furl, records)
		}
		if len(records) != 0 { // we got records from specific dbs instance
			return records, dbsinst
		}
	} else {
		if utils.VERBOSE > 1 {
			fmt.Println("DBS error with", furl, response)
		}
	}
	return out, ""
}

// find DBS instance which knows about given dataset
func findDBSInstance(dataset string) string {
	for _, dbsinst := range dbsInstances() {
		furl := fmt.Sprintf("%s/datasets/?dataset=%s", dbsUrl(dbsinst), dataset)
		response := utils.FetchResponse(furl, "")
		if response.Error == nil {
			records := loadDBSData(furl, response.Data)
			if utils.VERBOSE > 1 {
				fmt.Println("furl", furl, records)
			}
			if len(records) != 0 { // we got records from specific dbs instance
				return dbsinst
			}
		} else {
			if utils.VERBOSE > 1 {
				fmt.Println("DBS error with", furl, response)
			}
		}
	}
	return ""
}
