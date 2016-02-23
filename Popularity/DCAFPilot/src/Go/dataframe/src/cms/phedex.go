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
	"strings"
	"utils"
)

// helper function to load data stream and return DAS records
func loadPhedexData(furl string, data []byte) []Record {
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

// helper function to find all dataset at a given tier-site
func datasetSites(dataset string, ch chan Record) {
	api := "blockreplicas"
	furl := fmt.Sprintf("%s/%s?dataset=%s", phedexUrl(), api, dataset)
	if utils.VERBOSE > 1 {
		fmt.Println("furl", furl)
	}
	response := utils.FetchResponse(furl, "")
	sdict := make(Record)
	var se string
	if response.Error == nil {
		records := loadPhedexData(furl, response.Data)
		for _, rec := range records {
			if rec["phedex"] != nil {
				val := rec["phedex"].(map[string]interface{})
				blocks := val["block"].([]interface{})
				for _, item := range blocks {
					brec := item.(map[string]interface{})
					replicas := brec["replica"].([]interface{})
					for _, r := range replicas {
						rep := r.(map[string]interface{})
						site := rep["node"].(string)
						v := rep["se"]
						if v == nil {
							se = ""
						} else {
							se = v.(string)
						}
						sdict[site] = se
					}
				}
			}
		}
	}
	var s0, s1, s2, s3, su int
	for site, _ := range sdict {
		if strings.HasPrefix(site, "T0_") {
			s0 += 1
		} else if strings.HasPrefix(site, "T1_") {
			s1 += 1
		} else if strings.HasPrefix(site, "T2_") {
			s2 += 1
		} else if strings.HasPrefix(site, "T3_") {
			s3 += 1
		} else {
			su += 1
		}
	}
	ch <- Record{"s_0": s0, "s_1": s1, "s_2": s2, "s_3": s3, "s_u": su}
}
