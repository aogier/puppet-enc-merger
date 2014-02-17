import abc

class EncPlugin(object):
    
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def execute(self):
        '''execute plugin'''
