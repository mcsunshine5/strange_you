from sqlalchemy import Column, ForeignKey, Integer, String, Date
from passlib.context import CryptContext
from sqlalchemy.orm import relationship

from __strange_you_database__.database import Base


class User(Base):  # 用户表
    __tablename__ = "users"
    student_number = Column(String(12), primary_key=True, index=True)  # 学工号
    username = Column(String(20))
    openid = Column(String(30))


class Administrator(Base):  # 管理员表
    __tablename__ = "administrator"
    id = Column(Integer, primary_key=True)
    student_number = Column(String(12), ForeignKey("users.student_number"), index=True)
    administratorname = Column(String(20))
    hashed_password = Column(String(200))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


class Question(Base):
    __tablename__ = "question"
    id = Column(Integer, primary_key=True, index=True)
    sn = Column(String(32), unique=True, nullable=False)
    status = Column(String(256), nullable=False)
    question = Column(String(1024), nullable=False)
    source = Column(String, nullable=False)
    date = Column(Date)

    replies = relationship("Reply", back_populates="question")


class Reply(Base):
    __tablename__ = "reply"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    replyname = Column(String(64), nullable=False)
    content = Column(String(1024), nullable=False)
    source = Column(String(32))
    status = Column(String(32), nullable=False)
    date = Column(Date)

    question_id = Column(String, ForeignKey("question.id"))
    question = relationship("Question", back_populates="replies")
