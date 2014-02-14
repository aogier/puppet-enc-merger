#!/home/oggei/dev/virtualenvs/py2.7-enc/bin/python
'''
Created on 12/feb/2014

@author: oggei
'''

from enc.calendars import session
from enc.calendars.models import Principal
import sys
import yaml
from itertools import repeat
from enc.calendars.tools import getThunderbirdConfig

data = {'classes': 
        {'cluster.bioinfo.ieo.eu': [('ieo::classes::node', None),
                                      ('ieo::classes::calendar::client',
                                       {'calendars': getThunderbirdConfig('aparolin'),
                                        'prefix': '/tmp'}),
                                      ]}
        }

def enc(nodename):
    out = {'classes': dict(data['classes'][nodename]),
           'parameters': {'ciao': 'messaggio da ciao'}}
    return yaml.dump(out,
                     default_flow_style=False, 
                     explicit_start=True,
                 ).replace('null', '')

if __name__ == '__main__':

    nodename = 'cluster.bioinfo.ieo.eu'
    
#     print enc(nodename)
    print yaml.dump({'classes': None}, default_flow_style=False, explicit_start=True,).replace('null', '')
