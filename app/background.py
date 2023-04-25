from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm

from __strange_you_database__ import crud, authentication, utils, schemas
from fastapi import Depends, HTTPException
from requests import Session
from __strange_you_database__.database import SessionLocal
from fastapi import APIRouter

from __strange_you_database__.utils import create_access_token

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login/")
def login(user: schemas.LoginModel, db: Session = Depends(get_db)):
    counterfoil = authentication.get_counterfoil(user.username, user.password)
    if counterfoil == "学号不存在或密码错误":
        raise HTTPException(status_code=400, detail="Incorrect password or student number")
    ticket = authentication.get_ticket(counterfoil)
    data = authentication.get_info(ticket)
    openid = utils.get_wx(user.code)
    user_dict = {"student_number": data["student_number"], "name": data["name"], "openid": openid}
    db_user = crud.create_user(db, data["student_number"], data["name"], openid)
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_DAYS)
    # 把id进行username加密，要使用str类型
    access_token = create_access_token(data={"sub": data["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "data": data}


@router.get("/Questions")  # 查询所有问题
def get_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    questions = crud.get_questions(db, skip=skip, limit=limit)
    return questions


@router.delete("/question/")  # 删除问题
def delete_question(question_sn: int, db: Session = Depends(get_db)):
    question = crud.delete_question(question_sn, db)
    return question


@router.get("/Replies")  # 查询所有回复
def get_replies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    replies = crud.get_replies(db, skip=skip, limit=limit)
    return replies


@router.delete("/Reply/")  # 删除回复
def delete_reply(reply_id: int, db: Session = Depends(get_db)):
    reply = crud.delete_reply(reply_id, db)
    return reply


@router.get("/sns/")  # 查询所有序列号
def get_sns(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sns = crud.get_sns(db, skip=skip, limit=limit)
    return sns


@router.get("/users/")  # 查询所有用户
def read_user(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@router.delete("/user/")  # 删除用户
def delete_user(user_student_number: str, db: Session = Depends(get_db)):
    user = crud.delete_user(user_student_number, db)
    return user


@router.put("/question_status/")  # 改问题状态
def updateQuestionStatus(status, question_sn: int, db: Session = Depends(get_db)):
    question_status = crud.updateQuestionStatus(status, question_sn, db)
    return question_status


@router.put("/reply_status/")  # 改回复状态
def updateReplyStatus(status, reply_id: int, db=Depends(get_db)):
    reply_status = crud.updateReplyStatus(status, reply_id, db)
    return reply_status
