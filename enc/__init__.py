import xmlrpclib
import yaml
import re
import collections
import sys
plugins = []

import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger('enc')
logger.setLevel(logging.DEBUG)

from local import xmlrpc_uri, remote
wikiRoot = 'PuppetClasses'

# plugin registration
from enc.calendars import CalendarPlugin

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
#             logger.debug('registering file format: %s' % name)
            apiservers.append(_type)
            return _type

    def __init__(self, uri):
        self.uri = uri
    
    def getNode(self, uri):
        raise Exception, 'not implemented'

class XmlRpcApiServer(ApiServer):
    
    __type__ = 'xmlrpc'
    #fixme: it's a conf
    __prefix__ = 'PuppetClasses'
    
    def __init__(self, uri):
        super(XmlRpcApiServer, self).__init__(uri)
        self.xmlrpc = xmlrpclib.ServerProxy(self.uri)
    
    def getNode(self, uri):
        target = self.uri + uri
        print 'getting', target
        return self.xmlrpc.wiki.getPage(self.__prefix__ + uri)

class IeoEnc(object):

    data = collections.defaultdict(dict)

    def __init__(self, nodename):
        def extract(s):
            string = s.replace('\n', '|')
            regex = re.compile(r'.*{{{\|(?P<yaml>.*)\|}}}.*')
            match = regex.match(string)
            if match:
                out = match.groupdict()['yaml']
                return out.replace('|', '\n')
            return ''
        logger.debug('called for node %s' % nodename)
        self.nodename = nodename
        domainParts = reversed(nodename.split('.'))
        
#         self.xmlrpc = xmlrpclib.ServerProxy(xmlrpc_uri)
        self.api = XmlRpcApiServer(remote['xmlrpc'])
        
#         uri = wikiRoot
        uri = ''
        for domainPart in domainParts:
            uri = '/'.join([uri, domainPart])  
            logger.debug('merging classes from uri "%s"' % uri)
#             try:
                
#                 page = self.xmlrpc.wiki.getPage(uri)
            page = self.api.getNode(uri)
                
#             except:
#                 print 'except !'
#                 continue
            data = yaml.load(extract(page))
            for key in 'classes', 'parameters', 'environment':
                if data.get(key):
                    self.data[key].update(data[key])
        #FIXME: remove
        logger.debug(self.data)

        if self.data.get('classes'):
            for _class in self.data['classes']:
                logger.debug('searching plugin for class %s ...' % _class)
                for plugin in plugins:
                    logger.debug('trying %s' % plugin)
                    if plugin.__puppet_class__ == _class:
                        logger.debug('... found %s' % plugin)
                        try:
                            classData, parameters = plugin(nodename, self.data).execute()
                        except:
                            continue
                        if isinstance(self.data['classes'][_class], dict):
                            self.data['classes'][_class].update(classData or {})
                        else:
                            self.data['classes'][_class] = classData
                        if self.data['parameters']:
                            self.data['parameters'].update(parameters or {})
                        else:
                            self.data['parameters'] = parameters
                        break

    def __repr__(self):
        return yaml.dump(dict(self.data),
                         default_flow_style=False,
                         explicit_start=True,
                         ).replace('null', '')


def main():
    enc = IeoEnc(sys.argv[1])
    print enc.__repr__()
