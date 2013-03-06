#!/usr/bin/env python
#coding:utf-8
from __future__ import division
'''
precure/src/feature_extractor.py
'''
__author__ = "Yu SAWAI"
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"
__descripstion__ = ""
__usage__ = ""

from datetime import datetime
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.DEBUG)
import os
import sys
from collections import defaultdict
from pprint import pformat
from numpy import array
import cPickle as pickle
import traceback
import math
import nltk
from nltk import ngrams
from tools import senna
import aspell

path = unicode(os.environ["SENNAPATH"])
sp = senna.SennaWrap(path)
speller = aspell.Speller('lang', 'en')


class DocumentFeatures(object):
    """
    Document level features
    (takes document as a list of lists)
    """
    def __init__(self, doc=[], parse=True):
        if parse is True:
            parsed = [sp.parseSentence(" ".join(s)) for s in doc]
            self.doc = parsed
        else:
            self.doc = doc
        self.features = defaultdict(float)

    def pipeline(self):
        self.preprocess()
        self.doc_bow()
        # self.avg_length()
        self.doc_ngram()
        self.doc_spell()
        return self.features

    def preprocess(self):
        _sf = [getsf(s) for s in self.doc]
        self.sentfeatures = [s[0] for s in _sf]
        self.numspellerrors = [s[1] for s in _sf]
        self.docfeatures = reduce(lambda x,y: x+y, [d.items() for d in self.sentfeatures])

    def doc_bow(self):
        # Get tuples from sentence-wise BOW, and then flatten them as a list
        docbow = {id:v for (id, v) in self.docfeatures if id.startswith("BOW")}
        self.features.update(docbow)

    def avg_length(self):
        """
        Average length of sentences in a doc.
        """
        avglen = sum([len(l) for l in self.doc])/float(len(self.doc))
        if avglen < 5:
            self.features.update({"AVGLEN<5":1})
        for _t in range(5, 100, 5):
            if avglen >= _t:
                self.features.update({"AVGLEN>%d"%_t:1})

    def doc_ngram(self):
        docngram = {id:v for (id, v) in self.docfeatures if id.startswith("Ngram")}
        self.features.update(docngram)

    def doc_spell(self):
        numsplerr = sum(self.numspellerrors)
        if numsplerr == 0:
            self.features.update({"SpellError_None":1})
        for _t in range(2, 50, 2):
            if numsplerr >= _t:
                self.features.update({"SpellError_>%d"%_t:1})


def getsf(tags=[]):
    sf = SentenceFeatures(tags)
    f = sf.getfeatures()
    num_spellerror = sf.spellerror
    return f, num_spellerror


class SentenceFeatures(object):
    """
    Extractor for a sentence given as a list of lines
    (each line is assumed to be formatted as tab-separated 
        style, and must be parsed by SENNA parser)
    """
    def __init__(self, tags=[]):
        self.features = defaultdict(float)
        self.col_suf = 0
        self.col_offset = None
        self.col_pos = 1
        self.col_chk = 2
        self.col_ner = 3
        self.col_pre = 4
        self.col_psg = -1
        try:
            # for extracting features from parsed data
            # (tab separated dataset in CoNLL like format given by SENNA parser)
            self.tags = [[s.strip() for s in t.split("\t")] for t in tags if not t is ""]
        except AttributeError, IndexError:
            # for extracting features from tags' list
            self.tags = [t for t in tags]
        except:
            print pformat(tags)
            raise
        if self.is_withoffset(self.tags[0]):
            self.col_offset = 1
            self.col_pos += 1
            self.col_chk += 1
            self.col_ner += 1
            self.col_pre += 1
            self.OFFSET = [tuple(t[self.col_offset].split()) for t in self.tags]
        else:
            self.OFFSET = None
        try:
            self.SUF = [t[self.col_suf] for t in self.tags]
            self.POS = [t[self.col_pos] for t in self.tags]
            self.CHK = self.get_BIEStag(self.col_chk, self.tags)
            self.NER = self.get_BIEStag(self.col_ner, self.tags)
            self.SRL = self.get_SRL()
        except Exception, e:
            logging.debug(pformat(tags))
            raise

    def getfeatures(self):
        self.bow()
        self.ngrams()
        self.spell()
        return self.features

    def gen_fn(self, l=None):
        return "_".join(l)

    def is_withoffset(self, tag=None):
        return True if tag[1].split()[0].isdigit() else False

    def get_SRL(self):
        _t = [t[self.col_pre] for t in self.tags if not t[self.col_pre] == "-"]
        srl = []
        for i, w in enumerate(_t):
            srl.append(self.get_BIEStag(self.col_pre+i+1, self.tags))
        # print srl
        return srl

    def get_BIEStag(self, col=None, tag=None):
        _col = [t[col] for t in self.tags]
        try:
            idx_B = [(i, t.split("-")[-1]) for i, t in enumerate(_col) if t.startswith("B")]
            idx_E = [(i, t.split("-")[-1]) for i, t in enumerate(_col) if t.startswith("E")]
            idx_S = [(i, t.split("-")[-1]) for i, t in enumerate(_col) if t.startswith("S")]
            _be = [(t[0][1], t[0][0], t[1][0]) for t in zip(idx_B, idx_E)] if idx_B and idx_E else []
            _s = [(t[1], t[0], t[0]+1) for t in idx_S]
            return sorted(_be + _s, key=lambda x:x[1])
        except:
            return None

    def length(self):
        s_len_f = defaultdict(float)
        try:
            s_len = len(self.tags)
        except ValueError:
            s_len = 0
        if s_len < 5:
            s_len_f.update({"LEN<5":1})
        for _t in range(5, 100, 5):
            if s_len >= _t:
                s_len_f.update({"LEN>%d"%_t:1})
        self.features.update(s_len_f)

    def bow(self):
        bowf = {"BOW_%s"%w.lower() :1 for w in self.SUF}
        bowposf = {"BOWPOS_%s/%s"%(w[0].lower(), w[1].lower()) :1 for w 
                                              in zip(self.SUF, self.POS)}
        self.features.update(bowf)
        self.features.update(bowposf)

    def ngrams(self, ns=[2]):
        _p = ["/".join(t) for t in zip(self.SUF, self.POS)]
        for n in ns:
            ngf = {"Ngram(N={})_{}".format(n, "_".join(t)) : 1
                    for t in ngrams(self.SUF, n)}
            ngfp = {"NgramP(N={})_{}".format(n, "_".join(t)) : 1
                    for t in ngrams(_p, n)}
        self.features.update(ngf)
        self.features.update(ngfp)

    def spell(self):
        _c = 0
        _sple = [1 for s in self.SUF if (not s.istitle() and not speller.check(s))]
        _c += sum(_sple)
        # self.features.update({"SpellError_{}".format(_c) : 1})
        self.spellerror = _c

if __name__=='__main__':
    pass
