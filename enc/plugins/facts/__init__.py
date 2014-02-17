import abc
from enc import logger

class FactsPlugin(object):
    
    __metaclass__ = abc.ABCMeta

    def __repr__(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def execute(self):
        '''execute plugin'''

    def __init__(self, uri):
        self.uri = uri
        self.logger = logger.getChild('api (%s)' % self.__type__)
    
    @abc.abstractmethod
    def getNode(self, uri):
        '''return node'''
