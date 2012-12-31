#/usr/bin/env python
#encoding: utf-8

__author__ = 'Keisuke SAKAGUCHI'
__version__ = ""
__copyright__ = ""
__license__ = "GPL v3"
__descripstion__ = ""
__usage__ = ""

import sys
import os

# Constant values/strings here.
# You may change them according to your environment.
sennaPath = '/home/keisuke-sa/tools/senna/'

# Input: document as a string
# Output: the parsing result file named tmpOut.txt by SENNA
def sennaParse(documents):
    #documents to file
    tmpIn = open('tmpIn.txt', 'wb')
    tmpIn.write(documents)
    tmpIn.close()
    os.system(sennaPath + 'senna-linux64 ' + '-path ' + sennaPath + ' < tmpIn.txt > tmpOut.txt')
    os.remove('tmpIn.txt')
    return

if __name__ == '__main__':
    # For module tests, write code here.
    
    documents = 'This is a sentence.\nThis is a second one.'
    sennaParse(documents)
