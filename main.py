from fastapi import FastAPI, Query, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

# Import konfigurasi database kita
import models
from database import engine, get_db

# Otomatis membuat tabel di MySQL jika tabelnya belum ada
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="TRANSGO API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schema Pydantic untuk validasi inputan dari CI4 saat register
class UserRegister(BaseModel):
    nama: str
    email: EmailStr
    password: str
    role: str

# Schema untuk validasi inputan saat login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema untuk validasi inputan order baru
class OrderCreate(BaseModel):
    user_id: int
    kota_asal: str
    kota_tujuan: str
    berat: float
    total_harga: int

@app.get("/")
def home():
    return {"status": "online", "message": "Welcome to TRANSGO Backend API"}

# ==================== ENDPOINT REGISTER ====================
@app.post("/api/v1/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    # 1. Cek apakah email sudah terdaftar di database
    cek_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if cek_user:
        raise HTTPException(
            status_code=400, 
            detail="Email sudah terdaftar! Gunakan email lain."
        )
    
    # 2. Buat objek user baru (Tips skripsi: Idealnya password di-hash, kita simpan plain dulu untuk test awal)
    new_user = models.User(
        nama=user_data.nama,
        email=user_data.email,
        password=user_data.password, 
        role=user_data.role
    )
    
    # 3. Simpan ke MySQL
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"status": "success", "message": "Akun berhasil didaftarkan!", "user_id": new_user.id}

# ==================== ENDPOINT LOGIN ====================
@app.post("/api/v1/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    # 1. Cari user berdasarkan email di database MySQL
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    
    # 2. Jika user tidak ditemukan
    if not user:
        raise HTTPException(status_code=400, detail="Email atau password salah!")
        
    # 3. Cek apakah password cocok
    if user.password != user_data.password:
        raise HTTPException(status_code=400, detail="Email atau password salah!")
        
    # 4. Jika benar, kembalikan data sukses beserta detail usernya
    return {
        "status": "success",
        "message": "Login berhasil!",
        "user": {
            "id": user.id,
            "nama": user.nama,
            "email": user.email,
            "role": user.role
        }
    }

# ==================== ENDPOINT SIMPAN ORDER ====================
@app.post("/api/v1/orders")
def create_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    new_order = models.Order(
        user_id=order_data.user_id,
        kota_asal=order_data.kota_asal,
        kota_tujuan=order_data.kota_tujuan,
        berat=order_data.berat,
        total_harga=order_data.total_harga,
        status="Mencari Kurir"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return {"status": "success", "message": "Order pengiriman berhasil dibuat!", "order_id": new_order.id}

# ==================== ENDPOINT AMBIL SEMUA ORDER ====================
@app.get("/api/v1/orders")
def get_all_orders(db: Session = Depends(get_db)):
    orders = db.query(models.Order).all()
    return {"status": "success", "data": orders}

# ==================== ENDPOINT UPDATE STATUS (AMBIL ORDER) ====================
@app.put("/api/v1/orders/{order_id}/ambil")
def ambil_order(order_id: int, db: Session = Depends(get_db)):
    # 1. Cari order berdasarkan ID
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan!")
    
    # 2. Cek apakah orderan masih tersedia untuk diambil
    if order.status != "Mencari Kurir":
        raise HTTPException(status_code=400, detail="Order ini sudah diambil oleh kurir lain!")
    
    # 3. Ubah status orderan
    order.status = "Diproses (Kurir Menuju Lokasi)"
    db.commit()
    db.refresh(order)
    return {"status": "success", "message": "Orderan berhasil kamu ambil! Segera ambil paket ke lokasi asal."}

# ==================== INI TAMBAHAN: ENDPOINT UPDATE STATUS (SELESAI ANTAR) ====================
@app.put("/api/v1/orders/{order_id}/selesai")
def selesai_order(order_id: int, db: Session = Depends(get_db)):
    # 1. Cari order berdasarkan ID
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order tidak ditemukan!")
    
    # 2. Cek apakah statusnya memang sedang diproses
    if "Diproses" not in order.status:
        raise HTTPException(status_code=400, detail="Order belum diambil atau sudah selesai!")
    
    # 3. Ubah status menjadi Selesai
    order.status = "Selesai (Paket Diterima)"
    db.commit()
    db.refresh(order)
    return {"status": "success", "message": "Mantap! Tugas selesai, paket telah diterima pelanggan."}

# ==================== ENDPOINT HITUNG ONGKIR LAMA ====================
@app.get("/api/v1/hitung-ongkir")
def hitung_ongkir(kota_asal: str = Query(...), kota_tujuan: str = Query(...), berat_barang: float = Query(...)):
    tarif_per_kg = 5000
    biaya_admin = 2000
    jarak_simulasi = len(kota_asal) + len(kota_tujuan)
    total_ongkir = (berat_barang * tarif_per_kg) + (jarak_simulasi * 500) + biaya_admin
    return {
        "status": "success",
        "detail": {"asal": kota_asal, "tujuan": kota_tujuan, "berat": berat_barang, "tarif_per_kg": tarif_per_kg, "total_harga": total_ongkir}
    }