from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.sql.schema import Table, Column, ForeignKey
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer
import uuid

from local import db_uri
from enc.plugins import EncPlugin

engine = create_engine(db_uri)

Base = declarative_base()
Session = sessionmaker(bind=engine)

session = Session()

calendars_uuid = uuid.UUID('9eef4d4b-7b49-4364-85fe-84337e81af86')
uriPrefix = 'https://calendars.ieo.eu/caldav.php/%s'

class CalendarPlugin(EncPlugin):
    
    __puppet_class__ = 'ieo::classes::calendar::client' 
    
    def __init__(self, nodename, data):
        self.nodename = nodename
        self.data = data

    def execute(self):
        #FIXME: remove
        def wrap(s):
            if not isinstance(s, str):
                s = str(s)
            return s.join(["'"]*2)
        
        user = self.data['parameters']['ieo_username']
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
        #FIXME: implement
        return {'calendars': out}, {}


    def getCalendars(self, user):
    
        # query calendar DB for User object whose username is :user:
        query = session.query(User).filter(User.username == user)
        # one() fail if len(result) != 1
        user = query.one()
        #              for every item in
        collections = [xx for xx in
        #              flattened array of group grants [[group1_grants], [group2_grants], ...]
                       reduce(lambda x,y: x+y,
                              [x.collections for x in user.principal.groups])
        #              if granted object is a Calendar
                       if isinstance(xx, Calendar)]
        #               for every item in
        collections += [x for x
        #               user + dav_user collections
                        in user.collections + user.principal.collections
        #               if granted object is a Calendar
                        if isinstance(x, Calendar)] 
        # return a set
        return set(collections)

# avoid circular dependencies
from enc.plugins.calendars.models import User, Calendar
        