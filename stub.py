#!/home/oggei/dev/virtualenvs/py2.7-enc/bin/python
'''
Created on 12/feb/2014

@author: oggei
'''

from enc import IeoEnc

if __name__ == '__main__':

    nodename = 'parolini.segreterie'
    
    enc = IeoEnc(nodename)
    print enc.__repr__()
