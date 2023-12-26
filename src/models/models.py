from datetime import datetime
from uuid import uuid4
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from src.db.db import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(125), nullable=False, unique=True)
    password = Column(String(125), nullable=False)
    files = relationship('File', backref='user', cascade='all, delete')
    created_at = Column(DateTime, index=True, default=datetime.utcnow)


class File(Base):
    __tablename__ = 'files'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE'))
    name = Column(String(125), nullable=False)
    path = Column(String(255), nullable=False, unique=True)
    size = Column(Integer, nullable=False)
    is_downloadable = Column(Boolean, default=False)
    created_at = Column(DateTime, index=True, default=datetime.utcnow)
