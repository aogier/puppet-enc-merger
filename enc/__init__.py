import collections
import logging
import re
import sys
import xmlrpclib

from stevedore import driver
import yaml

from config import config

# plugins = []
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('enc')
logger.setLevel(logging.DEBUG)

wikiRoot = 'PuppetClasses'

# plugin registration
# from enc.plugins.calendars import CalendarPlugin

apiservers = []

class ApiServer(object):

    class __metaclass__(type):
        '''
        Maintain couple of global plugin registries.
        
        If called whitin Mafreader class creation, then update global
        _fileFormats registry.
        If called whitin a subclass creation, then update local
        _decoders registry.
        '''
        def __new__(cls, name, bases, _dict):
            _type = type.__new__(cls, name, bases, _dict)
            if name != 'ApiServer':
                logger.debug('registering api server: %s' % name)
                apiservers.append(_type)
            return _type

    def __init__(self, uri):
        self.uri = uri
        self.logger = logging.getLogger('%s api server' % self.__type__)
        self.logger.setLevel(logging.DEBUG)
    
    def getNode(self, uri):
        raise Exception, 'not implemented'

class XmlRpcApiServer(ApiServer):
    
    __type__ = 'xmlrpc'
    #fixme: it's a conf
    __prefix__ = 'PuppetClasses'
    
    regex = re.compile(r'.*{{{\|(?P<yaml>.*)\|}}}.*')
    
    def __init__(self, uri):
        super(XmlRpcApiServer, self).__init__(uri)
        logger.debug('called with uri: %s' % uri)
        self.xmlrpc = xmlrpclib.ServerProxy(self.uri)
    
    def getNode(self, uri):
        target = self.__prefix__ + uri
        self.logger.debug('getting %s' % target)
        node = self.xmlrpc.wiki.getPage(target)
        string = node.replace('\n', '|')
        match = self.regex.match(string)
        if match:
            group = match.groupdict()['yaml']
            out = group.replace('|', '\n')
            return yaml.load(out)
        return {}


class IeoEnc(object):

    data = collections.defaultdict(collections.defaultdict)

    def __init__(self, nodename):
        logger.debug('called for node %s' % nodename)
        domainParts = reversed(nodename.split('.'))
        self.api = XmlRpcApiServer(config.get('main', 'start'))        
        uri = ''
        for domainPart in domainParts:
            uri = '/'.join([uri, domainPart])  
            logger.debug('merging classes from uri "%s"' % uri)
            try:
                data = self.api.getNode(uri)
            except:
                logger.warn('api failed on "%s"' % uri)
                continue
            for key in 'classes', 'parameters', 'environment':
                if data.get(key):
                    self.data[key].update((k,v or {}) for k,v in data[key].iteritems())
        #FIXME: remove
        logger.debug(self.data)

        if self.data.get('classes'):
            
            for _class in self.data['classes']:
                logger.debug('searching plugin for class %s ...' % _class)
                try:
                    plugin = driver.DriverManager(
                                                  namespace = 'eu.ieo.puppet.classes',
                                                  name = _class,
                                                  invoke_on_load=True,
                                                  invoke_args=(nodename, self.data),
                                                  )
                # driver not found
                except RuntimeError:
                    continue
                logger.debug('executing plugin %s ...' % plugin)
                classData, parameters = plugin.driver.execute()
                self.data['classes'][_class].update(classData)
                self.data['parameters'].update(parameters)

    def __repr__(self):
        data = dict((k,dict(v)) for k,v in self.data.iteritems())
        return yaml.dump(data,
                         default_flow_style=False,
                         explicit_start=True,
                         ).replace('null', '')


def main():
    enc = IeoEnc(sys.argv[1])
    print enc
