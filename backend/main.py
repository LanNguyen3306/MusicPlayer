from fastapi import FastAPI
from .database import engine, Base
# Import models để SQLAlchemy biết các bảng cần tạo
from . import models 
from .routers import users, songs

app = FastAPI(
    title="Music Player API",
    description="API cho website nghe nhạc trực tuyến",
    version="1.0.0"
)

# 2. Tạo các bảng trong Cơ sở dữ liệu SQLite
# Lệnh này sẽ tự động tìm file models.py và tạo bảng users, songs nếu chúng chưa tồn tại
models.Base.metadata.create_all(bind=engine)
app.include_router(users.router)
app.include_router(songs.router)

# 3. Tạo một API endpoint cơ bản để kiểm tra server
@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với Backend của hệ thống Music Player!"}