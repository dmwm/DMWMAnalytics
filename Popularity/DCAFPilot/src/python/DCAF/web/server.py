#!/usr/bin/env python
"""
DCAFPilot static web server
"""

# system modules
import os
import sys
import stat
import time
import cherrypy
from optparse import OptionParser
from json import JSONEncoder

def popular_datasets(fname):
    "Return content of given file and return list of popular datasets"
    with open(fname, 'r') as istream:
        line = istream.readline().replace('\n', '')
        if  line:
            prob, dataset = line.split(',')
            prob = float(prob)
            if prob > 0.5:
                yield dataset

def exposejson (func):
    """CherryPy expose JSON decorator"""
    @cherrypy.expose
    def wrapper (self, *args, **kwds):
        """Decorator wrapper"""
        encoder = JSONEncoder()
        data = func (self, *args, **kwds)
        cherrypy.response.headers['Content-Type'] = "text/json"
        try:
            jsondata = encoder.encode(data)
            return jsondata
        except:
            Exception("Fail to JSONtify obj '%s' type '%s'" \
                % (data, type(data)))
    return wrapper

class Root:
    """DCAFPilot static web server root class"""
    def __init__(self, idir):
        self.idir = idir

    def pop_datasets(self):
        "Retrieve popular datasets for different algorithms"
        pdict = {}
        for fname in os.listdir(self.idir):
            if  fname.endswith('predicted'):
                alg = fname.split('.')[0]
                pdict[alg] = list(popular_datasets(os.path.join(self.idir, fname)))
        return pdict

    @exposejson
    def popular_datasets(self):
        "Return JSON stream with popular datasets"
        return self.pop_datasets()

    @cherrypy.expose
    def index(self):
        "Main method"
        pdict = self.pop_datasets()
        out = ""
        for alg, datasets in pdict.items():
            out += "<h3>%s</h3>\n" % alg
            for dataset in datasets:
                out += dataset+"<br/>\n"
        return out

    @cherrypy.expose
    def predictions(self):
        "Main method"
        files = ''
        for fname in os.listdir(self.idir):
            ctime = os.stat(os.path.join(self.idir, fname)).st_ctime
            ctime = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(ctime))
            files += '<a href="data/%s">%s</a> created on %s<br/>' % (fname, fname, ctime)
        form = """<html><head><title>DCAFPilot data</title></head><html>
                <body><h2>DCAF predictions</h2>
                %s
                </body></html>""" % files
        return form

def server(port):
    "DCAFPilot static web server"
    cherrypy.config.update({'environment': 'production',
                            'log.screen': True,
                            'server.socket_port': port})
    current_dir = os.path.dirname(os.path.abspath(__file__))
    idir = os.environ.get('DCAF_PREDICTIONS', os.path.join(current_dir, 'data/predictions'))
    conf = {'/data': {'tools.staticdir.on': True,
                      'tools.staticdir.dir': idir,
                      'tools.staticdir.content_types': {'data': 'multipart/form-data'}}}
    cherrypy.quickstart(Root(idir), '/', config=conf)

def main():
    "Main function to run DCAFPilot server"
    parser  = OptionParser()
    parser.add_option("--port", dest="port", default=8888, type="int", help="port number")
    opts, _ = parser.parse_args()
    server(opts.port)

if __name__ == '__main__':
    main()
