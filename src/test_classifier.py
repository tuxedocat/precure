#! /usr/bin/env python
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


@attr("svm")
def trsvm_test():
    path_parsed1 = "test/sennatags.txt"
    path_parsed2 = "test/sennatags_off.txt"
    path_model = "test/svm_model"
    svm = mkmodel(path_parsed1, path_parsed2, path_model)
    raise Exception

@attr("svmtest")
def predsvm_test():
    modelpath = "../model/model_KJUK"
    path_parsed = "test/sennatags_off.txt"
    testc = [s.split("\n") for s in open(path_parsed).read().split("\n\n") if s]
    features_t = [] 
    yt = []
    for sent in testc:
        fe = SentenceFeatures(sent)
        _f = fe.getfeatures()
        if _f:
            yt.append(1)
            features_t.append(_f)
        else:
            pass
    clsf = SklearnClassifier()
    clsf.load_model(modelpath)
    clsf.load_fmap(modelpath)
    xt = clsf.fmap.transform(features_t)
    yt = np.array(yt)
    for x in xt:
        print clsf.predict_proba(x)[0]
        clsf.show_readable_features(x)
    raise Exception