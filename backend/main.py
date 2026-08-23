from fastapi import FastAPI
from .database import engine, Base, SessionLocal
# Import models để SQLAlchemy biết các bảng cần tạo
from . import models 
from .routers import users, songs, playlists
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo DB Session
    db = SessionLocal()
    try:
        # Kiểm tra xem Database có bài hát nào chưa?
        song_count = db.query(models.Song).count()
        if song_count == 0:
            print("Đang tải dữ liệu nhạc khởi tạo từ iTunes...")
            # Nếu chưa có bài nào, tự động gọi API lấy nhạc (Ví dụ: Từ khóa "lofi")
            # Tạo một user admin ảo để đứng tên bài hát (tránh lỗi khóa ngoại)
            admin_user = models.User(username="admin", email="admin@system.com", hash_password="admin")
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)

            # Khéo léo tái sử dụng hàm fetch_free_music đã viết
            songs.fetch_free_music(keyword="vietnam", db=db) 
            print("Tải nhạc khởi tạo thành công!")
    finally:
        db.close()
    yield

app = FastAPI(
    title="Music Player API",
    description="API cho website nghe nhạc trực tuyến",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(songs.router)
app.include_router(playlists.router)

# 3. Tạo một API endpoint cơ bản để kiểm tra server
@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với Backend của hệ thống Music Player!"}