#!/usr/bin/env python
#encoding: utf-8

__author__ = 'Keisuke SAKAGUCHI'
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"
__descripstion__ = ""
__usage__ = ""

import sys
import os
import aspell
# Prerequisite: Install aspell-python from http://wm.ite.pl/proj/aspell-python/index-c.html


speller = aspell.Speller('lang', 'en')

def spellcheck(wordList):
    errorList = []
    for word in wordList:
        if word.isalpha():
            if speller.check(word):
                pass
            else:
                errorList.append(word)
        else:
            pass
        
    #print errorList
    return errorList


if __name__ == '__main__':
   
    # for module test
    sampleWordList = ['thiss', 'is', 'a', 'testtt', '.']
    spellcheck(sampleWordList)
