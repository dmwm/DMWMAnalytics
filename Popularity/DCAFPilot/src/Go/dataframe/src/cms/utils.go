/*
 *
 * Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
 * Description: utils for cms package
 * Created    : Wed Feb 10 19:31:44 EST 2016
 */
package cms

import (
	"bufio"
	"fmt"
	"os"
	"sort"
	"strings"
	"utils"
)

func datasetNameOk(dataset string) bool {
	pieces := strings.Split(dataset, "/")
	if len(pieces) == 4 { // /a/b/c -> ["", a, b, c]
		return true
	}
	return false
}

// helper function to write records to a given file name
func writeRecords(records []Record, fout string) {
	if utils.VERBOSE > 0 {
		fmt.Printf("Format %d records\n", len(records))
	}
	headers := make(Record)
	for _, rec := range records {
		for _, h := range utils.MapKeys(rec) {
			headers[h] = 0
		}
	}
	// open output file
	fo, err := os.Create(fout)
	if err != nil {
		panic(err)
	}
	// close fo on exit and check for its returned error
	defer func() {
		if err := fo.Close(); err != nil {
			panic(err)
		}
	}()
	// make a write buffer
	w := bufio.NewWriter(fo)
	// convert headers to string
	sheaders := utils.MapKeys(headers)
	sort.Sort(utils.StringList(sheaders))
	hout := ""
	for _, h := range sheaders {
		if len(hout) == 0 {
			hout = h
		} else {
			hout += fmt.Sprintf(",%s", h)
		}
	}
	// write headers
	if _, err := w.Write([]byte(hout + "\n")); err != nil {
		panic(err)
	}
	// loop over record values
	for _, record := range records {
		out := ""
		for _, k := range sheaders {
			if v, ok := record[k]; ok {
				vv := fmt.Sprintf("%v", v)
				switch v.(type) {
				case float64:
					vv = fmt.Sprintf("%f", v)
				}
				if len(out) == 0 {
					out = vv
				} else {
					out += fmt.Sprintf(",%s", vv)
				}
			} else {
				if len(out) == 0 {
					out = "0"
				} else {
					out += ",0"
				}

			}
		}
		// replace possible nil's with -1
		out = strings.Replace(out, "<nil>", "-1", -1)
		if _, err := w.Write([]byte(out + "\n")); err != nil {
			panic(err)
		}
	}
	if err = w.Flush(); err != nil {
		panic(err)
	}
}

// helper function to get data tier from dataset/block name
func dataTier(name string) string {
	dataset := strings.Split(name, "#")[0]
	dparts := strings.Split(dataset, "/")
	return dparts[len(dparts)-1]
}

// helper function to get data tier from dataset/block name
func datasetParts(dataset string) (uint64, uint64, uint64) {
	dparts := strings.Split(dataset, "/")
	return utils.Hash1(dparts[1]), utils.Hash1(dparts[2]), utils.Hash1(dparts[3])
}

// helper function to make chunks from record list
func makeChunksOfRecords(arr []Record, size int) [][]Record {
	var out [][]Record
	alen := len(arr)
	abeg := 0
	aend := size
	for {
		if aend < alen {
			out = append(out, arr[abeg:aend])
			abeg = aend
			aend += size
		} else {
			break
		}
	}
	if abeg < alen {
		out = append(out, arr[abeg:alen-1])
	}
	return out
}

// helper function to test Records
func testRecords() []Record {
	var records []Record
	var datasets []string
	datasets = append(datasets, "/SLQ_Lhanded-MLQ2800g1l1_13TeV-calchep/RunIIWinter15pLHE-MCRUN2_71_V1-v1/LHE")
	datasets = append(datasets, "/SeesawTypeIII_SIGMAplusSIGMA0HH_M-500_13TeV-madgraph/RunIISummer15GS-MCRUN2_71_V1-v1/GEN-SIM")
	datasets = append(datasets, "/QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8/dquach-ntuplev6p1_76x_errdxy40um-ccdf5da9331e9d81b86d4afa8a0c7533/USER")
	// dataset which has mcm
	datasets = append(datasets, "/WToENu_Tune4C_13TeV-pythia8/Fall13dr-tsg_PU40bx25_POSTLS162_V2-v1/GEN-SIM-RAW")
	for _, d := range datasets {
		prec := Record{"naccess": 0, "totcpu": 0, "nusers": 0, "rnaccess": 0, "rtotcpu": 0, "rnusers": 0, "dataset": d}
		records = append(records, prec)
	}
	return records
}

// helper function to get new DBS Records
func newRecords(start, stop string) []Record {
	var records []Record
	datasets := datasetsInTimeWindow(start, stop)
	for _, d := range datasets {
		prec := Record{"naccess": 0, "totcpu": 0, "nusers": 0, "rnaccess": 0, "rtotcpu": 0, "rnusers": 0, "dataset": d}
		records = append(records, prec)
	}
	return records
}
