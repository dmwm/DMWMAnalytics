// A package to collect meta-data information from various CMS data services
// and present it in CSV format for Machine Learning studies
package main

import (
	"cms"
	"flag"
	"utils"
)

func main() {
	var start string
	flag.StringVar(&start, "start", "", "Start timestamp in YYYYMMDD format")
	var stop string
	flag.StringVar(&stop, "stop", "", "Stop timestamp in YYYYMMDD format")
	var fout string
	flag.StringVar(&fout, "fout", "", "Name of output file")
	var newdata bool
	flag.BoolVar(&newdata, "newdata", false, "Get new data from DBS instead of popularity DB")
	var datamap string
	flag.StringVar(&datamap, "datamap", "", "Generate datamap file for given attribute, e.g. dataset, tier")
	var dbsExtra int
	flag.IntVar(&dbsExtra, "dbsExtra", 1000, "Extra number of DBS datasets not listed in popularity DB")
	var chunkSize int
	flag.IntVar(&chunkSize, "chunkSize", 100, "Chunk size for processing URLs")
	var verbose int
	flag.IntVar(&verbose, "verbose", 0, "Verbose level, support 0,1,2")
	var profile bool
	flag.BoolVar(&profile, "profile", false, "profile code")
	var test bool
	flag.BoolVar(&test, "test", false, "test mode")
	flag.Parse()
	utils.VERBOSE = verbose
	utils.PROFILE = profile
	if datamap == "dataset" || datamap == "tier" || datamap == "datasets" || datamap == "tiers" {
		cms.GenerateMap(datamap, fout)
	} else {
		cms.Process(start, stop, fout, newdata, dbsExtra, chunkSize, test)
	}
}
