#메모 관련 기능
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import schemas, models
from dependencies import get_db, get_current_user 

# prefix="/memos"를 설정하면 아래 주소들에 자동으로 /memos가 붙음
router = APIRouter(
    prefix="/memos",
    tags=["memos"]
)

#create_memo
@router.post("/", response_model=schemas.Memo)
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
    db.refresh(new_memo) # DB에서 방금 저장된 데이터다시 읽어옴
    
    return new_memo

#viewing memo
@router.get("/", response_model=list[schemas.Memo])
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
@router.put("/{memo_id}", response_model=schemas.Memo)
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
@router.delete("/{memo_id}")
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