from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from .. import models, schemas, utils
from ..database import SessionLocal

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/register", response_model=schemas.UserResponse)
def register_user(user: schemas.UserCreate, db:Session=Depends(get_db)):
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) |
        (models.User.email == user.email).first()
    )
    
    if db.user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập hoặc Email đã được sử dụng"
        )
        
    hashed_pw = utils.get_password_hash(user.password)
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        hash_password=hashed_pw
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    
    if not user or not utils.verify_password(form_data.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tài khoản hoặc mật khẩu không chính xác",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = utils.create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}