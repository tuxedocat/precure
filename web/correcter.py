#!/usr/bin/env python
# coding: utf-8


import urllib
import json

import BaseHTTPServer

import responce


class Server(BaseHTTPServer.HTTPServer):

    def __init__(self, opts, *args, **qdict):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **qdict)

        import nltk

        _SENTENCE_TOKENIZE_MODEL = "tokenizers/punkt/english.pickle"
        self.tokenizer = nltk.data.load(_SENTENCE_TOKENIZE_MODEL) 

#        self.funcs = { 'parse' : self.parse, 'split':self.split}
        self.funcs = {'split':self.split}


    def __split(self, text):
        assert isinstance(text, unicode)
        spans = self.tokenizer.span_tokenize(text)
        return {u"spans" : spans}

    def split(self, server, *args, **qdict):
        res = responce.Response()

        query = qdict.get('text', None)
        callback = qdict.get('callback', None)
        if (query):
            res.headers = {"Content-Type" : "text/javascript"}
            out = {}
            if query and len(query)>0:
                out = self.__split(query)
            if callback:
                myret = "%s(%s)" % (callback, json.dumps(out))
            else:
                myret = "%s" % (json.dumps(out))
            res.set_body(myret)
        else:
            res.status = 503
            res.status_message='Invalid Query format'
            res.set_error_body()
        return res

