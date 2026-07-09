import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

app = FastAPI(title="TransGo API Backend")

# 1. SETUP CORS (Supaya nanti bisa ditembak/diakses oleh CodeIgniter 4)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Mengizinkan semua domain mengakses API ini
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. KONFIGURASI DATABASE PINTAR (Menyatu di main.py)
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Jika di Railway, ubah driver bawaan mysql:// menjadi mysql+pymysql://
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Jika di laptop kamu (XAMPP lokal)
    SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/transgo_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency untuk mendapatkan session database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. ROUTE/ENDPOINT TESTING
@app.get("/")
def root():
    return {"message": "Welcome to TransGo Backend API is Running Online!"}

@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        # Mencoba melakukan query ringan ke database untuk tes koneksi
        db.execute(text("SELECT 1"))
        return {"status": "connected", "message": "Sukses terhubung ke Database MySQL!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
