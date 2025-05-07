import hashlib

# Define stored hashed passwords (from your database)
stored_passwords = {
    "nisha": "48a34e474d0de87dad5430827177b8b9a15d38d6695c6357ac772903cade1e2e",
    "gopika": "41f0f88265e4a1c8b389a1d497c792ba23db75cbaa9863461489deb34433cb6c"
}

# Function to hash input password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Test login credentials
test_username = input("Enter username: ")
test_password = input("Enter password: ")

# Hash the entered password
hashed_test_password = hash_password(test_password)

# Check if it matches stored hash
if test_username in stored_passwords and stored_passwords[test_username] == hashed_test_password:
    print("✅ Login successful!")
else:
    print("❌ Invalid username or password.")
