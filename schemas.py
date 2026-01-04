from pydantic import BaseModel
from typing import List, Optional

#Base Structure
class MemoBase(BaseModel):
    content : str

class UserBase(BaseModel):
    username : str

#Create Schema
class MemoCreate(MemoBase):
    pass

class UserCreate(UserBase):
    password : str

#Response Schema
class Memo(MemoBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True