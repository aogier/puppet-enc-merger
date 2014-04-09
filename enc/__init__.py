import collections
import logging
import re
import sys
import xmlrpclib

from stevedore import driver
import yaml


import urlparse

# plugins = []
FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('enc')
logger.setLevel(logging.DEBUG)

from config import config

wikiRoot = 'PuppetClasses'

class IeoEnc(object):

    data = collections.defaultdict(collections.defaultdict)

    def __init__(self, nodename):
        logger.debug('called for node %s' % nodename)
#         domainParts = reversed(nodename.split('.'))

        for factsPlugin in config.get('main', 'facts').split(','):
            logger.debug ('loading facts from %s' % factsPlugin)
            try:
                facts = driver.DriverManager(
                                             namespace='eu.ieo.puppet.facts',
                                             name=factsPlugin,
                                             invoke_on_load=True,
                                             invoke_args=([nodename]),
                                             )
            except (RuntimeError,), e:
                raise

            data = facts.driver.execute()
            for key in 'classes', 'parameters':
                if data.get(key):
                    if isinstance(data[key], list):
                        data[key] = dict.fromkeys(data[key])
                    self.data[key].update((k, v or {}) for k, v in data[key].iteritems())
#             self.data['environment'] =
            self.environment = data.get('environment', 'production')
#         logger.debug(self.data)
        if self.data.get('classes'):

            for _class in self.data['classes']:
                logger.debug('searching plugin for class %s ...' % _class)
                try:
                    plugin = driver.DriverManager(
                                                  namespace='eu.ieo.puppet.classes',
                                                  name=_class,
                                                  invoke_on_load=True,
                                                  invoke_args=(nodename, self.data),
                                                  )
                # driver not found
                except RuntimeError:
                    continue
                logger.debug('executing plugin %s ...' % plugin.driver)
                try:
                    classData, parameters = plugin.driver.execute()
                except Exception, e:
                    logger.warn('plugin %s failed - %s' % (plugin.driver, e))
                    continue
                self.data['classes'][_class].update(classData)
                self.data['parameters'].update(parameters)

    def __repr__(self):
        data = dict((k, dict(v)) for k, v in self.data.iteritems())
        data['environment'] = self.environment
        return yaml.dump(data,
                         default_flow_style=False,
                         explicit_start=True,
                         ).replace('null', '')


def main():
    enc = IeoEnc(sys.argv[1])
    print enc
