from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL koneksi ke MySQL XAMPP (Username bawaan XAMPP adalah root, password-nya kosong)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/transgo_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Fungsi untuk mendapatkan sesi database di setiap request API
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()