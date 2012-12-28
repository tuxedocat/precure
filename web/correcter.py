#!/usr/bin/env python
# coding: utf-8


import urllib
import json

import BaseHTTPServer

import responce

import sys
import os
import aspell
# Prerequisite: Install aspell-python from http://wm.ite.pl/proj/aspell-python/index-c.html


class Server(BaseHTTPServer.HTTPServer):

    def __init__(self, opts, *args, **qdict):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **qdict)

        import nltk

        _SENTENCE_TOKENIZE_MODEL = "tokenizers/punkt/english.pickle"
        self.tokenizer = nltk.data.load(_SENTENCE_TOKENIZE_MODEL) 

        self.speller = aspell.Speller('lang', 'en')

        self.funcs = {'split':self.split, 'spell':self.spell}

    def __common(self, query, callback, mymethod):
        res = responce.Response()
        if (query):
            res.headers = {"Content-Type" : "text/javascript"}
            out = {}
            if query and len(query)>0:
                out = mymethod(query)
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

    def __split(self, text):
        assert isinstance(text, unicode)
        spans = self.tokenizer.span_tokenize(text)
        return {u"spans" : spans}

    def split(self, server, *args, **qdict):
        query = qdict.get('text', None)
        callback = qdict.get('callback', None)
        return self.__common(query, callback, self.__split)



    def __spell(self, text):
        assert isinstance(text, unicode)

        out = []
        from nltk.tokenize import WhitespaceTokenizer
        for (beg, end) in WhitespaceTokenizer().span_tokenize(text):
            word = text[beg:end]
            if word.isalpha():
                if self.speller.check(word):
                    pass
                else:
                    description = """Spell error:<br />
                        Candidates : %s""" % self.speller.suggest(word)
#                    description = """<strong hptip="%s">%s</span>""" % (description, word) #XXX
                    description = """<strong>%s</span>""" % (word) #XXX
                    out.append({"begin":beg, "end": end, "type":"spell", "description" : description})
            else:
                pass
        return {u"errors" : out}

    def spell(self, server, *args, **qdict):
        query = qdict.get('sent', None)
        callback = qdict.get('callback', None)
        return self.__common(query, callback, self.__spell)




