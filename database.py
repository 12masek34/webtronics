import os
from typing import Iterator

from sqlalchemy import (
    Text,
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    MetaData,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, backref, relationship, sessionmaker
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_PORT = os.getenv('DB_PORT')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')


Base = declarative_base()
engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')
meta = MetaData(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db() -> Iterator[Session]:
    """
    Create db session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_db():
    """
    Create db.
    """
    Base.metadata.create_all(engine)
    # Base.metadata.drop_all(engine)


class User(Base):
    """
    Simple user model.
    """
    __tablename__ = 'user_'
    id = Column(Integer(), primary_key=True)
    username = Column(String(128), nullable=False)
    hashed_password = Column(String(128), nullable=False)
    posts = relationship('Post', backref='author')
    __table_args__ = (UniqueConstraint('username', name='name__uc'),)


class Post(Base):
    """
    Post model.
    """
    __tablename__ = 'post'
    id = Column(Integer(), primary_key=True)
    author_id = Column(Integer, ForeignKey('user_.id'))
    text = Column(Text)
