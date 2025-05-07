import sqlite3

DB_PATH = r"C:\CoolDrinkDetection\RestrictedDB\master_2025_03_30.db"  # Ensure correct path

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ✅ Create table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT,
        color TEXT,
        flavor TEXT,
        ingredients TEXT,
        detection_status TEXT,
        timestamp TEXT
    )
''')

conn.commit()
conn.close()
print("Table verified successfully!")
