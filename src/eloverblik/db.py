from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, configure_mappers
from sqlalchemy.ext.declarative import declarative_base

from eloverblik.settings import DATABASE_URI, SQL_ALCHEMY_SETTINGS


ModelBase = declarative_base()


if DATABASE_URI:
    engine = create_engine(DATABASE_URI, **SQL_ALCHEMY_SETTINGS)
    configure_mappers()
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    Session = scoped_session(factory)
else:
    from sqlalchemy.orm import Session


def make_session(*args, **kwargs):
    """
    Create a new SQLAlchemy session.

    :rtype: sqlalchemy.orm.Session
    """
    return Session(*args, **kwargs)


def inject_session(func):
    """
    Function decorator which injects a "session" named parameter
    if it doesn't already exists
    """
    def session_wrapper(*args, **kwargs):
        _session = kwargs.setdefault('session', make_session())
        try:
            return func(*args, **kwargs)
        finally:
            _session.close()

    return session_wrapper


def atomic(func):
    """
    Function decorator which injects a "session" named parameter
    if it doesn't already exists, and wraps the function in an
    atomic transaction.
    """
    @inject_session
    def atomic_wrapper(*args, **kwargs):
        session = kwargs['session']
        try:
            return_value = func(*args, **kwargs)
        except:
            session.rollback()
            raise
        else:
            session.commit()
            return return_value

    return atomic_wrapper
