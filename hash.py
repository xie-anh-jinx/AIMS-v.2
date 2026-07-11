import bcrypt
print(bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt()).decode("utf-8"))
