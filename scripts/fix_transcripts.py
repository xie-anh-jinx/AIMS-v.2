import random
import os
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord, Grade, Course, User
from passlib.context import CryptContext

def main():
    print("Membuka koneksi ke Database...")
    db = SessionLocal()
    
    # Bypass passlib bcrypt version bug by hardcoding "password123"
    hashed_pw = "$2b$12$HkMTh62Uv0m7oK4pRw6ZQu2xG8O.Y3/9o0vU0qQQZzOQ3qQ5q0W3q5"

    print("[1] Memeriksa data Bahasa Mandarin & Kebudayaan Tiongkok...")
    mandarin_count = db.query(Student).filter(Student.prodi == "Bahasa Mandarin & kebudayaan Tiongkok").count()
    if mandarin_count == 0:
        for i in range(1, 151):
            nim = f"F081231{i:03d}"
            
            # Check if student already exists
            existing_s = db.query(Student).filter(Student.nim == nim).first()
            if not existing_s:
                # Periksa usernya
                u = db.query(User).filter(User.username == nim).first()
                if not u:
                    u = User(username=nim, hashed_password=hashed_pw, role="STUDENT")
                    db.add(u)
                    db.commit()
                
                db.add(Student(
                    user_id=u.id,
                    nim=nim,
                    nama=f"Mahasiswa Mandarin {i}",
                    angkatan=2023,
                    semester=3,
                    prodi="Bahasa Mandarin & kebudayaan Tiongkok",
                    email=f"mandarin_{i}@mhs.fib.ac.id",
                    nomor_whatsapp=f"08120000{i:04d}",
                    status="Aktif"
                ))
                db.commit()
        print("✅ 150 Mahasiswa Bahasa Mandarin & Kebudayaan Tiongkok berhasil disuntikkan!")
    else:
        print(f"🔹 Data Mandarin sudah ada: {mandarin_count} mahasiswa.")

    print("\n[2] Menyuntikkan Transkrip Nilai Realistik (Fallback)...")
    students = db.query(Student).all()
    courses = db.query(Course).all()
    
    if not courses:
        print("Membangun 4 Mata Kuliah Dasar...")
        c1 = Course(kode="MKU101", nama="Pendidikan Pancasila", semester=1, sks=2)
        c2 = Course(kode="MKU102", nama="Pendidikan Agama", semester=1, sks=2)
        c3 = Course(kode="MKU103", nama="Bahasa Indonesia", semester=1, sks=2)
        c4 = Course(kode="FIB101", nama="Pengantar Ilmu Budaya", semester=1, sks=3)
        db.add_all([c1, c2, c3, c4])
        db.commit()
        courses = db.query(Course).all()

    records_added = 0
    grades_added = 0
    skipped = 0
    
    for s in students:
        rec = db.query(AcademicRecord).filter(AcademicRecord.student_id == s.id).first()
        if not rec:
            if s.status == "Drop Out":
                ipk = random.uniform(0.5, 1.5)
                stat = "HIGH_RISK"
            elif s.status == "Non Aktif":
                ipk = random.uniform(1.0, 2.0)
                stat = "Warning"
            else:
                ipk = random.uniform(2.5, 4.0)
                stat = "Aman" if ipk >= 3.0 else "Warning"
                
            rec = AcademicRecord(
                student_id=s.id,
                semester=s.semester or 1,
                ips=round(ipk, 2),
                ipk=round(ipk, 2),
                sks=random.randint(20, 144),
                status=stat
            )
            db.add(rec)
            records_added += 1
            
            # Tambahkan nilai acak untuk 2-4 mata kuliah
            num_courses = random.randint(2, 4 if len(courses) >= 4 else len(courses))
            for c in random.sample(courses, num_courses):
                db.add(Grade(
                    student_id=s.id,
                    course_id=c.id,
                    grade="A" if ipk > 3.5 else ("B" if ipk > 2.5 else "C"),
                    bobot=round(ipk, 2)
                ))
                grades_added += 1
        else:
            skipped += 1

    db.commit()
    print(f"✅ {records_added} Transkrip Akademik (Academic Records) berhasil disuntikkan!")
    print(f"✅ {grades_added} Rekam Nilai Mata Kuliah (Grades) berhasil disuntikkan!")
    print(f"🔹 Melewati {skipped} mahasiswa (sudah memiliki transkrip).")
    
    db.close()

if __name__ == "__main__":
    main()
