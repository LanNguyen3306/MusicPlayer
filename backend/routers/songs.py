import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from .. import models, schemas, config
from ..database import SessionLocal
from .users import get_current_user

router = APIRouter(
    prefix="/songs",
    tags=["Songs"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: 
        db.close()
        
@router.post("/upload", response_model=schemas.SongResponse)
def upload_song(
    title: str = Form(...),
    artist: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ file nhạc định dạng .mp3")
    
    os.makedirs(config.MUSIC_STORAGE_DIR, exist_ok = True)
    
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(config.MUSIC_STORAGE_DIR, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, details="Lỗi khi lưu file: {str(e)}")
    
    new_song = models.Song(
        title=title, 
        artist=artist,
        file_path=file_path,
        source_type="local",
        owner_id=current_user.id 
    
    )
    
    db.add(new_song)
    db.commit()
    db.refresh(new_song)
    
    return new_song