""" Database handler
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DB_SESSION = None
Base = declarative_base()


def get_session():
    return DB_SESSION


def init_db(app):
    """ todoc
    """
    global DB_SESSION
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    import auth.models

    engine = create_engine(app.config["DATABASE_URI"])
    DB_SESSION = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    Base.query = DB_SESSION.query_property()
    Base.metadata.create_all(bind=engine)
