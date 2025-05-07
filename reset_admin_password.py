from auth import hash_password
import sqlite3

conn = sqlite3.connect("C:/CoolDrinkDetection/backend/user_auth.db")
cursor = conn.cursor()

new_hashed_password = hash_password("admin123")  # Change this to your new password

cursor.execute("UPDATE users SET password = ? WHERE username = 'admin'", (new_hashed_password,))
conn.commit()
conn.close()

print("✅ Admin password reset to: admin123")
