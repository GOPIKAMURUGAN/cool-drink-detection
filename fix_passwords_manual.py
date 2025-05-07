import sqlite3

db_path = r"C:\CoolDrinkDetection\backend\user_auth.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Reset passwords to correct single-hashed values
cursor.execute("UPDATE users SET password = ? WHERE username = ?", (
    "76bddac6dd412463111c7a139592d2d05b24d5c1ef349d9972792ed796683401", "nisha"
))

cursor.execute("UPDATE users SET password = ? WHERE username = ?", (
    "ee4293bfa2f4fb6b106a9fb3b0936e96be1fcb5a60711ae3f81e75f8dcb77d3b", "gopika"
))

conn.commit()
conn.close()

print("✅ Passwords have been fixed! Try logging in again.")
