from sqlalchemy import Column, Integer, String, Date, Sequence
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False, unique=True)
    phonenumber = Column(String(13), nullable=False)
    birthdate = Column(Date, nullable=True)
    additional_info = Column(String(300), nullable=True, default="No have data")



