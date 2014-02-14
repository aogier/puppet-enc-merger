from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.sql.schema import Table, Column, ForeignKey
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from local import db_uri
import uuid

engine = create_engine(db_uri)

Base = declarative_base()
Session = sessionmaker(bind=engine)

session = Session()

calendars_uuid = uuid.UUID('9eef4d4b-7b49-4364-85fe-84337e81af86')
uriPrefix = 'https://calendars.ieo.eu/caldav.php/%s'

from enc import plugins

class CalendarPlugin(object):
    
    __puppet_class__ = 'ieo::classes::calendar::client' 
    
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
            plugins.append(_type)
            return _type
    
    def __init__(self, nodename, data):
        self.nodename = nodename
        self.data = data

    def execute(self):
        
        user = self.data['parameters']['ieo_username']
        
        def wrap(s):
            if not isinstance(s, str):
                s = str(s)
            return s.join(["'"]*2)
        
        collections = self.getCalendars(user)
        
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
        
        return {'calendars': out}, None


    def getCalendars(self, user):
    
        user = session.query(User).filter(User.username == user).one()
        collections = [xx for xx in
                       reduce(lambda x,y: x+y,
                              [x.collections for x in user.principal.groups])
                       if isinstance(xx, Calendar)]
        collections += [x for x 
                        in user.collections + user.principal.collections 
                        if isinstance(x, Calendar)] 
        return set(collections)

from enc.calendars.models import User, Calendar        