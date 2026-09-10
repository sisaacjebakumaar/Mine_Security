from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)

# =========================================================
# SENSOR DATA
# =========================================================

sensor_data = {
    "displacement": 2.4,
    "vibration": 0.18,
    "tilt": 1.8,
    "moisture": 42.0
}


# =========================================================
# RISK CALCULATION
# =========================================================

def calculate_risk(displacement, vibration, tilt, moisture):
    """
    Calculate mine safety risk based on sensor values.

    LOW    -> Normal condition
    MEDIUM -> Warning condition
    HIGH   -> Dangerous condition
    """

    risk_score = 0

    # Displacement
    if displacement >= 3.0:
        risk_score += 3
    elif displacement >= 2.0:
        risk_score += 1

    # Vibration
    if vibration >= 0.25:
        risk_score += 3
    elif vibration >= 0.20:
        risk_score += 1

    # Tilt
    if tilt >= 3.0:
        risk_score += 3
    elif tilt >= 2.0:
        risk_score += 1

    # Moisture
    if moisture >= 80:
        risk_score += 2
    elif moisture >= 60:
        risk_score += 1

    # Final risk
    if risk_score >= 6:
        return "HIGH"
    elif risk_score >= 2:
        return "MEDIUM"
    else:
        return "LOW"


# =========================================================
# GET CURRENT TIME
# =========================================================

def get_current_time():
    return datetime.now().strftime("%H:%M:%S")


# =========================================================
# FORMAT SENSOR RESPONSE
# =========================================================

def get_sensor_response():
    """
    Creates the exact response structure
    expected by the frontend.
    """

    risk = calculate_risk(
        sensor_data["displacement"],
        sensor_data["vibration"],
        sensor_data["tilt"],
        sensor_data["moisture"]
    )

    return {
        "success": True,
        "data": {
            "displacement": sensor_data["displacement"],
            "vibration": sensor_data["vibration"],
            "tilt": sensor_data["tilt"],
            "moisture": sensor_data["moisture"]
        },
        "risk": risk,
        "time": get_current_time()
    }


# =========================================================
# HOME / SERVER CHECK
# =========================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "success": True,
        "message": "Mine Security AI Monitoring Backend is Running",
        "status": "online",
        "time": get_current_time()
    })


# =========================================================
# GET SENSOR DATA
# =========================================================

@app.route("/api/sensors", methods=["GET"])
def get_sensors():

    return jsonify(get_sensor_response())


# =========================================================
# UPDATE SENSOR DATA
# =========================================================

@app.route("/api/sensors", methods=["POST"])
def update_sensors():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No sensor data received"
        }), 400

    try:

        # Update only values received from the device
        if "displacement" in data:
            sensor_data["displacement"] = float(
                data["displacement"]
            )

        if "vibration" in data:
            sensor_data["vibration"] = float(
                data["vibration"]
            )

        if "tilt" in data:
            sensor_data["tilt"] = float(
                data["tilt"]
            )

        if "moisture" in data:
            sensor_data["moisture"] = float(
                data["moisture"]
            )

    except (ValueError, TypeError):

        return jsonify({
            "success": False,
            "message": "Sensor values must be numbers"
        }), 400

    response = get_sensor_response()

    response["message"] = "Sensor data updated successfully"

    return jsonify(response)


# =========================================================
# SIMULATE SENSOR DATA
# =========================================================

@app.route("/api/simulate", methods=["GET"])
def simulate():

    # Generate realistic demo values
    sensor_data["displacement"] = round(
        random.uniform(1.0, 4.0), 2
    )

    sensor_data["vibration"] = round(
        random.uniform(0.10, 0.30), 2
    )

    sensor_data["tilt"] = round(
        random.uniform(1.0, 3.5), 2
    )

    sensor_data["moisture"] = round(
        random.uniform(35.0, 90.0), 2
    )

    response = get_sensor_response()

    response["message"] = "Demo sensor data generated"

    return jsonify(response)


# =========================================================
# RESET SENSOR DATA
# =========================================================

@app.route("/api/reset", methods=["GET"])
def reset_sensors():

    sensor_data["displacement"] = 2.4
    sensor_data["vibration"] = 0.18
    sensor_data["tilt"] = 1.8
    sensor_data["moisture"] = 42.0

    response = get_sensor_response()

    response["message"] = "Sensor data reset successfully"

    return jsonify(response)


# =========================================================
# SERVER START
# =========================================================

if __name__ == "__main__":

    print("--------------------------------------------")
    print(" Mine Security AI Backend")
    print(" AI Mine Subsidence Monitoring System")
    print("--------------------------------------------")
    print("Server: http://127.0.0.1:5000")
    print("API:    http://127.0.0.1:5000/api/sensors")
    print("--------------------------------------------")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )