from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
import models, schemas, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="자격 증명을 확인할 수 없습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. 토큰 복호화 (암호 풀기)
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub") 
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
        
    # 2. DB에서 유저 찾기
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user

#default path
@app.get('/')
def home():
    return {"message" : "서버가 정상 작동중", "status" : "success"}

#sign_in api
@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 중복 유저 확인
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 아이디입니다."
        )
    
    # 비밀번호 암호화 및 저장
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, password=hashed_password)
    
    db.add(new_user)
    db.commit()
    
    return {"message": "회원가입 성공!", "username": user.username}

#log_in api
@app.post("/login", response_model=schemas.Token)
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.username).first()

    if not user or not auth.verify_password(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login Failed : Check your ID or PW",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

#create_memo
@app.post("/memos", response_model=schemas.Memo)
def create_memo(
    memo: schemas.MemoCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) 
):
    #login success
    new_memo = models.Memo(
        content=memo.content, 
        user_id=current_user.id  # 토큰에서 찾은 유저의 ID를 자동으로 넣음
    )
    
    db.add(new_memo)
    db.commit()
    db.refresh(new_memo) # DB에서 방금 저장된 따끈따끈한 데이터(ID 포함)를 다시 읽어옴
    
    return new_memo

#viewing memo
@app.get("/memos", response_model=list[schemas.Memo])
def read_memos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    memos = db.query(models.Memo)\
    .filter(models.Memo.user_id == current_user.id)\
    .offset(skip)\
    .limit(limit)\
    .all()

    return memos

#update_memo
@app.put("/memos/{memo_id}", response_model=schemas.Memo)
def update_memo(
    memo_id: int,
    memo_data: schemas.MemoCreate, #수정할 내용
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    memo = db.query(models.Memo).filter(models.Memo.id == memo_id).first()

    if memo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메모를 찾을 수 없음"
        )
    
    if memo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="본인 메모만 수정 가능"
        )
    
    memo.content = memo_data.content
    db.commit()
    db.refresh(memo)

    return memo

#delete memo
@app.delte("/memo/{memo_id}")
def delete_memo(
    memo_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    memo = db.query(models.Memo).filter(models.Memo.id == memo_id).first()

    if memo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메모를 찾을 수 없음"
        )

    if memo.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="본인의 메모만 삭제할 수 있음"
        )
    
    db.delete(memo)
    db.commit()

    return {"message" : "메모 삭제 완료"}

