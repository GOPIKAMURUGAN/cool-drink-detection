from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import cv2
import base64
import numpy as np
from ultralytics import YOLO
from database import insert_detection, get_detections  # Shift-based detection results DB
import logging
from flask_cors import CORS
from flask_session import Session  # Import Flask-Session
from flask import send_file 
import os
import sqlite3
import subprocess
import psutil
import sys

DB_FOLDER = "D:/CoolDrinkDetection/RestrictedDB"


app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = "your_secret_key"  # Needed for session handling
app.config["SESSION_TYPE"] = "filesystem"  
app.config["SESSION_FILE_DIR"] = "./flask_sessions"  # Store session files
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
app.config["SESSION_KEY_PREFIX"] = "cooldrink_"

# Ensure session directory exists
os.makedirs(app.config["SESSION_FILE_DIR"], exist_ok=True)

# 🔹 Initialize session
Session(app)

from werkzeug.serving import WSGIRequestHandler
WSGIRequestHandler.protocol_version = "HTTP/1.1"

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    return jsonify({"status": "running"}), 200

@app.route('/list_databases')
def list_databases():
    """List all database files in RestrictedDB."""
    if 'username' in session and session['role'] == 'admin':
        try:
            files = [f for f in os.listdir(DB_FOLDER) if f.endswith(".db")]
            return jsonify({"files": files})
        except Exception as e:
            return jsonify({"error": str(e)})
    return jsonify({"error": "❌ Access Denied!"}), 403


@app.route('/view_database/<db_name>')
def view_database(db_name):
    """Fetch tables from the selected database."""
    if 'username' in session and session['role'] == 'admin':
        db_path = os.path.join(DB_FOLDER, db_name)
        if not os.path.exists(db_path):
            return jsonify({"error": "⚠ Database file not found!"}), 404

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            return jsonify({"tables": tables})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "❌ Access Denied!"}), 403


@app.route('/view_table/<db_name>/<table_name>')
def view_table(db_name, table_name):
    """View contents of a selected table."""
    if 'username' in session and session['role'] == 'admin':
        db_path = os.path.join(DB_FOLDER, db_name)
        if not os.path.exists(db_path):
            return jsonify({"error": "⚠ Database file not found!"}), 404

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            conn.close()
            return jsonify({"columns": columns, "rows": rows})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "❌ Access Denied!"}), 403

@app.before_request
def before_request_tasks():
    print(f"Incoming request: {request.method} {request.path}")  # Log requests
   
    # 🔹 Ensure users are redirected to login if session is missing
    if request.endpoint not in ['login', 'static'] and 'username' not in session:
        print("🔸 Session missing. Redirecting to login page.")
        return redirect(url_for('login'))


@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))  # ✅ Redirect to login if not logged in

    # ✅ If logged in, go to the correct dashboard
    if session['role'] == 'employee':
        return redirect(url_for('employee_dashboard'))
    elif session['role'] == 'admin':
        return redirect(url_for('admin_dashboard'))
    
    return redirect(url_for('login'))  # Fallback case


from auth import verify_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # No need to encode here

        role = verify_user(username, password)  # Verify credentials
        
        if role:
            session['username'] = username
            session['role'] = role
            return redirect(url_for('admin_dashboard' if role == 'admin' else 'employee_dashboard'))
        
        return render_template('login.html', error="Invalid username or password!")  # Wrong credentials

    return render_template('login.html')  # Show login page


@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', username=session['username'])



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/employee_dashboard')
def employee_dashboard():
    if 'username' in session and session['role'] == 'employee':
        return render_template('index.html')  # Employee can access detection results
    return "Unauthorized Access", 403


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'username' in session and session['role'] == 'admin':
        return render_template('index.html')  # Admin can access database
    return "Unauthorized Access", 403

@app.route('/check_role')
def check_role():
    if 'username' in session:
        return jsonify({"role": session['role']})
    return jsonify({"role": "guest"})



@app.route('/restricted_db/<db_name>')
def restricted_db(db_name):
    if 'username' in session and session['role'] == 'admin':
        db_path = os.path.join(DB_FOLDER, db_name)
        if os.path.exists(db_path):
            return send_file(db_path, as_attachment=True)
        return "⚠ Database file not found!", 404
    return "❌ Access Denied! Only admins can open the database.", 403

DASHBOARD_PATH = r"D:\CoolDrinkDetection\backend\dashboard.py"

@app.route('/open_dashboard')
def open_dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        # Kill existing Streamlit processes before starting a new one
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and any("streamlit" in part for part in proc.info['cmdline']):
                    print(f"🔴 Killing old Streamlit process: {proc.info['pid']}")
                    proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Start the dashboard using a properly formatted command
        command = [sys.executable, "-m", "streamlit", "run", DASHBOARD_PATH]
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return jsonify({"url": "http://127.0.0.1:8501"})

    except Exception as e:
        print(f"❌ Failed to open dashboard: {e}")
        return jsonify({"error": str(e)}), 500


@app.get("/test_model")
async def test_model():
    try:
        # Define the missing function
        def run_dummy_inference():
            return {"message": "Dummy inference executed successfully"}

        # Call the function
        result = run_dummy_inference()
        return {"status": "success", "output": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def run_dummy_inference():
    return {"message": "Dummy inference executed successfully"}




# Load YOLO models
brand_model = YOLO("D:/CoolDrinkDetection/backend/model/brand_best.pt")  
defect_model = YOLO("D:/CoolDrinkDetection/backend/model/defect_best.pt")

# Dummy image for model warm-up (black image)
dummy_image = np.zeros((640, 640, 3), dtype=np.uint8)

# Warm-up the models with the dummy image
try:
    print("🔄 Warming up YOLO models...")
    brand_model.predict(dummy_image)
    defect_model.predict(dummy_image)
    print("✅ Model warm-up complete.")
except Exception as e:
    print(f"❌ Error during model warm-up: {e}")


drink_info = {
    "Fanta": {"color": "Orange", "flavor": "Orange", "ingredients": "Carbonated Water, Sugar, Citric Acid, Natural Orange Flavor"},
    "Appy Fizz": {"color": "Golden Yellow", "flavor": "Apple", "ingredients": "Carbonated Apple Juice, Sugar, Citric Acid"},
    "Sprite": {"color": "Clear", "flavor": "Lemon-Lime", "ingredients": "Carbonated Water, Sugar, Citric Acid, Lemon and Lime Flavoring"},
    "Pepsi": {"color": "Dark Brown", "flavor": "Cola", "ingredients": "Carbonated Water, Sugar, Caramel Color, Phosphoric Acid, Caffeine"},
    "Frooti": {"color": "Mango Yellow", "flavor": "Mango", "ingredients": "Mango Pulp, Sugar, Water, Citric Acid"},
    "Coca-Cola": {"color": "Dark Brown", "flavor": "Cola", "ingredients": "Carbonated Water, Sugar, Caramel Color, Phosphoric Acid, Caffeine"},
    "Mirinda": {"color": "Bright Orange", "flavor": "Orange", "ingredients": "Carbonated Water, Sugar, Orange Juice, Citric Acid"},
    "Limca": {"color": "Cloudy White", "flavor": "Lemon", "ingredients": "Carbonated Water, Sugar, Lemon Juice, Citric Acid"},
    "Sting": {"color": "Red", "flavor": "Berry", "ingredients": "Carbonated Water, Sugar, Citric Acid, Caffeine, Taurine"}
}


logging.basicConfig(level=logging.DEBUG)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        if 'username' not in session:
            return jsonify({"error": "Unauthorized access"}), 403  

        if not request.is_json:
            return jsonify({"error": "Invalid request format. Expecting JSON."}), 400

        data = request.get_json()
        if "image" not in data or "shift" not in data:
            return jsonify({"error": "Missing 'image' or 'shift' in request"}), 400

        base64_image = data["image"]
        shift = data.get('shift')
        if not shift:
            return jsonify({"error": "Shift not specified in request"}), 400

        # Process Image
        image_data = base64.b64decode(base64_image.split(',')[1])
        np_arr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({"error": "Invalid image format"}), 400

        # YOLO brand detection
        brand_results = brand_model.predict(image)
        detected_brand = "Unknown"

        if brand_results and len(brand_results[0].boxes) > 0:
            detected_class_id = int(brand_results[0].boxes.cls[0])
            detected_class_name = brand_model.names[detected_class_id].strip().title()
            confidence = float(brand_results[0].boxes.conf[0])

            if confidence >= 0.5:
                detected_brand = detected_class_name

        # Defect Detection
        defect_results = defect_model.predict(image)
        detection_status = "Good"

        if defect_results and len(defect_results[0].boxes) > 0:
            defect_class_id = int(defect_results[0].boxes.cls[0])
            defect_class_name = defect_model.names[defect_class_id].strip().title()
            defect_confidence = float(defect_results[0].boxes.conf[0])

            if defect_confidence >= 0.5:
                if "Damage" in defect_class_name:
                    detection_status = "Damage"

        # Ensure detection_status is valid
        if detection_status not in ["Good", "Damage"]:
            detection_status = "Good"

        response_data = {
            "brand": detected_brand,
            "color": drink_info.get(detected_brand, {}).get("color", "Unknown"),
            "flavor": drink_info.get(detected_brand, {}).get("flavor", "Unknown"),
            "ingredients": drink_info.get(detected_brand, {}).get("ingredients", "Unknown"),
            "detection_status": detection_status
        }

        insert_detection(detected_brand, response_data["color"], response_data["flavor"], response_data["ingredients"], detection_status, shift)

        return jsonify(response_data)

    except Exception as e:
        app.logger.error(f"❌ Error: {str(e)}")
        return jsonify({"error": f"Unexpected error occurred: {str(e)}"}), 500



@app.route('/detections', methods=['GET'])
def detections():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized access"}), 403
    shift = request.args.get("shift", "shift1")
    data = get_detections(shift)
    return jsonify(data)


@app.route('/debug_session')
def debug_session():
    return str(session)  # Print current session data


if __name__ == '__main__':
    print(app.url_map)
    app.run(host="127.0.0.1", port=8000, debug=True)