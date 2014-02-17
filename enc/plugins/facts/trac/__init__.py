import re
import urlparse
from enc import logger
import xmlrpclib
import yaml
from enc.plugins.facts import FactsPlugin
import collections
from enc.config import config

class TracFactsPlugin(FactsPlugin):
    
    __type__ = 'ieo::facts::trac'
    #fixme: it's a conf
    __prefix__ = 'PuppetClasses'
    
    regex = re.compile(r'.*{{{\|(?P<yaml>.*)\|}}}.*')
    data = collections.defaultdict(collections.defaultdict)

    def __init__(self, uri):
        super(TracFactsPlugin, self).__init__(uri)
        
        rpc = config.get(self.__type__, 'uri')
        
        parsedUri = urlparse.urlparse(rpc)
        safeUri = '%s://%s:***@%s/%s' % (parsedUri.scheme, parsedUri. username,
                                         parsedUri.hostname, parsedUri.path)
        logger.debug('called with uri: %s' % safeUri)
        self.xmlrpc = xmlrpclib.ServerProxy(rpc)
        
        self.domainParts = reversed(uri.split('.'))
    
    def execute(self):
        uri = ''
        for domainPart in self.domainParts:
            uri = '/'.join([uri, domainPart])  
            logger.debug('merging classes from uri "%s"' % uri)
            try:
                data = self.getNode(uri)
            except Exception, e:
                logger.warn('api failed on "%s" - %s' % (uri, e))
                continue
            for key in 'classes', 'parameters', 'environment':
                if data.get(key):
                    self.data[key].update((k,v or {}) for k,v in data[key].iteritems())
        return self.data

    
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
