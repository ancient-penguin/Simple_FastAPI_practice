from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(120), unique=True, nullable=False)
    password = Column(String(120), nullable=False)

    memos = relationship("Memo", back_populates="author")

class Memo(Base):
    __tablename__ = "name"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)

    #외래키
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    #관계 설정
    author = relationship("User", back_populates="memos")