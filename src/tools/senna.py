#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
senna.py
=========
A wrapper class for SENNA parser.

>>> sp = SennaWrap(u"~/usr/bin/senna")
>>> sp.parseSentence(u"The cat sat on the mat.")

Parameters
----------
bin: unicode string
    path to the directory where senna parser is
sentence: unicode, string
    input string to be parsed

Returns
-------
result: list
    parsed sentence, one item per output line.
"""

__author__ = 'Yuta Hayashibe' 
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"


import subprocess


class SennaWrap(object):
    def __init__(self, bin):
        assert isinstance(bin, unicode)
        subproc_args = { 'stdin': subprocess.PIPE,
                         'stdout': subprocess.PIPE,
                         'stderr': subprocess.STDOUT,  # not subprocess.PIPE
                         'cwd': '.',
                         'close_fds' : True,          }
        args = [bin + 'senna', '-path', bin]
        try:
            self.p = subprocess.Popen(args, **subproc_args)
        except OSError:
            raise 
        (self.stdouterr, self.stdin) = (self.p.stdout, self.p.stdin)

    def __del__(self):
        self.p.stdin.close() #send EOF (This is not obligate)
        try:
            self.p.kill()
            self.p.wait()
        except OSError:
            # can't kill a dead proc
            pass


    def parseSentence(self, sentence):
        self.p.stdin.write(sentence + "\n")

        result = []
        while True:
            line = self.stdouterr.readline()[:-1]
            if not line:
                break
            result.append(line.split())
        return result

    def getPredicates(self, sentence):
        result = self.parseSentence(sentence)
        if len(result) == 0:
            return []

        DEFAULT_COLUM_NUM = 6
        PAS_START =4 
        pred_num = len(result[0]) - DEFAULT_COLUM_NUM
#        preds = [[] for i in xrange(0, pred_num)]
        preds = []
        _pred_count = 0

        for pos, items in enumerate(result):
            pred = items[PAS_START]
            if pred != "-":
                preds.append([pos, pred, {}])

        for pos, items in enumerate(result):
            for pred_id in xrange(0, pred_num):
                my_column = items[PAS_START+1 + pred_id]
                if my_column != 'O':
                    pred  = preds[pred_id]
                    pred[2][my_column] = items[0]
#                    pred[2][my_column] = (pos, items[0])

        return preds


if __name__ == '__main__':
    sennaPath = u'/data/tool/senna/'
    senna = SennaWrap(sennaPath)
    import sys 
    while True:
        string = raw_input('input: ')

        if len(string) == 0:
            sys.exit()
        out = senna.parseSentence(string)
        out = senna.getPredicates(string)
        print ">" , out


