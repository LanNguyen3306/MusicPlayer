from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from typing import Optional, List

class SongBase(BaseModel):
    title: str
    artist: str
    source_type: str = "local"                
    external_url: Optional[str] = None

class SongCreate(SongBase):
    pass # Khi user thêm bài hát mới, họ chỉ cần gửi title và artist

class SongResponse(SongBase):
    id: int
    file_path: Optional[str] = None
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True # Giúp chuyển đổi dữ liệu từ SQLAlchemy sang JSON dễ dàng

class UserCreate(BaseModel):
    username: str
    email: str
    password: str # Nhận mật khẩu thô từ người dùng khi đăng ký

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    songs: List[SongResponse] = [] 

    class Config:
        from_attributes = True
        # Quan trọng: Không khai báo 'password' ở đây để bảo mật thông tin khi trả về Frontend!
        

# --- SCHEMAS CHO PLAYLIST ---
class PlaylistBase(BaseModel):
    name: str

class PlaylistCreate(PlaylistBase):
    description: Optional[str] = None

class PlaylistResponse(PlaylistBase):
    id: int
    created_at: datetime
    description: Optional[str] = None
    owner_id: int
    songs: List[SongResponse] = [] # Trả về luôn danh sách bài hát trong playlist này

    class Config:
        from_attributes = True

# --- SCHEMAS CHO LỊCH SỬ NGHE NHẠC ---
class HistoryResponse(BaseModel):
    id: int
    played_at: datetime
    song: SongResponse # Trả về luôn thông tin chi tiết bài hát đã nghe

    class Config:
        from_attributes = True
        
# --- SCHEMAS CHO TOKEN ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    
# --- SCHEMAS CHO QUÊN MẬT KHẨU ---
class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    email: str
    otp: str
    new_password: str