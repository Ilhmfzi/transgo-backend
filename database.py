import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Ambil URL Database dari environment Railway
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Ubah mysql:// bawaan Railway menjadi mysql+pymysql://
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Ini HANYA berjalan kalau kamu di laptop (XAMPP lokal)
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/transgo_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
