#!/usr/bin/env python
#coding:utf-8
'''
Sample code for document-wise scoring
'''
__author__ = 'Yu SAWAI'
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"
__descripstion__ = ""
__usage__ = ""

from feature_extractor import DocumentFeatures, SentenceFeatures
from classifier_skl import SklearnClassifier

def get_score(doc=[], modelpath=None):
    '''
    Parameters
    ----------
    doc: a list of lists
        document as a list 
        (currently assuming this is not yet parsed)
    e.g.: [ ["The", "cat", "sat", "on", "the", "mat", "."],
           ["Colorless", "green", "ideas", "sleep", "furiously", "."] ]

    Returns
    -------
    score: float, ranges 0 to 1
        regression score
    '''
    fe = DocumentFeatures(doc)
    _f = fe.pipeline()
    model = SklearnClassifier()
    model.load_model(modelpath)
    model.load_fmap(modelpath)
    f = model.transform(_f)
    score = model.predict(f) 
    return int(score*100)

if __name__ == '__main__':
    test = [ ["The", "cat", "sat", "on", "the", "mat", "."],
           ["Colorless", "green", "ideas", "sleep", "furiously", "."] ]
    print get_score(test, "../model/")
