#!/usr/bin/env python
#coding:utf-8
__author__ = "Yu SAWAI"
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"
__descripstion__ = ""
__usage__ = ""

from nose.plugins.attrib import attr
from datetime import datetime
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.DEBUG)
import os
from pprint import pformat
from collections import defaultdict
import cPickle as pickle
from sklearn.feature_extraction import DictVectorizer
import json
from feature_extractor import SentenceFeatures, DocumentFeatures

class TestFext(object):
    def setUp(self):
        self.testpath = "test/sennatags.txt"
        self.testpath_off = "test/sennatags_off.txt"
        self.jsonpath = "../corpora/low.json"

    @attr("json")
    def test_json(self):
        self.json = json.load(open(self.jsonpath, "r"))
        fv = []
        for d in self.json[0:5]:
            fe = DocumentFeatures(d, parse=True)
            fe.pipeline()
            logging.debug(pformat(fe.features))
            fv.append(fe.features)
        # vec = DictVectorizer(sparse=True)
        # array_f = vec.fit_transform(fv).toarray()
        # logging.debug(pformat(array_f))
        raise Exception

    @attr("without_offset")
    def test_wo_offset(self):
        self.testdata = [doc.split("\n") for doc in open(self.testpath).read().split("\n\n") if doc]
        fv = []
        # print pformat(self.testdata)
        for t in self.testdata:
            fe = SentenceFeatures(t)
            fe.length()
            fe.bow()
            logging.debug(pformat(zip(fe.SUF, fe.POS)))
            logging.debug(pformat(fe.NER))
            logging.debug(pformat(fe.features))
            fv.append(fe.features)
        vec = DictVectorizer(sparse=True)
        array_f = vec.fit_transform(fv).toarray()
        logging.debug(pformat(array_f))
        raise Exception

    @attr("with_offset")
    def test_with_offset(self):
        self.testdata = [doc.split("\n") for doc in open(self.testpath_off).read().split("\n\n") if doc]
        fv = []
        # print pformat(self.testdata)
        for t in self.testdata:
            fe = SentenceFeatures(t)
            fe.length()
            fe.bow()
            logging.debug(pformat(zip(fe.SUF, fe.POS)))
            logging.debug(pformat(fe.OFFSET))
            logging.debug(pformat(fe.features))
            fv.append(fe.features)
        vec = DictVectorizer(sparse=True)
        array_f = vec.fit_transform(fv).toarray()
        logging.debug(pformat(array_f))
        raise Exception