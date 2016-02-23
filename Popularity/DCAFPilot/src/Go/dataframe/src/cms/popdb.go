/*
 *
 * Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
 * Description: part of cms package responsible for popDB calls
 * Created    : Wed Feb 10 19:31:44 EST 2016
 */
package cms

import (
	"encoding/json"
	"fmt"
	"strconv"
	"utils"
)

// helper function to load PopDB data stream
func loadPopDBData(furl string, data []byte) []Record {
	var out []Record
	var rec Record
	err := json.Unmarshal(data, &rec)
	if err != nil {
		msg := fmt.Sprintf("PopDB unable to unmarshal the data, furl=%s, data=%s, error=%v", furl, string(data), err)
		fmt.Println(msg)
		return out
	}
	values := rec["DATA"].([]interface{})
	for _, item := range values {
		rec := item.(map[string]interface{})
		dataset := rec["COLLNAME"].(string)
		row := make(Record)
		if datasetNameOk(dataset) {
			row["dataset"] = dataset
			row["naccess"] = rec["NACC"].(float64)
			row["totcpu"] = rec["TOTCPU"].(float64)
			row["nusers"] = rec["NUSERS"].(float64)
			row["rnaccess"], _ = strconv.ParseFloat(rec["RNACC"].(string), 10)
			row["rtotcpu"], _ = rec["RTOTCPU"].(float64)
			row["rnusers"], _ = strconv.ParseFloat(rec["RNUSERS"].(string), 10)
			out = append(out, row)
		}
	}
	return out
}

// convert YYYYDDMM into popdb notation
func popDBtstamp(ts string) string {
	return fmt.Sprintf("%s-%s-%s", ts[0:4], ts[4:6], ts[6:8])
}

// helper function to collect dataset usage from popularity DB
func datasetStats(start, stop string) []Record {
	var out []Record
	api := "DSStatInTimeWindow"
	tstart := popDBtstamp(start)
	tstop := popDBtstamp(stop)
	furl := fmt.Sprintf("%s/%s/?tstart=%s&tstop=%s", popdbUrl(), api, tstart, tstop)
	if utils.VERBOSE > 1 {
		fmt.Println("furl", furl)
	}
	response := utils.FetchResponse(furl, "")
	if response.Error == nil {
		records := loadPopDBData(furl, response.Data)
		return records
	}
	return out
}
