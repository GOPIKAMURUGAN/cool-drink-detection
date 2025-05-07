import sqlite3

db_path = r"C:\CoolDrinkDetection\backend\user_auth.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT username, password FROM users")
users = cursor.fetchall()

conn.close()

print("Stored Users in Database:")
for user in users:
    print(f"Username: {user[0]}, Password Hash: {user[1]}")
