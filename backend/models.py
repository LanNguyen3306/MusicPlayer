from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

user_favourites = Table(
    "user_favourites",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True)
)

playlist_songs = Table(
    "playlist_songs",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlists.id"), primary_key=True),
    Column("song_id", Integer, ForeignKey("songs.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique = True, index=True)
    email = Column(String, unique=True, index=True)
    hash_password = Column(String)
    is_active = Column(Boolean, default=True)

    # thuộc tính ảo, giúp gọi user1.songs
    songs = relationship("Song", back_populates="owner")


class Song(Base):
    __tablename__ = "songs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    
    file_path = Column(String, nullable=True)       # Cho phép để trống (None) nếu là nhạc ngoài
    source_type = Column(String, default="local")   # Nhận 2 giá trị: "local" hoặc "external"
    external_url = Column(String, nullable=True)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="songs")
    
class Playlist(Base):
    __tablename__="playlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at=Column(DateTime, default=datetime.utcnow)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="playlists")
    
    songs = relationship("Song", secondary=playlist_songs, backref="playlists")
    
class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    song_id = Column(Integer, ForeignKey("songs.id"))
    played_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="histories")
    song = relationship("Song")