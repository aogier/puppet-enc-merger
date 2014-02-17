'''
Created on 17/feb/2014

@author: oggei
'''

import os
import ConfigParser
import pkg_resources
import shutil

config_path = os.path.join(os.environ.get('VIRTUAL_ENV', '/'), 'etc/ieo_enc', 'enc.cfg')

if not os.path.exists(config_path):
    template = pkg_resources.resource_filename('enc.config', 'files/enc.cfg')
    os.umask(0077)
    try:
        shutil.copyfile(template, config_path)
    except:
        pass

config = ConfigParser.SafeConfigParser()
config.read(['dev.cfg', config_path])
