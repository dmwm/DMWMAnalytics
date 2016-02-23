/*
 *
 * Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
 * Description: McM module
 * Created    : Mon Feb 22 11:08:35 EST 2016
 *
 */
package cms

import (
	"encoding/json"
	"fmt"
	"utils"
)

// helper function to load McM data stream
func loadMcMData(furl string, data []byte) []Record {
	var out []Record
	var rec Record
	err := json.Unmarshal(data, &rec)
	if err != nil {
		if utils.VERBOSE > 1 {
			msg := fmt.Sprintf("unable to unmarshal the data into record, furl=%s, data=%s, error=%v", furl, string(data), err)
			fmt.Println(msg)
		}
	}
	out = append(out, rec)
	return out
}

// Unmarshal McM data stream and return DAS records based on api
func mcmProduces(dataset string, ch chan Record) {
	api := "produces"
	furl := fmt.Sprintf("%s/%s/%s", mcmUrl(), api, dataset)
	if utils.VERBOSE > 1 {
		fmt.Println("furl", furl)
	}
	response := utils.FetchResponse(furl, "")
	if response.Error == nil {
		records := loadMcMData(furl, response.Data)
		for _, r := range records {
			if r == nil {
				continue
			}
			v := r["results"]
			if v == nil {
				continue
			}
			res := v.(map[string]interface{})
			rec := make(Record)
			rec["energy"] = utils.GetFloatValue(res["energy"])
			s := res["sequences"]
			if s != nil {
				rec["nseq"] = len(s.([]interface{}))
			} else {
				rec["nseq"] = 0
			}
			rec["flown_with"] = utils.GetValue(res["flown_with"])
			rec["mcmtype"] = utils.GetValue(res["type"])
			rec["pwg"] = utils.GetValue(res["pwg"])
			rec["idataset"] = utils.GetValue(res["input_dataset"])
			rec["pdataset"] = utils.GetValue(res["pileup_dataset_name"])
			rec["campain"] = utils.GetValue(res["member_of_campaign"])
			rec["mcmevts"] = utils.GetFloatValue(res["nevents"])
			rec["mcmpid"] = utils.GetValue(res["prepid"])
			ch <- rec
			return
		}
	}
	rec := make(Record)
	ch <- rec // we must send at least empty record
}
