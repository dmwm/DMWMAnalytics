/*
 *
 * Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
 * Description: part of cms package responsible for static URLs
 * Created    : Wed Feb 10 19:31:44 EST 2016
 */
package cms

import "fmt"

func dbsInstances() Record {
	return Record{"prod/global": 0, "prod/phys01": 1, "prod/phys02": 2, "prod/phys03": 3}
}
func dbsUrl(dbsinst string) string {
	return fmt.Sprintf("https://cmsweb.cern.ch/dbs/%s/DBSReader", dbsinst)
}
func phedexUrl() string {
	return "https://cmsweb.cern.ch/phedex/datasvc/json/prod"
}
func sitedbUrl() string {
	return "https://cmsweb.cern.ch/sitedb/data/prod"
}
func popdbUrl() string {
	return "https://cmsweb.cern.ch/popdb/popularity"
}
func victordbUrl() string {
	return "https://cmsweb.cern.ch/popdb/victorinterface"
}
func mcmUrl() string {
	return "https://cms-pdmv.cern.ch/mcm/public/restapi/requests"
}

// main record we work with
type Record map[string]interface{}
