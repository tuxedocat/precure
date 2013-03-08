#!/usr/bin/env python
# coding: utf-8

"""
renamed (yu-s)
"""

import urllib
import json

import BaseHTTPServer

import response

import sys
import os
import aspell
# Prerequisite: Install aspell-python from http://wm.ite.pl/proj/aspell-python/index-c.html
import random
import src.tools.senna
from src.feature_extractor import DocumentFeatures, SentenceFeatures
from src.classifier_skl import SklearnClassifier


class Server(BaseHTTPServer.HTTPServer):

    def __init__(self, opts, *args, **qdict):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **qdict)
        import nltk
        _SENTENCE_TOKENIZE_MODEL = "tokenizers/punkt/english.pickle"
        self.tokenizer = nltk.data.load(_SENTENCE_TOKENIZE_MODEL) 
        self.speller = aspell.Speller('lang', 'en')
        try:
            sennabin = unicode(os.environ['SENNAPATH'])
        except KeyError:
            sennabin = u"/data/tool/senna/"
        self.senna = src.tools.senna.SennaWrap(sennabin)
        self.funcs = {'split':self.split, 'spell':self.spell, 'pas': self.pas, "score" : self.score}
        M_PATH = opts.model_dir
        self.model = SklearnClassifier()
        self.model.load_model(M_PATH)
        self.model.load_fmap(M_PATH)

    def __common(self, query, callback, mymethod):
        res = response.Response()
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

    def __score(self, texts):
        texts = texts.split("///")
        from nltk.tokenize import word_tokenize
        tokens = []
        for s in texts:
            tk = word_tokenize(s)
            tokens.append(tk)
        fe = DocumentFeatures(tokens, parse=True)
        _f = fe.pipeline()
        features = self.model.transform(_f)
        score = self.model.predict(features) 
        # return {"score" : round(random.random() * 100, 1)} #FIXME
        return {"score" : int(score * 100)}

    def __spell(self, text):
        assert isinstance(text, unicode)
        out = []
        from nltk.tokenize import WhitespaceTokenizer
        for (beg, end) in WhitespaceTokenizer().span_tokenize(text):
            word = text[beg:end]
            word = word.encode("utf8") #XXX
            if word.isalpha():
                if self.speller.check(word):
                    pass
                else:
                    candidates = self.speller.suggest(word)
                    out.append({"begin":beg, "end": end, "type":"spell", "candidates" : candidates})
            else:
                pass
        return {u"errors" : out}

    def __pas(self, text):
        assert isinstance(text, unicode)

        out = []
#        text = text.encode("utf8") #XXX
        text = text.rstrip().lstrip()
        if len(text) == 0:
            return out

        result = self.senna.getPredicates(text)
#        [[1, 'love', {'S-V': 'love', 'S-A0': 'I'}], [3, 'kill', {'S-V': 'kill', 'S-A1': 'you.', 'S-A0': 'I'}]]
        for item in result:
            out.append(item[2])
        return str(out) #FIXME


    def spell(self, server, *args, **qdict):
        query = qdict.get('sent', None)
        callback = qdict.get('callback', None)
        return self.__common(query, callback, self.__spell)

    def pas(self, server, *args, **qdict):
        query = qdict.get('sent', None)
        callback = qdict.get('callback', None)
        return self.__common(query, callback, self.__pas)

    def score(self, server, *args, **qdict):
        query = qdict.get('sents', None)
        callback = qdict.get('callback', None)
        return self.__common(query, callback, self.__score)





