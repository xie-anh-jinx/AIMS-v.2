import os
import sys
from dotenv import load_dotenv

# Configure path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from packages.database.connection import SessionLocal
from sqlalchemy import text

MAPPING = {
    'F062': 'Kajian Budaya (S2)',
    'F032': 'Bahasa Indonesia (S2)',
    'F013': 'Ilmu Linguistik (S3)',
    'F042': 'Arkeologi (S2)',
    'F022': 'Bahasa Inggris (S2)',
    'F012': 'Linguistik (S2)',
    'F033': 'Sastra Indonesia (S3)',
    'F052': 'Sejarah (S2)',
    'F023': 'Bahasa Inggris (S3)',
}

def fix_prodi_raw():
    db = SessionLocal()
    total_updated = 0
    try:
        for prefix, new_prodi in MAPPING.items():
            result = db.execute(
                text("UPDATE students SET prodi = :prodi WHERE nim LIKE :prefix AND prodi != :prodi"),
                {"prodi": new_prodi, "prefix": f"{prefix}%"}
            )
            total_updated += result.rowcount
            print(f"Updated {result.rowcount} rows for {prefix}")
            
        db.commit()
        print(f"DONE! Total updated: {total_updated}")
    except Exception as e:
        db.rollback()
        print("Error:", e)
    finally:
        db.close()

if __name__ == "__main__":
    fix_prodi_raw()
