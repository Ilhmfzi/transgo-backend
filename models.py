from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), default="pelanggan")

# --- INI TAMBAHAN TABEL ORDERS ---
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False) # ID Pelanggan yang order
    kota_asal = Column(String(100), nullable=False)
    kota_tujuan = Column(String(100), nullable=False)
    berat = Column(Float, nullable=False)
    total_harga = Column(Integer, nullable=False)
    status = Column(String(50), default="Mencari Kurir") # Mencari Kurir -> Diproses -> Selesai