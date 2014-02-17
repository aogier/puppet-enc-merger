'''
Created on 17/feb/2014

@author: oggei
'''

import os
import ConfigParser
import pkg_resources
import shutil
import sys

from enc import logger

log = logger.getChild('config')

try:
    getattr(sys, 'real_prefix')
    prefix = sys.prefix
except:
    prefix = '/'

configFile = 'enc.cfg'

config_path = os.path.join(prefix, 'etc/ieo_enc')
config_file = os.path.join(config_path, 'enc.cfg')

if not os.path.exists(config_file):
    if not os.path.exists(config_path):
        log.info('create config directories:  %s' % config_path)
        os.makedirs(config_path)
    template = pkg_resources.resource_filename('enc.config', 'files/enc.cfg')  # @UndefinedVariable
    os.umask(0077)
    try:
        log.info('creating empty config in %s' % config_path)
        shutil.copyfile(template, config_file)
    except:
        pass

config = ConfigParser.SafeConfigParser()
config.read([config_file, 'dev.cfg'])
