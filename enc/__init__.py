import xmlrpclib
import yaml
import re
import collections
plugins = []

import logging

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.getLogger('enc')
logger.setLevel(logging.DEBUG)

from local import xmlrpc_uri
wikiRoot = 'PuppetClasses'

from enc.calendars import CalendarPlugin

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
        self.xmlrpc = xmlrpclib.ServerProxy(xmlrpc_uri)
        uri = wikiRoot
        for domainPart in domainParts:
            uri = '/'.join([uri, domainPart])  
            logger.debug('merging classes from uri "%s"' % uri)
            try:
                page = self.xmlrpc.wiki.getPage(uri)
            except:
                continue
            data = yaml.load(extract(page))
            for key in 'classes', 'parameters', 'environment':
                if data.get(key):
                    self.data[key].update(data[key])
        logger.debug(self.data)

        if self.data.get('classes'):
            for _class in self.data['classes']:
                logger.debug('searching plugin for class %s ...' % _class)
                for plugin in plugins:
                    if plugin.__puppet_class__ == _class:
                        logger.debug('... found %s' % plugin)
                        classData, parameters = plugin(nodename, self.data).execute()
                        if isinstance(self.data['classes'][_class], dict):
                            self.data['classes'][_class].update(classData or {})
                        else:
                            self.data['classes'][_class] = classData
                        if self.data['parameters']:
                            self.data['parameters'].update(parameters or {})
                        else:
                            self.data['parameters'] = parameters

    def __repr__(self):
        return yaml.dump(dict(self.data),
                         default_flow_style=False,
                         explicit_start=True,
                         ).replace('null', '')
