# backend/config.py

# ==========================================
# CẤU HÌNH BẢO MẬT (JWT TOKEN)
# ==========================================
SECRET_KEY = "mot_chuoi_bi_mat_rat_dai_va_kho_doan_cho_music_player"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # Token sống trong 7 ngày

# ==========================================
# CẤU HÌNH GỬI EMAIL (OTP)
# ==========================================
SENDER_EMAIL = "email_he_thong_cua_ban@gmail.com" 
SENDER_PASSWORD = "mat_khau_ung_dung_16_ky_tu" 
OTP_EXPIRE_MINUTES = 10  # Thời gian sống của mã OTP (phút)

# ==========================================
# CẤU HÌNH DATABASE & ĐƯỜNG DẪN
# ==========================================
DATABASE_URL = "sqlite:///./storage/database.db"
MUSIC_STORAGE_DIR = "storage/music" # Dành cho tính năng Upload nhạc sắp tới