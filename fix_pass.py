from packages.database.connection import get_db
from packages.database.models import User
import bcrypt
db = next(get_db())
nip = "197911172010122002"
hashed = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
u = db.query(User).filter(User.username == nip).first()
if u:
    u.hashed_password = hashed
    db.commit()
    print(f"Password rigorously updated for {nip}!")
