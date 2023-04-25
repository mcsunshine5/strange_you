from starlette.middleware.cors import CORSMiddleware

from app import infront, background
from fastapi import FastAPI
from mongoengine import *

connect("test", host='localhost', port=27017)
app = FastAPI()
app.include_router(background.router)  #
app.include_router(infront.router)
# 设置允许跨域请求的来源、方法和头部信息
origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)