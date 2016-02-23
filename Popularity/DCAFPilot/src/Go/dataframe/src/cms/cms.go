/*
 *
 * Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
 * Description: cms package which provides set of utilities to get statistics
 *				about CMS tier sites
 * Created    : Wed Feb 10 19:31:44 EST 2016
 */
package cms

import (
	"fmt"
	"math/rand"
	"os"
	"time"
	"utils"
)

// function to generate datamap
func GenerateMap(datamap, fout string) {
	startTime := time.Now()
	if fout == "" {
		fout = fmt.Sprintf("%s.txt", datamap)
	}
	utils.TestEnv()
	var names []string
	var records []Record
	for dbsinst, dbsId := range dbsInstances() {
		if datamap == "dataset" || datamap == "datasets" {
			names = dbsDatasets(dbsinst)
		} else if datamap == "tier" || datamap == "tiers" {
			names = dbsTiers(dbsinst)
		} else {
			fmt.Printf("Unsupported map name '%s'\n", datamap)
			os.Exit(-1)
		}
		for _, n := range names {
			rec := make(Record)
			rec[datamap] = n
			rec["dbsinst"] = dbsId
			rec["hash"] = utils.Hash1(n)
			records = append(records, rec)
		}
	}
	// process extra dataset
	writeRecords(records, fout)
	if utils.PROFILE {
		fmt.Printf("Processed %d urls\n", utils.UrlCounter)
		fmt.Printf("Elapsed time %s\n", time.Since(startTime))
	}
	if utils.VERBOSE > 0 {
		fmt.Println("Job finished", time.Now())
	}
}

// function which process user request
func Process(start, stop, fout string, newdata bool, dbsExtra, chunkSize int, test bool) {
	startTime := time.Now()
	utils.TestEnv()
	if start == "" {
		start = utils.Today()
	}
	if stop == "" {
		stop = utils.Today()
	}
	if fout == "" {
		fout = fmt.Sprintf("dataframe-%s-%s.csv", start, stop)
	}
	if utils.VERBOSE > 0 {
		fmt.Println("Job started", time.Now())
		fmt.Println(fout)
	}
	var results, popdbRecords, missRecords []Record
	if test {
		for _, rec := range testRecords() {
			popdbRecords = append(popdbRecords, rec)
		}
	} else {
		// get popularity DB records for given time interval
		popdbRecords = datasetStats(start, stop)
		if len(popdbRecords) == 0 {
			fmt.Println("No records from PopDB, better stop here")
			os.Exit(-1)
		}
		extraRecords := extraRecords(dbsDatasets("prod/global"), popdbRecords, dbsExtra)
		if utils.VERBOSE > 0 {
			fmt.Printf("Process %d popdb records\n", len(popdbRecords))
			fmt.Printf("Process %d extra records\n", len(extraRecords))
		}
		// combine all records togther
		for _, rec := range extraRecords {
			popdbRecords = append(popdbRecords, rec)
		}
	}
	// for every dataset in popdbRecords we need to collect its information
	for cdx, chunk := range makeChunksOfRecords(popdbRecords, chunkSize) {
		if utils.VERBOSE == 1 {
			fmt.Printf("process chunk=%d, %d records\n", cdx, len(chunk))
		}
		if utils.VERBOSE == 2 {
			fmt.Println("process chunk", chunk)
		}
		var counter int
		ch := make(chan Record)
		for _, prec := range chunk {
			if prec != nil {
				go datasetInfo(prec, start, stop, ch)
				counter += 1
			}
		}
		var out []Record
		var missCount int
		for { // collect results from a given chunk
			select {
			case r := <-ch:
				v := r["dataset"]
				if v == nil {
					missRecords = append(missRecords, r)
					missCount += 1
				} else {
					switch v.(type) {
					case string:
						missRecords = append(missRecords, r)
						missCount += 1
					default:
						out = append(out, r)
					}
				}
			default:
				time.Sleep(time.Duration(10) * time.Millisecond) // wait for response
			}
			if len(out)+missCount == len(chunk) {
				for _, rec := range out {
					results = append(results, rec)
				}
				break
			}
		}
		if utils.PROFILE {
			fmt.Printf("Processed %d chunk in %s\n", cdx, time.Since(startTime))
		}
	}
	// check if we miss some datasets and try to recover them
	if len(missRecords) > 0 {
		if utils.VERBOSE > 0 {
			fmt.Printf("Process missed dataset %d records\n", len(missRecords))
		}
		var missCount int
		for _, chunk := range makeChunksOfRecords(missRecords, 10) {
			ch := make(chan Record)
			for _, prec := range chunk {
				if prec != nil {
					go datasetInfo(prec, start, stop, ch)
				}
			}
			var out []Record
			missCount = 0
			for { // collect results from a given chunk
				select {
				case r := <-ch:
					v := r["dataset"]
					switch v.(type) {
					case uint64:
						if v.(uint64) == 0 {
							fmt.Println("Miss record", r)
							missCount += 1
						} else {
							out = append(out, r)
						}
					default:
						fmt.Println("Miss record", r)
						missCount += 1
					}
				default:
					time.Sleep(time.Duration(10) * time.Millisecond) // wait for response
				}
				if len(out)+missCount == len(chunk) {
					for _, rec := range out {
						results = append(results, rec)
					}
					break
				}
			}
		}
		if missCount > 0 {
			fmt.Printf("Number of missed records: %d\n", missCount)
		}
	}

	// process extra dataset
	writeRecords(results, fout)
	if utils.PROFILE {
		fmt.Printf("Processed %d urls\n", utils.UrlCounter)
		fmt.Printf("Elapsed time %s\n", time.Since(startTime))
	}
	if utils.VERBOSE > 0 {
		fmt.Println("Job finished", time.Now())
	}
}

// get random set of datasets from provided DBS set
// but exclude popularity datasets
func extraRecords(datasets []string, pRecords []Record, dbsExtra int) []Record {
	rand.Seed(12345)
	pdict := make(Record)
	for _, r := range pRecords {
		d := r["dataset"].(string)
		pdict[d] = struct{}{}
	}
	var records []Record
	for {
		if len(records) == dbsExtra {
			break
		}
		d := datasets[rand.Intn(len(datasets))]
		if _, ok := pdict[d]; !ok {
			prec := Record{"naccess": 0, "totcpu": 0, "nusers": 0, "rnaccess": 0, "rtotcpu": 0, "rnusers": 0, "dataset": d}
			records = append(records, prec)
		}
	}
	return records
}

// get dataset information from various CMS data-services
func datasetInfo(prec Record, start, stop string, och chan Record) {
	dataset := prec["dataset"].(string)
	ch := make(chan Record)
	counter := 0 // count how may go routines we send
	// DBS calls
	go datasetReleases(dataset, ch)
	counter += 1
	go datasetSummary(dataset, ch)
	counter += 1
	go datasetParent(dataset, ch)
	counter += 1
	go datasetDetails(dataset, ch)
	counter += 1
	// McM calls
	go mcmProduces(dataset, ch)
	counter += 1
	// Phedex calls
	//     go datasetSites(dataset, ch)
	//     counter += 1
	// collect results
	var records []Record
	for {
		select {
		case r := <-ch:
			records = append(records, r)
		default:
			time.Sleep(time.Duration(10) * time.Millisecond) // wait for response
		}
		if len(records) == counter {
			break
		}
	}
	rec := make(Record)
	for _, srec := range records { // loop over all received service records
		for k, v := range srec { // loop over service record key-value pairs
			switch v.(type) {
			case string:
				rec[k] = utils.Hash1(v.(string))
			default:
				rec[k] = v
			}
		}
	}
	// popdb metrics
	rec["naccess"] = prec["naccess"]
	rec["totcpu"] = prec["totcpu"]
	rec["nusers"] = prec["nusers"]
	rec["rnaccess"] = prec["rnaccess"]
	rec["rtotcpu"] = prec["rtotcpu"]
	rec["rnusers"] = prec["rnusers"]
	v := rec["dataset"]
	if v == nil || v.(uint64) == 0 {
		if utils.VERBOSE > 0 {
			fmt.Println("miss dataset", dataset, rec)
		}
		rec["dataset"] = dataset
	}
	if utils.VERBOSE > 1 {
		fmt.Println("rec", rec)
	}
	och <- rec
}
