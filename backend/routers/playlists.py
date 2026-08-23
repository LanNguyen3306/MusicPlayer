from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from .. import models, schemas
from ..database import SessionLocal
from .users import get_current_user

router = APIRouter(prefix="/playlists", tags=["Playlist"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@router.post("/", response_model = schemas.PlaylistResponse)
def create_playlist(
    playlist: schemas.PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_playlists = models.Playlist(
        name = playlist.name,
        description = playlist.description,
        owner_id = current_user.id
    )
    
    db.add(new_playlists)
    db.commit()
    db.refresh(new_playlists)
    
@router.get("/me", response_model=List[schemas.PlaylistResponse])
def get_my_playlists(
    db:Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    playlists = db.query(models.Playlist).filter(models.Playlist.owner_id == current_user.id).all()
    return playlists

@router.post("/{playlist_id}/toggle-song/{song_id}")
def toggle_song_in_playlist(
    playlist_id: int,
    song_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Tìm Playlist (phải đảm bảo là playlist của chính user này tạo)
    playlist = db.query(models.Playlist).filter(
        models.Playlist.id == playlist_id, 
        models.Playlist.owner_id == current_user.id
    ).first()
    
    if not playlist:
        raise HTTPException(status_code=404, detail="Không tìm thấy Playlist hoặc bạn không có quyền.")

    # 2. Tìm Bài hát
    song = db.query(models.Song).filter(models.Song.id == song_id).first()
    if not song:
        raise HTTPException(status_code=404, detail="Không tìm thấy bài hát.")

    # 3. Logic Toggle (Thêm hoặc Xóa)
    if song in playlist.songs:
        playlist.songs.remove(song)
        db.commit()
        return {"message": f"Đã xóa bài hát '{song.title}' khỏi Playlist '{playlist.name}'"}
    else:
        playlist.songs.append(song)
        db.commit()
        return {"message": f"Đã thêm bài hát '{song.title}' vào Playlist '{playlist.name}'"}