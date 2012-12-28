#! /usr/bin/env python
# coding: utf-8
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
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
import cPickle as pickle
from collections import defaultdict
from pprint import pformat
from time import time
from random import shuffle
try: 
    from sklearn.linear_model import SGDClassifier, Perceptron
    from sklearn.feature_extraction import DictVectorizer
    from sklearn.svm import NuSVC, SVC
    from sklearn import preprocessing
    import numpy as np
    import scipy as sp
    from feature_extractor import SentenceFeatures
except:
    print "Prerequisite: Please install 'sklearn', 'numpy', 'scipy'"
    raise ImportError


chunk_gen = lambda x,y: (x[i:i+y] for i in range(0,len(x),y))

class CaseMaker(object):
    def __init__(self, path_neg=None, path_pos=None, out_path_model=None):
        """
        Read corpus files (assuming SENNA format)
        """
        self.corpus_neg = [s.split("\n") for s in open(path_neg).read().split("\n\n") if s]
        self.corpus_pos = [s.split("\n") for s in open(path_pos).read().split("\n\n") if s]
        self.out_path_model = out_path_model

    def get_instances(self):
        self.labels_neg = []
        self.features_neg = []
        self.labels_pos = []
        self.features_pos = []
        self.labels = []
        self.features = []
        for sent in self.corpus_neg:
            fe = SentenceFeatures(sent)
            _f = fe.getfeatures()
            if _f:
                self.labels_neg.append(0)  # 0 means negative (non-native like class)
                self.features_neg.append(_f)
            else:
                pass
        for sent in self.corpus_pos:
            fe = SentenceFeatures(sent)
            _f = fe.getfeatures()
            if _f:
                self.labels_pos.append(1)  # 1 means positive (native like class)
                self.features_pos.append(_f)
            else:
                pass
        self.features = self.features_neg + self.features_pos
        self.labels = self.labels_neg + self.labels_pos
        self.featureid_map = DictVectorizer(sparse=True)
        self.X = self.featureid_map.fit_transform(self.features)
        self.Y = np.array(self.labels)
        return self.X, self.Y, self.featureid_map



class SklearnClassifier(object):
    def __init__(self, opts=None):
        self.model = None
        self.opts = opts
        self.multicpu = 1


    def trainSGD(self, X=None, Y=None):
        sgd = SGDClassifier(**self.opts)
        self.model = sgd.fit(X, Y)

    def trainSVM(self, X=None, Y=None):
        # svm = NuSVC(nu=0.5, kernel='rbf', degree=3, gamma=0.0, coef0=0.0, shrinking=True, probability=True, tol=0.001, cache_size=500, verbose=False, max_iter=-1)
        # svm = SVC(C=0.5, kernel='rbf', degree=3, gamma=0.0, coef0=0.0, shrinking=True, probability=True, tol=0.001, cache_size=200, class_weight=None, verbose=True, max_iter=-1)
        svm = SVC(**self.opts)
        self.model = svm.fit(X, Y)

    def predict_proba(self, X=None, Y=None):
        """
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

    def save_model(self, output_path=None):
        try:
            with open(os.path.join(output_path, "model_svm"), "wb") as f:
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
            with open(os.path.join(path_model, "model_svm"), "rb") as f:
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
        try:
            strf = self.fmap.inverse_transform(X)
            print pformat(strf)
        except:
            raise


def mkmodel(path_neg=None, path_pos=None, path_model=None):
    svcopts = {"C":0.5, "kernel":'rbf', "degree":3, "gamma":0.0, 
               "coef0":0.0, "shrinking":True, 
               "probability":True, "tol":0.001, "cache_size":200, "class_weight":None, 
               "verbose":True, "max_iter":-1}
    cm = CaseMaker(path_neg=path_neg, path_pos=path_pos)
    X, Y, fmap = cm.get_instances()
    clsf = SklearnClassifier(svcopts)
    clsf.trainSVM(X, Y)
    try:
        os.makedirs(os.path.abspath(path_model))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    clsf.save_model(path_model)
    clsf.save_fmap(fmap, path_model)
    return clsf.model


if __name__=='__main__':
    import argparse
    starttime = time.time()
    argv = sys.argv
    argc = len(argv)
    description = """python classifier_skl.py -n [parsed_file_of_negative_class]
     -p [parsed_file_of_positive_class] -o [output_path_of_model]\n"""
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("-o", '--model_save_dir', action="store",
                    help="path to trained classifier model directory")
    ap.add_argument("-n", '--neg-class', action="store",
                    help="path_to_parsed_file (negative class)")
    ap.add_argument("-p", '--pos-class', action="store",
                    help="path_to_parsed_file (positive class)")
    args = ap.parse_args()
    if args:
        mkmodel(path_neg=args.neg_class, path_pos=args.pos_class, path_model=args.model_save_dir)
    else:
        ap.print_help()
    quit()
