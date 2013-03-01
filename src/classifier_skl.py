#!/usr/bin/env python
#coding:utf-8
'''
precure/src/classifer_skl.py
'''
__author__ = 'Yu SAWAI'
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"
__descripstion__ = ""
__usage__ = ""

import os
import errno
import sys
import logging
import cPickle as pickle
from collections import defaultdict
from pprint import pformat
from time import time
from random import shuffle, randrange
import glob
import json
try: 
    from sklearn.linear_model import SGDClassifier, Perceptron
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.svm import NuSVC, SVC, SVR
    from sklearn import preprocessing
    import numpy as np
    import scipy as sp
    from tools import sparse_matrices
    from feature_extractor import DocumentFeatures, SentenceFeatures
except ImportError:
    print "Prerequisite: This requires 'sklearn', 'numpy', 'scipy'"
    exit()

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
chunk_gen = lambda x,y: (x[i:i+y] for i in range(0,len(x),y))


def train_model(path_dat=None, path_model=None):
    """
    Read JSON files with some degrees of fluency 
        (each file has different fluency, e.g. 0_low.json, 1_mid.json)
    """
    svropts = {"C":1000, "kernel":"poly", "degree":2, "gamma":0.0, 
               "coef0":0.0, "shrinking":True, 
               "probability":True, "tol":0.001, "cache_size":200, 
               "verbose":True, "max_iter":-1}

    # Simply load files in dictionary order
    # (so files must have the same order of fluency level)
    files = glob.glob(path_dat+"*.json")
    dat = [json.load(open(f,'r')) for f in files]
    X, Y, fmap = make_cases(dat)
    clsf = SklearnClassifier(svropts)
    clsf.trainSVR(X, Y)
    try:
        os.makedirs(os.path.abspath(path_model))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    clsf.save_model(path_model)
    clsf.save_fmap(fmap, path_model)
    return clsf.model


def make_cases(traindata=[]):
    """
    Read corpus files loaded from JSON files as a list 
        i.e. [[`low`], [`mid`], [`high`]]
    """
    scores = []
    features = []
    for n, docs in enumerate(traindata):
        _f, _s = process_each_cat(n, docs)
        features += _f
        scores += _s
    featureid_map = DictVectorizer(sparse=True)
    X = featureid_map.fit_transform(features)
    Y = np.array(scores)
    return X, Y, featureid_map


def process_each_cat(cat=None, docs=[]):
    """
    Parameters
    ----------
    cat: integer
        low=0, mid=1, high=2
    docs: list
        [[`doc1`],...]

    Returns
    -------
    _f: list of dictionaries 
        feature vectors 
    _s: list of integers
        scores
    """
    assignment = [20, 70, 100]
    _f = []
    _s = []
    for d in docs:
        fe = DocumentFeatures(d, parse=True)
        fe.pipeline()
        _f.append(fe.features)
        b = assignment[cat]
        # s = randrange(b-10, b+10)/100.0
        _s.append(s)
    assert len(_f)==len(_s)
    return _f, _s


#==============================================================================

class SklearnClassifier(object):
    """
    A wrapper for scikit-learn classifiers
    """
    def __init__(self, opts=None):
        self.model = None
        self.fmap = None
        self.opts = opts
        self.multicpu = 1

    def trainSGD(self, X=None, Y=None):
        sgd = SGDClassifier(**self.opts)
        self.model = sgd.fit(X, Y)

    def trainSVM(self, X=None, Y=None):
        svc = SVC(**self.opts)
        self.model = svc.fit(X, Y)

    def trainSVR(self, X=None, Y=None):
        svr = SVR(**self.opts)
        self.model = svr.fit(X, Y)

    def transform(self, X=None):
        if self.fmap:
            return self.fmap.transform(X)
        else:
            print "FeatureIDMapping is not loaded"
            raise TypeError

    def predict_proba(self, X=None, Y=None):
        """
        Only for estimators which have `predict_proba` method

        Parameters
        ----------
        X: {array-like, sparse matrix}, shape = [n_samples, n_features]
            Data.

        Y : numpy array of shape [n_samples]
            Multi-class targets.

        Returns
        -------
        pred_p: {array-like}, shape = {n_samples, n_classes}
        """
        if hasattr(self.model, "predict_proba"):
            pred_p = self.model.predict_proba(X)
            return pred_p
        else:
            raise NotImplementedError

    def predict(self, X=None, Y=None):
        if hasattr(self.model, "predict"):
            pred = self.model.predict(X)[0]
            return pred
        else:
            raise NotImplementedError

    def save_model(self, output_path=None):
        try:
            with open(os.path.join(output_path, "model"), "wb") as f:
                pickle.dump(self.model, f, -1)
        except Exception, e:
            print pformat(e)
            with open(output_path, "wb") as f: 
                pass

    def save_fmap(self, fmap=None, output_path=None):
        try:
            with open(os.path.join(output_path, "fmap"), "wb") as f:
                pickle.dump(fmap, f, -1)
        except Exception, e:
            print pformat(e)
            with open(output_path, "wb") as f: 
                pass

    def load_model(self, path_model=None):
        try:
            with open(os.path.join(path_model, "model"), "rb") as f:
                self.model = pickle.load(f)
        except:
            raise

    def load_fmap(self, path_model=None):
        try:
            with open(os.path.join(path_model, "fmap"), "rb") as f:
                self.fmap = pickle.load(f)
        except:
            raise

    def show_readable_features(self, X=None):
        """
        Show human-readable features
        Currently, this simply shows string-IDs of features
        """
        try:
            strf = self.fmap.inverse_transform(X)
            print pformat(strf)
        except:
            raise



if __name__=='__main__':
    import argparse
    starttime = time()
    argv = sys.argv
    argc = len(argv)
    description = """python classifier_skl.py -d ../corpora -o ../models\n"""
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("-o", '--model_save_dir', action="store",
                    help="path to trained classifier model directory")
    ap.add_argument("-d", '--dataset_path', action="store",
                    help="path_to_dir of JSON files")
    args = ap.parse_args()
    if args.dataset_path and args.model_save_dir:
        train_model(path_dat=args.dataset_path, path_model=args.model_save_dir)
    else:
        ap.print_help()
    quit()
