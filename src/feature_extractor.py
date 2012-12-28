#! /usr/bin/env python
# coding: utf-8
'''
precure/src/feature_extractor.py
Created on 28 Dec. 2012
'''
__author__ = "Yu Sawai"
__version__ = "0"
__status__ = "Prototyping"

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
from nltk import ngrams as ng


class FeatureExtractorBase(object):
    """
    Extractor for a sentence given as a list of lines
    """
    nullfeature = {"NULL":1}

    def __init__(self, tags=[]):
        self.features = defaultdict(float)
        self.col_suf = 0
        self.col_off_b = None
        self.col_off_e = None
        self.col_pos = 1
        self.col_chk = 2
        self.col_ner = 3
        self.col_pre = 4
        self.col_psg = -1
        try:
            # for extracting features from parsed data
            # (tab separated dataset in CoNLL like format given by SENNA parser)
            self.tags = [t.split("\t") for t in tags if not t is ""]
        except AttributeError, IndexError:
            # for extracting features from tags' list
            self.tags = [t for t in tags]
        except:
            print pformat(tags)
            raise
        try:
            if self.is_withoffset(self.tags[0]):
                self.col_off_b = 1
                self.col_off_e = 2
                self.col_pos = 3
                self.col_chk = 4
                self.col_ner = 5
                self.col_pre = 6
        except:
            print pformat(tags)
        try:
            self.SUF = [t[self.col_suf].strip() for t in self.tags]
            self.POS = [t[self.col_pos].strip() for t in self.tags]
            # self.CHK = self.get_chunks(self.tags)
            self.CHK = self.get_BIEStag(self.col_chk, self.tags)
            self.NER = self.get_BIEStag(self.col_ner, self.tags)
            print pformat(self.CHK)
            print pformat(self.NER)
            self.WL = zip(self.SUF, self.POS)
        except Exception, e:
            raise
            # self.features.update(FeatureExtractorBase.nullfeature)

    def gen_fn(self, l=None):
        return "_".join(l)

    def is_withoffset(self, tag=None):
        return True if tag[1].isdigit() and tag[2].isdigit() else False

    def get_BIEStag(self, col=None, tag=None):
        _col = [t[col].strip() for t in self.tags]
        idx_B = [(i, t.split("-")[-1]) for i, t in enumerate(_col) if t.startswith("B")]
        idx_E = [(i, t.split("-")[-1]) for i, t in enumerate(_col) if t.startswith("E")]
        idx_S = [(i, t.split("-")[-1]) for i, t in enumerate(_col) if t.startswith("S")]
        _be = [(t[0][1], t[0][0], t[1][0]) for t in zip(idx_B, idx_E)]
        _s = [(t[1], t[0], t[0]+1) for t in idx_S]
        return sorted(_be + _s, key=lambda x:x[1])


class SimpleFeatureExtractor(FeatureExtractorBase):
    """
    Extract features for given case, 
    this one has Surface/POS ngram, dependency, Semantic tags, and SRL related features 
    introduced by Liu et.al 2010

    More interesting features such as sentence wise topic models will be implemented in next update
    """

    def ngrams(self, n=5, v_idx=None):
        """
        Make a query for ngram frequency counter
        @takes:
            n :: N gram size (if n=5, [-2 -1 +1 +2])
            v_idx:: int, positional index of the checkpoint
            w_list:: list, words of a sentence
            alt_candidates:: list, alternative candidates if given
        @returns:
            suf_ngram: {"suf_-2_the": 1, "suf_-1_cat": 1, ...}
            pos_ngram: {"suf_-2_DT": 1, "suf_-1_NN": 1, ...}
        """
        try:
            if not v_idx:
                v_idx = self.v_idx
            suf_ngram = {}
            pos_ngram = {}
            window = int((n - 1)/2)
            if not v_idx:
                v_idx = 0
            core = self.WL[v_idx]
            _lefts = [word for index, word in enumerate(self.SUF) if index < v_idx and index != v_idx][-window:]
            _leftp = [word for index, word in enumerate(self.POS) if index < v_idx and index != v_idx][-window:]
            _rights = [word for index, word in enumerate(self.SUF) if index > v_idx and index != v_idx][:window]
            _rightp = [word for index, word in enumerate(self.POS) if index > v_idx and index != v_idx][:window]
            concats = _lefts + ["*V*"] + _rights
            concatp = _leftp + ["*V*"] + _rightp
            suf_unigram = {SimpleFeatureExtractor.gen_fn(["SUF1G", str(i-window), "".join(w)]):1 
                        for i, w in enumerate(concats) if w != "*V*"}
            pos_unigram = {SimpleFeatureExtractor.gen_fn(["POS1G", str(i-window), "".join(w)]):1 
                        for i, w in enumerate(concatp) if w != "*V*"}
            suf_bigram = {SimpleFeatureExtractor.gen_fn(["SUF2G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concats, 3)) if w[0] == "*V*" or w[2] == "*V*"} if n >= 5 else {}
            pos_bigram = {SimpleFeatureExtractor.gen_fn(["POS2G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concatp, 3)) if w[0] == "*V*" or w[2] == "*V*"} if n >= 5 else {}
            suf_trigram = {SimpleFeatureExtractor.gen_fn(["SUF3G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concats, 4)) if w[0] == "*V*" or w[3] == "*V*"} if n >= 7 else {}
            pos_trigram = {SimpleFeatureExtractor.gen_fn(["POS3G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concatp, 4)) if w[0] == "*V*" or w[3] == "*V*"} if n >= 7 else {}
            suf_c3gram = {SimpleFeatureExtractor.gen_fn(["SUF3G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concats, 3)) if w[1] == "*V*"} if n >= 3 else {}
            suf_c5gram = {SimpleFeatureExtractor.gen_fn(["SUF5G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concats, 5)) if w[2] == "*V*"} if n >= 5 else {}
            # suf_c7gram = {SimpleFeatureExtractor.gen_fn(["SUF7G", "", "-".join(w)]):1 
                        # for i, w in enumerate(ng(concats, 7)) if w[3] == "*V*"} if n >= 7 else {}
            pos_c3gram = {SimpleFeatureExtractor.gen_fn(["POS3G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concatp, 3)) if w[1] == "*V*"} if n >= 3 else {}
            pos_c5gram = {SimpleFeatureExtractor.gen_fn(["POS5G", "", "-".join(w)]):1 
                        for i, w in enumerate(ng(concatp, 5)) if w[2] == "*V*"} if n >= 5 else {}
            # pos_c7gram = {SimpleFeatureExtractor.gen_fn(["POS7G", "", "-".join(w)]):1 
                        # for i, w in enumerate(ng(concatp, 7)) if w[3] == "*V*"} if n >= 7 else {}
            self.features.update(suf_unigram)
            self.features.update(pos_unigram)
            self.features.update(suf_bigram)
            self.features.update(pos_bigram)
            # self.features.update(suf_trigram)
            # self.features.update(pos_trigram)
            self.features.update(suf_c3gram)
            # self.features.update(suf_c5gram)
            # self.features.update(suf_c7gram)
            self.features.update(pos_c3gram)
            # self.features.update(pos_c5gram)
            # self.features.update(pos_c7gram)
        except Exception, e:
            pass
            # self.features.update(SimpleFeatureExtractor.nullfeature)

    def chunk(self, v_idx=None):
        try:
            if not v_idx:
                v_idx = self.v_idx
            l_ctxid = [idx for idx, pt in enumerate(self.POS) if idx < v_idx and pt.startswith("NN")]
            r_ctxid = [idx for idx, pt in enumerate(self.POS) if idx > v_idx and pt.startswith("NN")]
            l_nearestNN = {SimpleFeatureExtractor.gen_fn(["NN", "L", self.SUF[l_ctxid[-1]]]) : 1} if l_ctxid else None
            r_nearestNN = {SimpleFeatureExtractor.gen_fn(["NN", "R", self.SUF[r_ctxid[0]]]) : 1} if r_ctxid else None
            self.features.update(l_nearestNN)
            self.features.update(r_nearestNN)
        except:
            pass



class FeatureExtractor(SimpleFeatureExtractor):
    def dependency(self, v_idx=None):
        try:
            if not v_idx:
                v_idx = self.v_idx
            deps = [(t[FeatureExtractor.col_deprel], t[FeatureExtractor.col_suf], 
                     t[FeatureExtractor.col_pos], t[FeatureExtractor.col_netag]) for t in self.tags
                     if int(t[FeatureExtractor.col_headid]) == v_idx+1]
            depr = {FeatureExtractor.gen_fn(["DEP", d[0].upper(), d[1].lower()+"/"+d[2]]):1 for d in deps}
            depp = {FeatureExtractor.gen_fn(["DEP", d[0].upper(), d[1].lower()]):1 for d in deps}
            depn = {FeatureExtractor.gen_fn(["DEP", d[0].upper(), d[3]]):1 for d in deps if not d[3]=="_" }
            self.features.update(depr)
            self.features.update(depp)
            self.features.update(depn)
        except Exception, e:
            logging.debug(pformat(e))
            # self.features.update(FeatureExtractor.nullfeature)


    def ne(self, v_idx=None):
        try:
            if not v_idx:
                v_idx = self.v_idx
            ne = self.tags[v_idx][FeatureExtractor.col_netag]
            ne_tag = {"V-NE_" + ne: 1} if not ne == "_" else {}
            self.features.update(ne_tag)
        except Exception, e:
            logging.debug(pformat(e))


    @classmethod
    def __format_srl(cls, srldic):
        srl= []
        moc = ("","","","")
        for pkey in srldic:
            out = {}
            out["PRED"] = (pkey[cls.col_suf], pkey[cls.col_pos], pkey[cls.col_deprel], pkey[cls.col_netag])
            try:
                a0 = srldic[pkey]["ARG0"]
                out["ARG0"] = (a0[cls.col_suf], a0[cls.col_pos], a0[cls.col_deprel], a0[cls.col_netag])
            except KeyError:
                out["ARG0"] = moc 
            try:
                a1 = srldic[pkey]["ARG1"]
                out["ARG1"] = (a1[cls.col_suf], a1[cls.col_pos], a1[cls.col_deprel], a1[cls.col_netag])
            except KeyError:
                out["ARG1"] = moc 
            srl.append(out)
        return srl


    def srl(self, v_idx=None):
        try:
            if not v_idx:
                v_idx = self.v_idx
            self.tmp_ARG0 = []
            self.tmp_ARG1 = []
            self.tmp_PRED = defaultdict(dict)
            ARGS = [(l[FeatureExtractor.col_srlrel], l[FeatureExtractor.col_suf], 
                     l[FeatureExtractor.col_pos], l[FeatureExtractor.col_netag]) for l in self.tags 
                    if l[FeatureExtractor.col_srl] != "_" and int(l[FeatureExtractor.col_srl]) - 1 == v_idx]
            if ARGS:
                srlf = {FeatureExtractor.gen_fn(["SRL", t[0], en.lemma(t[1])]):1 for t in ARGS}
                srlp = {FeatureExtractor.gen_fn(["SRL", t[0], en.lemma(t[1])+"/"+t[2]]):1 for t in ARGS}
                srln = {FeatureExtractor.gen_fn(["SRL", t[0], t[3]]):1 for t in ARGS if not t[3]=="_"}
                self.features.update(srlf)
                self.features.update(srlp)
                self.features.update(srln)
        except Exception, e:
            logging.debug(pformat(e))
            # self.features.update(FeatureExtractor.nullfeature)

    @classmethod
    def _load_errorprobs(cls, vspath=None):
        if vspath:
            cls.dic_errorprobs = pickle.load(open(vspath, "rb"))
        else:
            raise IOError


    def _read_errorprob(self):
        try:
            prob_v = FeatureExtractor.dic_errorprobs[self.v]
        except KeyError:
            prob_v = FeatureExtractor.dic_errorprobs[en.lemma(self.v)]
        finally:
            pass

    def errorprob(self, vspath=None):
        if FeatureExtractor.dic_errorprobs:
            pass
        else:
            try:
                _load_errorprobs(vspath)
            except IOError:
                pass


    def topic(self):
        raise NotImplementedError
