import sqlite3
import os

# List of all shift databases
shift_dbs = ["shift1.db", "shift2.db", "shift3.db"]

# Path to the databases
BASE_DB_PATH = r"C:\CoolDrinkDetection\backend"

def reset_work_status_table(db_name):
    db_path = os.path.join(BASE_DB_PATH, db_name)
    
    if not os.path.exists(db_path):
        print(f"⚠️ Database {db_name} not found, skipping...")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"🔄 Resetting work_status table in {db_name}...")

    # Drop the old work_status table if it exists
    cursor.execute("DROP TABLE IF EXISTS work_status")

    # Recreate the work_status table with correct schema
    cursor.execute('''
        CREATE TABLE work_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            status_type TEXT,
            start_time TEXT,
            end_time TEXT,
            duration INTEGER
        )
    ''')

    conn.commit()
    conn.close()
    print(f"✅ work_status table fixed in {db_name}")

# Run the fix on all shift databases
for db in shift_dbs:
    reset_work_status_table(db)
