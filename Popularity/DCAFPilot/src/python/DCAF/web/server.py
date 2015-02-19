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

class Root:
    """DCAFPilot static web server root class"""
    def __init__(self, idir):
        self.idir = idir

    @cherrypy.expose
    def index(self):
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
