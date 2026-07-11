"""
sync_sks_from_grades.py
Recalculate and sync AcademicRecord.sks + ipk from the real grades table
for ALL students who have grade data.
Run once to fix the synthetic values.
"""
from dotenv import load_dotenv
load_dotenv(".env")

from sqlalchemy import func
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord, Grade, Course

def main():
    db = SessionLocal()

    # Get all students who have at least one grade entry
    students_with_grades = db.query(Student.id, Student.nim).join(
        Grade, Grade.student_id == Student.id
    ).distinct().all()

    print(f"Found {len(students_with_grades)} students with grade data. Starting sync...")

    updated = 0
    created = 0
    skipped = 0

    for student_id, nim in students_with_grades:
        # Real SKS = sum of course.sks for all grades of this student
        real_sks = db.query(func.sum(Course.sks)).join(
            Grade, Grade.course_id == Course.id
        ).filter(Grade.student_id == student_id).scalar() or 0
        real_sks = int(real_sks)

        # Real IPK = weighted sum (bobot * sks) / total sks
        weighted_sum = db.query(func.sum(Grade.bobot * Course.sks)).join(
            Course, Grade.course_id == Course.id
        ).filter(Grade.student_id == student_id).scalar() or 0
        real_ipk = round(float(weighted_sum) / real_sks, 2) if real_sks > 0 else 0.0

        if real_sks == 0:
            skipped += 1
            continue

        # Update existing AcademicRecord
        records = db.query(AcademicRecord).filter(
            AcademicRecord.student_id == student_id
        ).order_by(AcademicRecord.semester.desc()).all()

        if records:
            # Update the latest record
            rec = records[0]
            changed = rec.sks != real_sks or abs(rec.ipk - real_ipk) > 0.01
            if changed:
                rec.sks = real_sks
                rec.ipk = real_ipk
                rec.ips = real_ipk  # Use same as ipk for cumulative record
                updated += 1
            else:
                skipped += 1
        else:
            # Create new record
            student = db.query(Student).filter(Student.id == student_id).first()
            new_r = AcademicRecord(
                student_id=student_id,
                semester=student.semester or 2,
                sks=real_sks,
                ipk=real_ipk,
                ips=real_ipk,
                status="AKTIF"
            )
            db.add(new_r)
            created += 1

    db.commit()
    print(f"\n✅ Sync complete!")
    print(f"   Updated : {updated} records")
    print(f"   Created : {created} new records")
    print(f"   Skipped : {skipped} (no grades or already up to date)")

    # Verify spot check
    from packages.database.models import User
    student = db.query(Student).filter(Student.nim == 'F051201050').first()
    if student:
        rec = db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).first()
        print(f"\n🔍 Spot check MUH. ALI IMRAN (F051201050):")
        if rec:
            print(f"   IPK: {rec.ipk}  |  SKS: {rec.sks}")
        else:
            print("   No record found")

if __name__ == "__main__":
    main()
