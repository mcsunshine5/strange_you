from datetime import date
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import FastAPI, HTTPException, APIRouter, Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status
from __strange_you_database__ import authentication
from __strange_you_database__ import crud
from __strange_you_database__ import models
from __strange_you_database__ import schemas
from __strange_you_database__ import utils
from __strange_you_database__.database import SessionLocal, engine
from __strange_you_database__.utils import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS

app = FastAPI
router = APIRouter(

    prefix="/infront",

    tags=["infront"],

    responses={404: {"description": "Not found"}},

)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
models.Base.metadata.create_all(bind=engine)
security = HTTPBearer()
oauth2_scheme_1 = OAuth2PasswordBearer(tokenUrl="/frontpage/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """

    :param data: 需要进行JWT令牌加密的数据（解密的时候会用到）
    :param expires_delta: 令牌有效期
    :return: token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    # 添加失效时间
    to_encode.update({"exp": expire})
    # SECRET_KEY：密钥
    # ALGORITHM：JWT令牌签名算法
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # 从请求头中获取 JWT 访问令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 解密后的数据应包含失效时间字段 exp
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_DAYS)
        # 校验令牌是否已过期
        expire = datetime.fromisoformat(payload["exp"])
        if expire - datetime.utcnow() < token_expires:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    # 返回用户名，即当前登录用户
    return username


@router.get("/protected/")
async def protected_route(current_user: str = Depends(get_current_user)):
    return {"current_user": current_user}


# 登录注册接口
@router.post("/login/")
def login(user: schemas.LoginModel, db: Session = Depends(get_db)):
    counterfoil = authentication.get_counterfoil(user.username, user.password)
    if counterfoil == "学号不存在或密码错误":
        raise HTTPException(status_code=400, detail="Incorrect password or student number")
    ticket = authentication.get_ticket(counterfoil)
    data = authentication.get_info(ticket)
    openid = utils.get_wx(user.code)
    user_dict = {"student_number": data["student_number"], "username": data["name"], "openid": openid}
    db_user = crud.create_user(db, user_dict, username=data["name"], openid=openid)
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={"sub": data["username"]}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "data": data, "db_user": db_user}


# # 通过student_number查询用户
@router.get("/user/{student_number}")
def read_user(student_number: str, db: Session = Depends(get_db)):
    user = crud.get_user(db=db, user_student_number=student_number)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# 分页查询用户
@router.get("/users/all", response_model=List[schemas.UserSchema])
def read_users(skip: int = 0, limit: int = 100,
               db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# 创建用户
@router.post("/user/")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.create_user(db=db, username=user.username, student_number=user.student_number, openid=user.openid)
    return db_user


# # 删除用户
@router.delete("/user/{student_number}")
def user_delete(student_number: str, db: Session = Depends(get_db)):
    return crud.delete_user(user_student_number=student_number, db=db)


# 删除多个用户
@router.delete("/users/")
def delete_users(user_student_numbers: List[str],
                 db: Session = Depends(get_db)):
    return crud.deleteUser(user_student_numbers=user_student_numbers, db=db)


# 根据学工号修改用户昵称
@router.put("/user/")
def update_user(user_student_number: str, user_name: str,
                db: Session = Depends(get_db)):
    return crud.updateUser(user_student_number=user_student_number, user_name=user_name, db=db)


# 通过序号查询问题
@router.get("/question/{sn}")
def read_question(sn: str, db: Session = Depends(get_db)):
    question = crud.get_sn(db=db, sn=sn)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


#
# #分页查询问题
@router.get("/questions/all", response_model=List[schemas.QuestionSchema])
def read_questions(skip: int = 0, limit: int = 100,
                   db: Session = Depends(get_db)):
    questions = crud.get_sns(db, skip=skip, limit=limit)
    return questions


# 通过来源查询问题
@router.get("/question/{source}")
def read_source_question(source: str, db: Session = Depends(get_db)):
    questions = crud.get_source_question(db=db, source=source)
    if questions is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return questions


# # 创建问题
@router.post("/question/")
def create_question(question: schemas.QuestionCreate,
                    db: Session = Depends(get_db)):
    db_question = crud.create_question(db=db, question=question.question, source=question.source, status="待审批",
                                       date=date.today())
    return db_question


# # 删除问题
@router.delete("/question/{question}")
def question_delete(sn: str, db: Session = Depends(get_db)):
    return crud.delete_question(sn=sn, db=db)


# # 查询回复
@router.get("/reply/{id}")
def read_reply(db_id, db: Session = Depends(get_db)):
    reply = crud.get_reply(db=db, db_id=db_id)
    if reply is None:
        raise HTTPException(status_code=404, detail="Reply not found")
    return reply


# 分页查询回复
@router.get("/replies/all", response_model=List[schemas.ReplySchema])
def read_replies(skip: int = 0, limit: int = 100,
                 db: Session = Depends(get_db)):
    replies = crud.get_replies(db, skip=skip, limit=limit)
    return replies


@router.get("/reply/{sn}")
def read_reply(question_id: str, db: Session = Depends(get_db)):
    reply = crud.get_question_sn_reply(db=db, question_id=question_id)
    if reply is None:
        raise HTTPException(status_code=404, detail="Reply not found")
    return reply


# 通过来源查询回复
@router.post("/question/{sn}/reply", response_model=schemas.ReplySchema)
def create_question_reply(sn: str, reply: schemas.ReplyCreate,
                          db: Session = Depends(get_db)):
    # 创建新回答
    db_reply = models.Reply(**reply.dict(), question_id=sn)
    db.add(db_reply)
    db.commit()
    db.refresh(db_reply)
    return db_reply


# 删除回复
@router.delete("/reply/{content}")
def reply_delete(reply_id: int, db: Session = Depends(get_db)):
    return crud.delete_reply(reply_id=reply_id, db=db)
