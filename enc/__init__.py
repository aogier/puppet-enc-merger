from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.sql.schema import Table, Column, ForeignKey
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Integer

from local import db_uri

engine = create_engine(db_uri)

Base = declarative_base()
Session = sessionmaker(bind=engine)

session = Session()