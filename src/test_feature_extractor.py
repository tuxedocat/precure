# ! /usr/bin/env python
# coding: utf-8

from nose.plugins.attrib import attr
from feature_extractor import FeatureExtractor
from datetime import datetime
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.DEBUG)
import os
from pprint import pformat
from collections import defaultdict
import cPickle as pickle
from sklearn.feature_extraction import DictVectorizer


class TestFext(object):
    def setUp(self):
        self.testpath = "test/sennatags.txt"
        self.testpath_off = "test/sennatags_off.txt"

    @attr("without_offset")
    def test_single(self):
        self.testdata = [doc.split("\n") for doc in open(self.testpath).read().split("\n\n")]
        print pformat(self.testdata)
        for t in self.testdata:
            fe = FeatureExtractor(t)
            fe.ngrams(n=5)
            logging.debug(pformat(zip(fe.SUF, fe.POS)))
            logging.debug(pformat(fe.features))

            vec = DictVectorizer(sparse=True)
            array_f = vec.fit_transform(fe.features).toarray()
            # logging.debug(pformat(array_f))

        raise Exception