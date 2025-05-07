import sqlite3
import os
from datetime import datetime
import pytz
from auth import get_user_role  # Import user authentication

# Define your local timezone
LOCAL_TZ = pytz.timezone("Asia/Kolkata")

# Base directory for DB storage
BASE_DB_PATH = r"D:\CoolDrinkDetection\RestrictedDB"

# Ensure path exists
if not os.path.exists(BASE_DB_PATH):
    os.makedirs(BASE_DB_PATH)

def get_local_time():
    return datetime.now(LOCAL_TZ).strftime("%Y-%m-%d %H:%M:%S")

def get_today_date_str():
    return datetime.now(LOCAL_TZ).strftime("%Y_%m_%d")

def get_master_db_path():
    return os.path.join(BASE_DB_PATH, f"master_{get_today_date_str()}.db")

def get_shift_db_path(shift):
    shift = shift.lower()
    return os.path.join(BASE_DB_PATH, f"{shift}_{get_today_date_str()}.db")


def validate_time_format(time_str):
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None

# Create necessary tables if not exist
def init_db(db_path, is_master=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Detection table
    cursor.execute('''
       CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT,
            color TEXT,
            flavor TEXT,
            ingredients TEXT,
            detection_status TEXT,
            timestamp TEXT
        );
    ''')

    # Brand count table
      # Brand count table
    if is_master:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_brand_counts (
                brand TEXT,
                date TEXT,
                count INTEGER,
                UNIQUE(brand, date)
            );
        ''')
       
        # Store work status for all shifts in master DB
        

    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS brand_counts (
                brand TEXT PRIMARY KEY,
                count INTEGER
            );
        ''')
        
    conn.commit()
    conn.close()

# Insert detection into a given DB
def insert_into_db(db_path, brand, color, flavor, ingredients, status):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    timestamp = get_local_time()

    cursor.execute('''
        INSERT INTO detections (brand, color, flavor, ingredients, detection_status, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (brand, color, flavor, ingredients, status, timestamp))

    conn.commit()
    conn.close()

# Update brand count in shift DB
def update_brand_count_shift(db_path, brand):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT count FROM brand_counts WHERE brand = ?', (brand,))
    row = cursor.fetchone()

    if row:
        new_count = row[0] + 1
        cursor.execute('UPDATE brand_counts SET count = ? WHERE brand = ?', (new_count, brand))
    else:
        cursor.execute('INSERT INTO brand_counts (brand, count) VALUES (?, ?)', (brand, 1))

    conn.commit()
    conn.close()

# Update daily brand count in master DB
def update_brand_count_master(db_path, brand):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    today = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")

    cursor.execute('SELECT count FROM daily_brand_counts WHERE brand = ? AND date = ?', (brand, today))
    row = cursor.fetchone()

    if row:
        new_count = row[0] + 1
        cursor.execute('UPDATE daily_brand_counts SET count = ? WHERE brand = ? AND date = ?', (new_count, brand, today))
    else:
        cursor.execute('INSERT INTO daily_brand_counts (brand, date, count) VALUES (?, ?, ?)', (brand, today, 1))

    conn.commit()
    conn.close()

def insert_detection(brand, color, flavor, ingredients, status, shift):
    shift_db = get_shift_db_path(shift)
    master_db = get_master_db_path()

    print(f"🔄 Inserting detection: {brand}, {color}, {flavor}, {status} into {shift_db} and {master_db}")

    # Initialize tables if not exist
    init_db(shift_db, is_master=False)
    init_db(master_db, is_master=True)

    # Insert detections
    insert_into_db(shift_db, brand, color, flavor, ingredients, status)
    insert_into_db(master_db, brand, color, flavor, ingredients, status)

    # Update brand counts
    update_brand_count_shift(shift_db, brand)
    update_brand_count_master(master_db, brand)

    print(f"✅ Detection inserted successfully!")


# Fetch detection records - **Only admins allowed**
def get_detections(username, shift):
    """Fetch detection records only if user is admin."""
    user_role = get_user_role(username)  # Get user role from user_auth.db

    if user_role != "admin":
        return {"error": "Access Denied: Only admins can view detections"}

    db_path = get_shift_db_path(shift)
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, brand, color, flavor, ingredients, detection_status, timestamp FROM detections ORDER BY timestamp DESC")
    rows = cursor.fetchall()
    conn.close()

    return [  # Return formatted detection data
        {
            "id": row[0],
            "brand": row[1],
            "color": row[2],
            "flavor": row[3],
            "ingredients": row[4],
            "detection_status": row[5],
            "timestamp": row[6]
        }
        for row in rows
    ]
# OPTIONAL: Get brand counts (API support later if needed)
def get_brand_counts(shift):
    db_path = get_shift_db_path(shift)
    if not os.path.exists(db_path):
        return []

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT brand, count FROM brand_counts ORDER BY count DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"brand": row[0], "count": row[1]} for row in rows]

# Fetch daily brand counts - **Only admins allowed**
def get_daily_brand_counts(username):
    """Fetch daily brand counts only if user is admin."""
    user_role = get_user_role(username)  # Check user role

    if user_role != "admin":
        return {"error": "Access Denied: Only admins can view brand counts"}

    db_path = get_master_db_path()
    if not os.path.exists(db_path):
        return []

    today = datetime.now(LOCAL_TZ).strftime("%Y-%m-%d")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT brand, count FROM daily_brand_counts WHERE date = ? ORDER BY count DESC", (today,))
    rows = cursor.fetchall()
    conn.close()

    return [{"brand": row[0], "count": row[1]} for row in rows]
