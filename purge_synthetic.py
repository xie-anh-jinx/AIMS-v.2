import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import AcademicRecord

db = SessionLocal()
# Hapus semua academic record karena semuanya tadi digenerate random!
db.query(AcademicRecord).delete()
db.commit()
print("Berhasil menghapus seluruh riwayat metrik palsu (Dummy IPK)!")
