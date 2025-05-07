import sqlite3
import hashlib

db_path = r"D:\CoolDrinkDetection\backend\user_auth.db"  # Path to the user authentication database

import hashlib

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user_table():
    """Creates the users table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, password, role):
    """Adds a new user to the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Error: Username '{username}' already exists.")
    conn.close()

def verify_user(username, password):
    """Verifies user credentials and returns the user role."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Fetch stored password and role
    cursor.execute("SELECT password, role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result:
        stored_password, role = result
        hashed_input_password = hash_password(password)

        print(f"🔹 Stored Password (DB): {stored_password}")  # Debugging
        print(f"🔹 Hashed Entered Password: {hashed_input_password}")  # Debugging

        if stored_password.strip() == hashed_input_password.strip():
            return role  # ✅ Authentication successful
    
    print("❌ Authentication failed!")
    return None  # ❌ Authentication failed



def get_user_role(username):
    """Fetch the role of a user from user_auth.db"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None  # Return the role if found, otherwise None    

# Run this once to create the table if it doesn't exist
if __name__ == "__main__":
    create_user_table()