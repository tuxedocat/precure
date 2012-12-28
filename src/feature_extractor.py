#! /usr/bin/env python
# coding: utf-8
from __future__ import division
'''
precure/src/feature_extractor.py
'''
__author__ = 'Yu SAWAI'
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
from nltk import ngrams as ng


class SentenceFeatures(object):
    """
    Extractor for a sentence given as a list of lines
    """
    nullfeature = {"NULL":1}

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
        self.length()
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
        print srl
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
            s_len = math.log10(len(self.tags))
        except ValueError:
            s_len = 0
        if s_len < 1.0:
            s_len_f.update({"LEN_LOG<1.0":1})
        for _t in (x * 0.1 for x in range(10, 21)):
            if s_len >= _t:
                s_len_f.update({"LEN_LOG>%1.1f"%_t:1})
        # print pformat(self.tags)
        self.features.update(s_len_f)


    def bow(self):
        bowf = {"BOW_%s"%w.lower() :1 for w in self.SUF}
        self.features.update(bowf)


