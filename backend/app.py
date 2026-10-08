from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import random
from datetime import datetime

app = Flask(
    __name__,
    static_folder="../frontend",
    static_url_path=""
)

CORS(app)

# ============================================================
# SENSOR DATA
# ============================================================

sensor_data = {
    "soil": 45.0,
    "tilt": 1.2,
    "ultrasonic": 50.0,
    "smoke": 20.0,
    "vibration": 0.0,
    "load": 2.5,
    "displacement": 0.5
}

# ============================================================
# THRESHOLDS
# ============================================================

thresholds = {
    "soil": {
        "warning": 60,
        "danger": 80
    },

    "tilt": {
        "warning": 2,
        "danger": 3
    },

    "ultrasonic": {
        "warning": 30,
        "danger": 15
    },

    "smoke": {
        "warning": 40,
        "danger": 70
    },

    "vibration": {
        "warning": 0.20,
        "danger": 0.25
    },

    "load": {
        "warning": 7,
        "danger": 9
    },

    "displacement": {
        "warning": 2,
        "danger": 3
    }
}

# ============================================================
# BUZZER
# ============================================================

# This represents the physical/automatic buzzer state.
# IMPORTANT:
# Buzzer is controlled ONLY by vibration.
buzzer_state = "OFF"


# ============================================================
# SENSOR STATUS FUNCTION
# ============================================================

def get_sensor_status(sensor, value):

    # Soil
    if sensor == "soil":
        if value >= thresholds["soil"]["danger"]:
            return "DANGER"
        elif value >= thresholds["soil"]["warning"]:
            return "WARNING"
        else:
            return "NORMAL"

    # Tilt
    elif sensor == "tilt":
        if value >= thresholds["tilt"]["danger"]:
            return "DANGER"
        elif value >= thresholds["tilt"]["warning"]:
            return "WARNING"
        else:
            return "NORMAL"

    # Ultrasonic
    # Smaller distance = more dangerous
    elif sensor == "ultrasonic":

        if value < 0:
            return "UNKNOWN"

        if value <= thresholds["ultrasonic"]["danger"]:
            return "DANGER"
        elif value <= thresholds["ultrasonic"]["warning"]:
            return "WARNING"
        else:
            return "NORMAL"

    # Smoke / gas
    elif sensor == "smoke":
        if value >= thresholds["smoke"]["danger"]:
            return "DANGER"
        elif value >= thresholds["smoke"]["warning"]:
            return "WARNING"
        else:
            return "NORMAL"

    # Vibration
    elif sensor == "vibration":
        if value >= thresholds["vibration"]["danger"]:
            return "DANGER"
        elif value >= thresholds["vibration"]["warning"]:
            return "WARNING"
        else:
            return "NORMAL"

    # Load
    elif sensor == "load":
        if value >= thresholds["load"]["danger"]:
            return "DANGER"
        elif value >= thresholds["load"]["warning"]:
            return "WARNING"
        else:
            return "NORMAL"

    # Ground displacement
    elif sensor == "displacement":
        if value >= thresholds["displacement"]["danger"]:
            return "DANGER"
        elif value >= thresholds["displacement"]["warning"]:
            return "WARNING"
        else:
            return "NORMAL"

    return "UNKNOWN"


# ============================================================
# CALCULATE OVERALL RISK
# ============================================================

def calculate_risk():

    statuses = {}

    for sensor, value in sensor_data.items():
        statuses[sensor] = get_sensor_status(sensor, value)

    # Critical conditions
    if (
        statuses["smoke"] == "DANGER"
        or
        statuses["vibration"] == "DANGER"
        or
        statuses["load"] == "DANGER"
        or
        statuses["displacement"] == "DANGER"
    ):
        return "CRITICAL", statuses

    # Warning conditions
    if "WARNING" in statuses.values():
        return "WARNING", statuses

    return "SAFE", statuses


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():

    try:
        return send_from_directory(
            app.static_folder,
            "index.html"
        )

    except Exception:
        return jsonify({
            "success": True,
            "message": "Mine Security AI backend is running"
        })


# ============================================================
# GET SENSOR DATA
# ============================================================

@app.route("/api/sensors", methods=["GET"])
def get_sensors():

    risk, statuses = calculate_risk()

    return jsonify({
        "success": True,
        "data": sensor_data,
        "statuses": statuses,
        "risk": risk,
        "buzzer": buzzer_state,
        "time": datetime.now().isoformat()
    })


# ============================================================
# POST SENSOR DATA
# ESP32 SENDS DATA HERE
# ============================================================

@app.route("/api/sensors", methods=["POST"])
def update_sensors():

    global buzzer_state

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "message": "No JSON data received"
            }), 400

        # ----------------------------------------------------
        # SENSOR ALIASES
        # ----------------------------------------------------

        # Soil
        if "soil" in data:
            sensor_data["soil"] = float(data["soil"])

        elif "moisture" in data:
            sensor_data["soil"] = float(data["moisture"])

        # Tilt
        if "tilt" in data:
            sensor_data["tilt"] = float(data["tilt"])

        # Ultrasonic
        if "ultrasonic" in data:
            sensor_data["ultrasonic"] = float(data["ultrasonic"])

        elif "distance" in data:
            sensor_data["ultrasonic"] = float(data["distance"])

        # MQ-4 gas
        if "smoke" in data:
            sensor_data["smoke"] = float(data["smoke"])

        elif "gas" in data:
            sensor_data["smoke"] = float(data["gas"])

        # Vibration
        if "vibration" in data:

            sensor_data["vibration"] = float(
                data["vibration"]
            )

            # =================================================
            # IMPORTANT:
            # BUZZER ONLY FOR VIBRATION
            # =================================================

            if sensor_data["vibration"] >= 1:
                buzzer_state = "ON"
            else:
                buzzer_state = "OFF"

        # Load
        if "load" in data:
            sensor_data["load"] = float(data["load"])

        elif "weight" in data:
            sensor_data["load"] = float(data["weight"])

        # Ground displacement
        if "displacement" in data:
            sensor_data["displacement"] = float(
                data["displacement"]
            )

        elif "ground_displacement" in data:
            sensor_data["displacement"] = float(
                data["ground_displacement"]
            )

        # ----------------------------------------------------
        # CALCULATE RISK
        # ----------------------------------------------------

        risk, statuses = calculate_risk()

        return jsonify({
            "success": True,
            "message": "Sensor data updated",
            "data": sensor_data,
            "statuses": statuses,
            "risk": risk,
            "buzzer": buzzer_state,
            "time": datetime.now().isoformat()
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ============================================================
# SIMULATE SENSOR DATA
# ============================================================

@app.route("/api/simulate", methods=["POST"])
def simulate():

    global buzzer_state

    sensor_data["soil"] = round(
        random.uniform(20, 90), 2
    )

    sensor_data["tilt"] = round(
        random.uniform(0, 4), 2
    )

    sensor_data["ultrasonic"] = round(
        random.uniform(10, 70), 2
    )

    sensor_data["smoke"] = round(
        random.uniform(0, 100), 2
    )

    sensor_data["vibration"] = round(
        random.choice([0, 0.15, 0.30]), 2
    )

    sensor_data["load"] = round(
        random.uniform(1, 11), 2
    )

    sensor_data["displacement"] = round(
        random.uniform(0, 4), 2
    )

    # Buzzer only for vibration
    if sensor_data["vibration"] >= 0.25:
        buzzer_state = "ON"
    else:
        buzzer_state = "OFF"

    risk, statuses = calculate_risk()

    return jsonify({
        "success": True,
        "message": "Simulation data generated",
        "data": sensor_data,
        "statuses": statuses,
        "risk": risk,
        "buzzer": buzzer_state,
        "time": datetime.now().isoformat()
    })


# ============================================================
# RESET SENSOR DATA
# ============================================================

@app.route("/api/reset", methods=["POST"])
def reset():

    global buzzer_state

    sensor_data["soil"] = 45.0
    sensor_data["tilt"] = 1.2
    sensor_data["ultrasonic"] = 50.0
    sensor_data["smoke"] = 20.0
    sensor_data["vibration"] = 0.0
    sensor_data["load"] = 2.5
    sensor_data["displacement"] = 0.5

    buzzer_state = "OFF"

    risk, statuses = calculate_risk()

    return jsonify({
        "success": True,
        "message": "Sensor data reset",
        "data": sensor_data,
        "statuses": statuses,
        "risk": risk,
        "buzzer": buzzer_state,
        "time": datetime.now().isoformat()
    })


# ============================================================
# BUZZER API
# ============================================================

@app.route("/api/buzzer", methods=["GET", "POST"])
def buzzer():

    global buzzer_state

    # GET
    if request.method == "GET":

        return jsonify({
            "success": True,
            "buzzer": buzzer_state
        })

    # POST
    try:

        data = request.get_json()

        if data and "state" in data:

            requested_state = str(
                data["state"]
            ).upper()

            if requested_state in ["ON", "OFF"]:
                buzzer_state = requested_state

        return jsonify({
            "success": True,
            "buzzer": buzzer_state
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():

    return jsonify({
        "success": True,
        "status": "online",
        "message": "Mine Security AI backend is running",
        "time": datetime.now().isoformat()
    })


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )