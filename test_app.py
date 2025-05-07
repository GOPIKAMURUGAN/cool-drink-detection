from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask server is running!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    return jsonify({"message": "Prediction successful!", "received_data": data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
