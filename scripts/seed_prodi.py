import sys
import os
import bcrypt

# Add root project path to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.database.connection import SessionLocal
from packages.database.models import User, Student, Advisor, ProdiAdmin

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def run():
    db = SessionLocal()
    
    print("1. Menambahkan Prodi ke Advisor berdasarkan mahasiswa bimbingan...")
    advisors = db.query(Advisor).all()
    for adv in advisors:
        if not adv.prodi and adv.mahasiswa_bimbingan:
            # Ambil prodi dari mahasiswa bimbingan pertamanya
            adv.prodi = adv.mahasiswa_bimbingan[0].prodi
            db.commit()
            print(f"Set Advisor {adv.nama} -> Prodi {adv.prodi}")
            
    print("2. Mencari semua Prodi unik dari Student...")
    prodis = db.query(Student.prodi).distinct().all()
    prodi_list = [p[0] for p in prodis if p[0]]
    
    print(f"Ditemukan {len(prodi_list)} program studi: {prodi_list}")
    
    print("3. Membuat User dan ProdiAdmin untuk setiap Prodi...")
    for prodi_name in prodi_list:
        username = f"kaprodi_{prodi_name.lower().replace(' ', '')}"
        
        # Check if user exists
        existing_user = db.query(User).filter(User.username == username).first()
        if not existing_user:
            # Create user
            new_user = User(
                username=username,
                hashed_password=hash_password("password123"),
                role="PRODI"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"Created User: {username}")
            
            # Create ProdiAdmin
            new_admin = ProdiAdmin(
                user_id=new_user.id,
                nama=f"Kaprodi {prodi_name}",
                prodi_name=prodi_name
            )
            db.add(new_admin)
            db.commit()
            print(f"Created ProdiAdmin: Kaprodi {prodi_name}")
        else:
            print(f"User {username} already exists, skipping.")

    db.close()
    print("Selesai.")

if __name__ == "__main__":
    run()
