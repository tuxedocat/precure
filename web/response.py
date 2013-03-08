#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"

class Response(object):
    def __init__(self, charset='utf-8'):
        self.headers={'Content-type':'text/html;charset=%s' % charset}
        self.body=""
        self.status=200
        self.status_message=''

    def set_header(self, name, value):
        self.headers[name]=value

    def get_header(self, name):
        return self.headers.get(name, None)

    def set_body(self, bodystr):
        self.body=bodystr

    def set_error_body(self):
        self.body = u"""
    <html>
      <head>
        <title>ERROR %d</title>
        <meta http-equiv="content-type" content="text/html;charset=utf-8" />
      </head>
      <body>
      ERROR %d<br />
      %s
      </body>
    </html>""" % (self.status, self.status, self.status_message)

    def __str__(self):
        headers='\n'.join(["%s: %s" % (k, v) for k,v in self.headers.items()])
        ret = headers + '\n\n' + self.body
        return ret.encode('utf-8')

