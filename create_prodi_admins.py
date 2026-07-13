"""
create_prodi_admins.py
────────────────────────
Membuat user Kaprodi (role PRODI) untuk seluruh program studi
yang terdaftar di database, lalu menghubungkannya di tabel prodi_admins.

Jalankan: python3 create_prodi_admins.py
"""

import os, sys, bcrypt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import User, Student, ProdiAdmin

def main():
    db = SessionLocal()
    
    # Ambil daftar prodi unik dari database mahasiswa angkatan 2019-2025
    prodis = [r[0] for r in db.query(Student.prodi).distinct().all() if r[0]]
    
    print(f"Ditemukan {len(prodis)} prodi aktif di database.")
    
    hashed_pw = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode()
    
    created = 0
    updated = 0
    
    # Mapping nama prodi ke username ramah URL/login
    table_rows = []
    
    for prodi in sorted(prodis):
        # Format username: prodi_sastra_jepang
        clean_name = prodi.lower()
        clean_name = clean_name.replace(" ", "_").replace("(", "").replace(")", "").replace("-", "_").replace("&", "dan")
        username = f"prodi_{clean_name}"
        
        # 1. Pastikan User ada
        u = db.query(User).filter(User.username == username).first()
        if not u:
            u = User(username=username, hashed_password=hashed_pw, role="PRODI")
            db.add(u)
            db.flush()
            created += 1
        else:
            u.role = "PRODI"
            u.hashed_password = hashed_pw
            updated += 1
            
        # 2. Pastikan ProdiAdmin terhubung
        pa = db.query(ProdiAdmin).filter(ProdiAdmin.user_id == u.id).first()
        if not pa:
            pa = ProdiAdmin(
                user_id=u.id,
                nama=f"Kaprodi {prodi}",
                prodi_name=prodi
            )
            db.add(pa)
            
        table_rows.append((prodi, username, "password123"))
        
    db.commit()
    db.close()
    
    print("=" * 60)
    print(f"👥 Seeding Akun Kaprodi (PRODI) Selesai!")
    print(f"   - User baru dibuat   : {created}")
    print(f"   - User lama diupdate : {updated}")
    print("=" * 60)
    print("\nDaftar Akun Kaprodi:")
    print("| Program Studi | Username | Password |")
    print("|---|---|---|")
    for r in table_rows:
        print(f"| {r[0]} | `{r[1]}` | `{r[2]}` |")

if __name__ == "__main__":
    main()
