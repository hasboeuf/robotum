from sqlalchemy import Column, Integer, String, Boolean
from auth.database import Base, get_session


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(120))
    admin = Column(Boolean)

    def add(self):
        get_session().add(self)
        try:
            get_session().commit()
        except Exception as error:
            get_session().rollback()
            raise error

    def delete(self):
        get_session().delete(self)
        try:
            get_session().commit()
        except Exception as error:
            get_session().rollback()
            raise error

    @staticmethod
    def delete_all():
        get_session().query(User).delete()
        try:
            get_session().commit()
        except Exception as error:
            get_session().rollback()
            raise error

    @staticmethod
    def get(username):
        return get_session().query(User).filter_by(username=username).first()

    def __init__(self, username=None, password=None, admin=None):
        self.username = username
        self.password = password
        self.admin = admin

    def __repr__(self):
        return "<User %r admin:%s>" % (self.username, self.admin)
