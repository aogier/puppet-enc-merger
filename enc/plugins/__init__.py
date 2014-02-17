import abc

class EncPlugin(object):
    
    __metaclass__ = abc.ABCMeta

    def __repr__(self):
        return self.__class__.__name__

    @abc.abstractmethod
    def execute(self):
        '''execute plugin'''
