#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"

import BaseHTTPServer
import SimpleHTTPServer
import cgi

import multiprocessing
import sys

import datetime

class Server(SimpleHTTPServer.SimpleHTTPRequestHandler):

    # we override log_message() to show which process is handling the request
    def log_message(self, format, *args):
        now = datetime.datetime.now()
        sys.stderr.write('%s.%04d\t%s\t%s\n' % (now.strftime("%Y/%m/%d %H:%M:%S"), now.microsecond//1000, multiprocessing.current_process().name, format%args))

    def do_GET(self):
        path = self.path.split('/')
        if len(path) >= 2:
            path = path[1].split("?")[0]
        else:
            path = None

        if path in self.server.funcs:
            i=self.path.rfind('?')
            if i>=0:
                path, query=self.path[:i], self.path[i+1:]
            else:
                path=self.path
                query=''
            self.handle_query(path, query)
        else:
            SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
            return


    def do_POST(self):
        length=self.headers.getheader('content-length')
        try:
            nbytes=int(length)
        except (TypeError, ValueError):
            nbytes=0
        data=self.rfile.read(nbytes)
        self.handle_query(self.path, data)


    def handle_query(self, path, query):
        args=[]
        path=path[1:]
        if path.find('/') != -1:
            args=path.split('/')[1:]
            path=path.split('/')[0]
        qdict=cgi.parse_qs(query, keep_blank_values=True)
        for k in qdict.keys():
            if isinstance(qdict[k], list) and len(qdict[k]):
                qdict[k]=unicode(qdict[k][0], 'utf-8', 'ignore')
            else:
                qdict[k]=unicode(qdict[k], 'utf-8', 'ignore')
        if path in self.server.funcs:
            qdict.update({'_request':self})
            resp = self.server.funcs[path](self, *args, **qdict)
            self.send_response(resp.status, resp.status_message)
            self.wfile.write(str(resp))
        else:
            self.send_error(404, "No such handler function (%r)" % path)

