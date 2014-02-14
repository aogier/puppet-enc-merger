import xmlrpclib
import yaml
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

    data = {}

    def __init__(self, nodename):
        logger.debug('called for node %s' % nodename)
        self.nodename = nodename
        domainParts = reversed(nodename.split('.'))
        self.xmlrpc = xmlrpclib.ServerProxy(xmlrpc_uri)
        uri = wikiRoot
        for domainPart in domainParts:
            uri = '/'.join([uri, domainPart])  
            logger.debug('merging classes from uri "%s"' % uri)
            page = yaml.load(self.xmlrpc.wiki.getPage(uri))
            for key in 'classes', 'parameters', 'environment':
                if page.get(key):
                    if isinstance(self.data.get(key, None), dict):
                        self.data[key].update(page[key])
                    else:
                        self.data[key] = page[key]
        logger.debug(self.data)

        for _class in self.data['classes']:
            logger.debug('searching plugin for class %s...' % _class)
            for c in plugins:
                if c.__puppet_class__ == _class:
                    logger.debug('... found %s' % c)
                    classData, parameters = c(nodename, self.data).execute()
                    if isinstance(self.data['classes'][_class], dict):
                        self.data['classes'][_class].update(classData)
                    else:
                        self.data['classes'][_class] = classData
                    if self.data['parameters']:
                        self.data['parameters'].update(parameters or {})
                    else:
                        self.data['parameters'] = parameters

    def __repr__(self):
        return yaml.dump(self.data,
                         default_flow_style=False,
                         explicit_start=True,
                         ).replace('null', '')
