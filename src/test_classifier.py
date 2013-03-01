#!/usr/bin/env python
# coding: utf-8

from nose.plugins.attrib import attr
from classifier_skl import * 
from feature_extractor import * 
from datetime import datetime
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.DEBUG)
import os
from pprint import pformat
from collections import defaultdict
import cPickle as pickle
import json


@attr("svm")
def trsvm_test():
    path = "test/tiny/"
    path_model = "test/models/"
    svm = train_model(path, path_model)
    raise Exception

@attr("svmtest")
def predsvm_test():
    # modelpath = "test/models"
    modelpath = "../model"
    path_test = "test/testcase/test.json"
    # path_test = "../corpora/0_low.json"
    # path_test = "../corpora/2_high.json"
    testc = json.load(open(path_test, "r"))
    features_t = [] 
    yt = []
    for doc in testc:
        fe = DocumentFeatures(doc)
        _f = fe.pipeline()
        clsf = SklearnClassifier()
        clsf.load_model(modelpath)
        clsf.load_fmap(modelpath)
        xt = clsf.fmap.transform(_f)
        print clsf.predict(xt)
        # clsf.show_readable_features(xt)
    raise Exception