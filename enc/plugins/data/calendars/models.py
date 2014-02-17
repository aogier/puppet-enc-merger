'''
Created on 13/feb/2014

@author: oggei
'''

from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import Table, Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer

# from local import db_uri
from enc import config
db_uri = config.get('ieo::classes::calendar::client', 'db_uri')

# from enc.plugins.data.calendars import Base, engine
engine = create_engine(db_uri)


Base = declarative_base()
Session = sessionmaker(bind=engine)

session = Session()

# many to many association tables
grants_table = Table('grants', Base.metadata,
                     Column('to_principal',
                            Integer,
                            ForeignKey('principal.principal_id')),
                     Column('by_collection',
                            Integer,
                            ForeignKey('collection.collection_id')),
                     )

group_member_table = Table('group_member', Base.metadata,
                           Column('group_id',
                                  Integer,
                                  ForeignKey('principal.principal_id'),
                                  primary_key=True),
                           Column('member_id',
                                  Integer,
                                  ForeignKey('principal.principal_id'),
                                  primary_key=True),
                           )

class Principal(Base):
    __tablename__ = 'principal'
    __table_args__ = {'autoload': True, 'autoload_with': engine}
    __mapper_args__ = {
                       'polymorphic_identity':'principal',
                       'polymorphic_on':'type_id'
                       }
    user_no = Column(Integer, ForeignKey('usr.user_no'))
    user = relationship('User', backref=backref('principal', uselist=False))
    collections = relationship('Collection',
                               secondary=grants_table,
                               backref='granted_users')
    principal_id = Column(Integer, primary_key=True)

    @property
    def members(self):
        return self
#         raise Exception, 'unimplemented'


class User(Base):
    __tablename__ = 'usr'
    __table_args__ = {'autoload': True, 'autoload_with': engine}
    collections = relationship('Collection',
                               backref=backref('owner', uselist=False))

class PrincipalType(Base):
    __table__ = Table('principal_type',
                      Base.metadata,
                      autoload=True, autoload_with=engine)

class Person(Principal):
    __mapper_args__ = {
                       'polymorphic_identity':1,
                       }

class Resource(Principal):
    __mapper_args__ = {
                       'polymorphic_identity':2,
                       }

class Group(Principal):
    __mapper_args__ = {
                       'polymorphic_identity':3,
                       }
    members = relationship('Principal', secondary=group_member_table,
                           primaryjoin=group_member_table.c.group_id == Principal.principal_id,
                           secondaryjoin=group_member_table.c.member_id == Principal.principal_id,
                           backref='groups')

class Collection(Base):
    __table__ = Table('collection', Base.metadata, autoload=True, autoload_with=engine)
    __mapper_args__ = {
                   'polymorphic_identity':'collection',
                   'polymorphic_on':'is_calendar'
                   }

class Calendar(Collection):
    __mapper_args__ = {
                   'polymorphic_identity': True,
                   }

class AddressBook(Collection):
    __mapper_args__ = {
                   'polymorphic_identity': False,
                   }

