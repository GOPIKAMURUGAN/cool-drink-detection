import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Enter the password you THINK is correct
password_to_test = "gopi07"
hashed_password = hash_password(password_to_test)

print(f"🔹 Hashed version of '{password_to_test}': {hashed_password}")
