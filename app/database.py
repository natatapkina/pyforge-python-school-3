from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'postgresql+psycopg://user:password@postgres/postgres'

# an Engine, which the Session will use for connection
# resources, typically in module scope
engine = create_engine(DATABASE_URL)

# a sessionmaker(), also in the same scope as the engine
Session = sessionmaker(engine)

Base = declarative_base()
