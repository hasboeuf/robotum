from sqlalchemy import Column, Integer, String, Boolean
from auth.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password = Column(String(120))
    admin = Column(Boolean)

    def __init__(self, username=None, password=None, admin=None):
        self.username = username
        self.password = password
        self.admin = admin

    def __repr__(self):
        return "<User %r admin:%s>" % (self.username, self.admin)
