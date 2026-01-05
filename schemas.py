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

class User(UserBase):
    id: int
    memos: List[Memo]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None