'''
Created on 17/feb/2014

@author: oggei
'''

import os
import ConfigParser

config_path = os.path.join(os.environ.get('VIRTUAL_ENV', '/'), 'etc/ieo_enc', 'enc.cfg')

config = ConfigParser.SafeConfigParser()
config.read(['dev.cfg', config_path])
