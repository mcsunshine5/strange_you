import datetime

from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    openid: str
    student_number: str = Field(..., example="20220001")
    username: str = Field(..., example="小明")

    class Config:
        orm_mode = True


class UserCreate(UserSchema):
    pass


class UserUpdate(UserSchema):
    pass


class AdministratorSchema(BaseModel):
    id: int = Field(..., example=1)
    student_number: str = Field(..., example="20220001")
    administratorname: str = Field(..., example="管理员")
    hashed_password: str = Field(..., example="password_hash")

    class Config:
        orm_mode = True


class AdministratorCreate(AdministratorSchema):
    pass


class QuestionSchema(BaseModel):
    sn: int = Field(..., example="1")
    question: str = Field(..., example="这是一个问题吗？")
    source: str = Field(..., example="20220001")
    status: str = Field(..., example="待审批")
    date: datetime.date = Field(..., example="2023-04-21")

    class Config:
        orm_mode = True


class QuestionCreate(QuestionSchema):
    pass


class QuestionUpdate(QuestionCreate):
    pass


class ReplySchema(BaseModel):
    id: int = Field(..., example="1")
    replyname: str = Field(..., example="小红")
    content: str = Field(..., example="这是一个回复")
    source: str = Field(..., example="20220002")
    status: str = Field(..., example="待审批")
    date: datetime.date = Field(..., example="2023-04-22")

    class Config:
        orm_mode = True


class ReplyCreate(ReplySchema):
    pass


class ReplyUpdate(ReplySchema):
    pass


class TokenModel(BaseModel):
    token: str = None


class LoginModel(BaseModel):
    username: str = None
    password: str = None
    code: str = None
