/*
 *
 * Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
 * Description: utils module for sitestat package
 * Created    : Wed Feb 10 19:31:44 EST 2016
 */
package utils

import (
	"crypto/md5"
	"encoding/hex"
	"fmt"
	"os"
	"strconv"
	"time"
)

// global variable for this module which we're going to use across
// many modules
var VERBOSE int
var PROFILE bool

// test environment
func TestEnv() {
	uproxy := os.Getenv("X509_USER_PROXY")
	ucert := os.Getenv("X509_USER_CERT")
	if uproxy == "" && ucert == "" {
		fmt.Println("Neither X509_USER_PROXY or X509_USER_CERT is set")
		os.Exit(-1)
	}
	uckey := os.Getenv("X509_USER_KEY")
	if uckey == "" {
		fmt.Println("X509_USER_KEY is not set")
		os.Exit(-1)
	}
}

// helper function to check item in a list
func InList(a string, list []string) bool {
	check := 0
	for _, b := range list {
		if b == a {
			check += 1
		}
	}
	if check != 0 {
		return true
	}
	return false
}

// helper function to return keys from a map
func MapKeys(rec map[string]interface{}) []string {
	keys := make([]string, 0, len(rec))
	for k := range rec {
		keys = append(keys, k)
	}
	return keys
}

// helper function to return keys from a map
func MapIntKeys(rec map[int]interface{}) []int {
	keys := make([]int, 0, len(rec))
	for k := range rec {
		keys = append(keys, k)
	}
	return keys
}

// helper function to convert input list into set
func List2Set(arr []string) []string {
	var out []string
	for _, key := range arr {
		if !InList(key, out) {
			out = append(out, key)
		}
	}
	return out
}

// helper function to convert size into human readable form
func SizeFormat(val float64) string {
	base := 1000. // CMS convert is to use power of 10
	xlist := []string{"", "KB", "MB", "GB", "TB", "PB"}
	for _, vvv := range xlist {
		if val < base {
			return fmt.Sprintf("%3.1f%s", val, vvv)
		}
		val = val / base
	}
	return fmt.Sprintf("%3.1f%s", val, xlist[len(xlist)])
}

// helper function to perform sum operation over provided array of floats
func Sum(data []float64) float64 {
	out := 0.0
	for _, val := range data {
		out += val
	}
	return out
}

// implement sort for []string type
type StringList []string

func (s StringList) Len() int           { return len(s) }
func (s StringList) Swap(i, j int)      { s[i], s[j] = s[j], s[i] }
func (s StringList) Less(i, j int) bool { return s[i] < s[j] }

// helper function to extract value from tstamp string
func extractVal(ts string) int {
	val, _ := strconv.Atoi(ts[0 : len(ts)-1])
	return val
}

// helper function to convert given time into Unix timestamp
func UnixTime(ts string) int64 {
	// time is unix since epoch
	if len(ts) == 10 { // unix time
		tstamp, _ := strconv.ParseInt(ts, 10, 64)
		return tstamp
	}
	// YYYYMMDD, always use 2006 as year 01 for month and 02 for date since it is predefined int Go parser
	const layout = "20060102"
	t, err := time.Parse(layout, ts)
	if err != nil {
		panic(err)
	}
	return int64(t.Unix())
}

// helper function to get today's date
func Today() string {
	const layout = "20060102"
	t := time.Now()
	today := t.Format(layout)
	return today
}

// helper function to make chunks from provided list
func MakeChunks(arr []string, size int) [][]string {
	var out [][]string
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

// helper function to convert given string into a hash
func Hash1(rec string) uint64 {
	data := []byte(rec)
	arr := md5.Sum(data)
	hexVal := hex.EncodeToString(arr[:])
	return hexdec(hexVal)
}

// helper function to convert given strings into a hash
func Hash2(rec1, rec2 string) uint64 {
	return Hash1(rec1 + rec2)
}

// convert hex string to decimal representation
// http://stackoverflow.com/questions/27198396/golang-decimal-to-hex-conversion-error
func hexdec(s string) uint64 {
	d := uint64(0)
	for i := 0; i < len(s); i++ {
		x := uint64(s[i])
		if x >= 'a' {
			x -= 'a' - 'A'
		}
		d1 := x - '0'
		if d1 > 9 {
			d1 = 10 + d1 - ('A' - '0')
		}
		if 0 > d1 || d1 > 15 {
			panic("hexdec")
		}
		d = (16 * d) + d1
	}
	return d
}

// helper function to increment dict value
func IncDictValue(r *map[string]int, key string) {
	if _, ok := (*r)[key]; ok {
		(*r)[key] += 1
	} else {
		(*r)[key] = 1 // we start with one to mark that key is present in dict
	}
}

// helper function to get value from interface
func GetValue(rec interface{}) uint64 {
	if rec == nil {
		return 0
	}
	return Hash1(rec.(string))
}

// helper function to get value from interface
func GetFloatValue(rec interface{}) float64 {
	if rec == nil {
		return 0
	}
	return rec.(float64)
}
