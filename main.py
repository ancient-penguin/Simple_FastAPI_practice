from fastapi import FastAPI
import models
from database import engine
from router import memos, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(memos.router)

#default path
@app.get('/')
def home():
    return {"message" : "서버가 정상 작동중", "status" : "success"}



