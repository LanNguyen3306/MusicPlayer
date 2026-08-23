import os
import uuid
import shutil
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from .. import models, schemas, config
from ..database import SessionLocal
from .users import get_current_user
from fastapi.responses import FileResponse, RedirectResponse
from typing import List, Optional
import requests

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


@router.get("/{song_id}/play")
def play_song(song_id: int, db: Session = Depends(get_db)):
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài hát")
    
    # 1. NẾU LÀ NHẠC TỪ API BÊN NGOÀI (EXTERNAL)
    if song.source_type == "external" and song.external_url:
        # Chuyển hướng trình duyệt thẳng tới link stream nhạc gốc
        return RedirectResponse(url=song.external_url)
        
    # 2. NẾU LÀ NHẠC TẢI LÊN (LOCAL)
    if not song.file_path or not os.path.exists(song.file_path):
        raise HTTPException(status_code=404, detail="Không tìm thấy file nhạc")
        
    return FileResponse(song.file_path, media_type="audio/mpeg")
    
@router.get("/", response_model=List[schemas.SongResponse])
def get_all_song(
    skip: int = 0, # skip bao nhieu bai
    limit: int = 100, # toi da bao nhieu bai tren 1 trang
    db: Session = Depends(get_db)
    ):
    songs = db.query(models.Song).offset(skip).limit(limit).all()
    
    return songs


# API THÊM/XÓA BÀI HÁT YÊU THÍCH (TOGGLE FAVORITE)
@router.post("/{song_id}/favorite")
def toggle_favorite(
    song_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) # Bắt buộc phải đăng nhập
):
    # 1. Tìm xem bài hát có tồn tại trong hệ thống không
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài hát")

    # 2. Kiểm tra xem bài hát đã có trong danh sách yêu thích của User chưa
    if song in current_user.favorites:
        # Nếu đã có -> Xóa khỏi danh sách (Bỏ tim)
        current_user.favorites.remove(song)
        db.commit()
        return {"message": "Đã bỏ yêu thích bài hát", "status": "unliked"}
    else:
        # Nếu chưa có -> Thêm vào danh sách (Thả tim)
        current_user.favorites.append(song)
        db.commit()
        return {"message": "Đã thêm vào danh sách yêu thích", "status": "liked"}
    

@router.post("/fetch-free-music")
def fetch_free_music(keyword: str = "lofi", db: Session = Depends(get_db)):
    """
    API gọi đến iTunes (Miễn phí, không cần Key). 
    Lấy về các bản stream chất lượng cao (bản nghe thử 30s của Apple Music).
    """
    url = f"https://itunes.apple.com/search?term={keyword}&media=music&limit=12"
    
    try:
        response = requests.get(url)
        data = response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail="Không thể kết nối đến máy chủ âm nhạc.")

    added_songs = []
    
    # Duyệt qua danh sách bài hát lấy được từ API
    for track in data.get("results", []):
        # Kiểm tra xem bài hát đã tồn tại trong DB chưa để tránh trùng lặp
        exists = db.query(models.Song).filter(models.Song.title == track.get("trackName")).first()
        
        if not exists and track.get("previewUrl"):
            new_song = models.Song(
                title=track.get("trackName"),
                artist=track.get("artistName"),
                source_type="external",           # Đánh dấu là nhạc lấy từ API ngoài
                external_url=track.get("previewUrl"), # Link stream .m4a/.mp3
                owner_id=1  # Gán cho một User ID bất kỳ (VD: Admin) để không bị lỗi ForeignKey
            )
            db.add(new_song)
            added_songs.append(new_song.title)
            
    db.commit()
    return {
        "message": f"Đã lấy và lưu thành công {len(added_songs)} bài hát từ từ khóa '{keyword}'!", 
        "songs": added_songs
    }