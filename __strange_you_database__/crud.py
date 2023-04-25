from sqlalchemy.orm import Session
from __strange_you_database__ import models, schemas
from __strange_you_database__.database import SessionLocal
from fastapi import Depends, HTTPException
from typing import List


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_user(db: Session, user_student_number=str):  # 查询用户
    return db.query(models.User).filter(models.User.student_number == user_student_number).first()


def get_users(db: Session, skip=0, limit=0):  # 查询所有用户
    return db.query(models.User).offset(skip).limit(limit).all()


def get_users_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).all()


def create_user(db: Session, student_number, username, openid):  # 创建用户
    db_user = models.User(student_number=student_number, username=username, openid=openid)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_administrator(db: Session, administrator_student_number=int):  # 查询管理员表
    return db.query(models.Administrator).filter(
        models.Administrator.student_number == administrator_student_number).first()


def create_administrator(db: Session, student_number, administratorname, hashed_password):  # 创建管理员表
    db_administrator = models.Administrator(student_number=student_number,
                                            administratorname=administratorname,
                                            hashed_password=hashed_password)
    db.add(db_administrator)
    db.commit()
    db.refresh(db_administrator)
    return db_administrator


def get_sn(db: Session, sn=str):  # 查询序列号
    return db.query(models.Question).filter(
        models.Question.sn == sn).first()


def get_sns(db: Session, skip=0, limit=0):  # 查询所有序列号
    return db.query(models.Question).offset(skip).limit(limit).all()


def create_question(question, source, status, date, db: Session):  # 创建问题表
    db_question = models.Question(
        question=question,
        source=source,
        status=status,
        date=date
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


def get_reply(db: Session, db_id=int):  # 查询回复
    return db.query(models.Reply).filter(models.Reply.id == db_id).first()


def get_replies(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Reply).offset(skip).limit(limit).all()


def create_question_reply(db: Session, reply: schemas.ReplyCreate, question_id: str):
    db_item = models.Reply(**reply.dict(), question_id=question_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def delete_user(user_student_number=str, db=Depends(get_db)):  # 删除用户
    user = db.query(models.User).filter(models.User.student_number == user_student_number).first()
    if not user:
        raise HTTPException(detail="用户不存在,删除失败", status_code=400)
    db.delete(user)
    db.commit()
    return {"detail": "删除成功"}


def deleteUser(user_student_numbers: List[str], db=Depends(get_db)):  # 删除多个用户
    try:
        for user_student_number in user_student_numbers:
            users = db.query(models.User).filter(models.User.student_number == user_student_number).first()
            if users:
                db.delete(users)
                db.commit()
                db.close()
        return {"code": "0000", "message": "删除成功"}
    except ArithmeticError:
        return {"code": "0002", "message": "数据库错误"}


def get_sn_question(db: Session, question_sn: str):  # 查询问题
    return db.query(models.Question).filter(models.Question.question_sn == question_sn).first()


def get_source_question(db: Session, source: str):  # 查询问题
    return db.query(models.Question).filter(models.Question.source == source).all()


def get_questions(db: Session, skip, limit):  # 查询所有问题
    return db.query(models.Question).offset(skip).limit(limit).all()


def delete_question(sn=str, db=Depends(get_db)):  # 删除问题
    question = db.query(models.Question).filter(models.Question.sn == sn).first()
    if not question:
        raise HTTPException(detail="问题不存在,删除失败", status_code=400)
    db.delete(question)
    db.commit()
    return {"detail": "删除成功"}


def delete_reply(reply_id=int, db=Depends(get_db)):  # 删除回复
    content = db.query(models.Reply).filter(models.Reply.id == reply_id).first()
    if not content:
        raise HTTPException(detail="回复不存在,删除失败", status_code=400)
    db.delete(content)
    db.commit()
    return {"detail": "删除成功"}


def get_source_reply(db: Session, source: str):  # 通过来源查询回复
    return db.query(models.Reply).filter(models.Reply.source == source).all()


def get_question_sn_reply(db: Session, question_id: str):  # 通过问题序号查询回复
    return db.query(models.Reply).filter(models.Question.sn == question_id).all()


# 根据user_student_number修改user_name
def updateUser(user_student_number=str, user_name=str, db=Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.student_number == user_student_number).first()
        print(user)
        if user:
            models.User.name = user_name
            db.commit()
            db.close()
            return {"code": "0000", "message": "修改成功"}
        else:
            return {"code": "0001", "message": "学工号或昵称错误"}
    except ArithmeticError:
        return {"code": "0002", "message": "数据库错误"}


def updateQuestionStatus(status, question_sn: str, db: Session):  # 改问题表审核状态
    question_status = db.query(models.Reply).filter(models.Question.sn == question_sn).first()
    question_status.status = status
    db.commit()


def updateReplyStatus(status, reply_id: int, db: Session):  # 改回复表审核状态
    reply_status = db.query(models.Reply).filter(models.Reply.id == reply_id).first()
    reply_status.status = status
    db.commit()
