'''
Created on 13/feb/2014

@author: oggei
'''
from enc import session
from enc.models import User, Calendar
import uuid
import yaml

calendars_uuid = uuid.UUID('9eef4d4b-7b49-4364-85fe-84337e81af86')
hiera_root = 'ieo::classes::calendar::client::calendars'

def getCalendars(user):
    
    user = session.query(User).filter(User.username == user).one()
    collections = [xx for xx in
                   reduce(lambda x,y: x+y,
                          [x.collections for x in user.principal.groups])
                   if isinstance(xx, Calendar)]
    collections += [x for x 
                    in user.collections + user.principal.collections 
                    if isinstance(x, Calendar)] 
    return set(collections)

uriPrefix = 'https://calendars.ieo.eu/caldav.php/%s'

def getThunderbirdConfig(user):
    
    def wrap(s):
        if not isinstance(s, str):
            s = str(s)
        return s.join(["'"]*2)
    
    collections = getCalendars(user)
    
    defaults = ((
                ('calendar-main-in-composite', True),
                ('cache-enabled', False),
                ('type', wrap('caldav')),
                ))
    out = {}
    for collection in collections:
        parm = dict(defaults)
        parm.update({'name': wrap(collection.dav_displayname or collection.dav_name),
                     'uri': wrap(uriPrefix % collection.dav_name)
                        })
        out[wrap(uuid.uuid5(calendars_uuid,
                       str(collection.dav_name)))] = parm
    
    return out
