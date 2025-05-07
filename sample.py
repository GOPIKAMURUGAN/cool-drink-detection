import sqlite3

today_date = datetime.datetime.now().strftime("%Y_%m_%d")
DB_PATH = rf"C:\CoolDrinkDetection\backend\master_{today_date}.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check if the 'detections' table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='detections';")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ 'detections' table exists.")
else:
    print("❌ 'detections' table NOT found!")

conn.close()

