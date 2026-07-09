import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Mengambil URL database dari environment variable Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Railway memberikan awalan mysql://, kita ubah menjadi mysql+pymysql:// agar SQLAlchemy tidak error
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # 2. URL default jika dijalankan di localhost laptop (XAMPP)
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/transgo_db"

# Buat engine koneksi
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True,  # Memastikan koneksi database yang terputus otomatis tersambung kembali
    pool_recycle=3600    # Merefresh koneksi setiap 1 jam agar tidak kena timeout di cloud
)

# Buat session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class untuk model database
Base = declarative_base()

# Fungsi dependency injection untuk mengambil session DB di router FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
