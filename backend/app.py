from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
import random
import os


# =========================================================
# MINE SECURITY AI
# BACKEND SERVER
#
# Sensors:
# 1. Soil Moisture
# 2. MPU6050 Tilt
# 3. Ultrasonic Distance
# 4. Smoke
# 5. Vibration
# 6. Load
# 7. Ground Displacement
#
# Actuator:
# - Buzzer
# =========================================================


# =========================================================
# FRONTEND LOCATION
# =========================================================

FRONTEND_FOLDER = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "frontend"
    )
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)

CORS(app)


# =========================================================
# SENSOR DATA
#
# These are demo values.
# Later, replace them with actual ESP32/sensor values.
# =========================================================

sensor_data = {

    "soil": 42.0,

    "tilt": 1.8,

    "ultrasonic": 45.0,

    "smoke": 20.0,

    "vibration": 0.18,

    "load": 5.0,

    "displacement": 2.4

}


# =========================================================
# BUZZER STATE
#
# Buzzer is an actuator, NOT a sensor.
# =========================================================

buzzer_state = "OFF"


# =========================================================
# SENSOR THRESHOLDS
#
# IMPORTANT:
# These are prototype/demo thresholds only.
# They are NOT certified mine-safety limits.
# =========================================================

THRESHOLDS = {

    "soil": {
        "warning": 60.0,
        "danger": 80.0
    },

    "tilt": {
        "warning": 2.0,
        "danger": 3.0
    },

    "ultrasonic": {
        "warning": 30.0,
        "danger": 15.0
    },

    "smoke": {
        "warning": 40.0,
        "danger": 70.0
    },

    "vibration": {
        "warning": 0.20,
        "danger": 0.25
    },

    "load": {
        "warning": 7.0,
        "danger": 9.0
    },

    "displacement": {
        "warning": 2.0,
        "danger": 3.0
    }

}


# =========================================================
# GET CURRENT TIME
# =========================================================

def get_current_time():

    return datetime.now().strftime(
        "%H:%M:%S"
    )


# =========================================================
# GET SENSOR STATUS
#
# Returns:
# NORMAL
# WARNING
# HIGH
#
# Ultrasonic is different:
# smaller distance = higher risk
# =========================================================

def get_sensor_status(
    sensor,
    value
):

    try:

        value = float(value)

    except (
        ValueError,
        TypeError
    ):

        return "UNKNOWN"


    threshold = THRESHOLDS.get(
        sensor
    )


    if not threshold:

        return "UNKNOWN"


    # -----------------------------------------------------
    # ULTRASONIC
    #
    # Smaller distance is more dangerous.
    # -----------------------------------------------------

    if sensor == "ultrasonic":

        if value <= threshold["danger"]:

            return "HIGH"

        elif value <= threshold["warning"]:

            return "WARNING"

        else:

            return "NORMAL"


    # -----------------------------------------------------
    # NORMAL SENSOR LOGIC
    #
    # Higher value = higher risk.
    # -----------------------------------------------------

    if value >= threshold["danger"]:

        return "HIGH"

    elif value >= threshold["warning"]:

        return "WARNING"

    else:

        return "NORMAL"


# =========================================================
# GET STATUS OF ALL 7 SENSORS
# =========================================================

def get_all_statuses():

    return {

        "soil": get_sensor_status(
            "soil",
            sensor_data["soil"]
        ),

        "tilt": get_sensor_status(
            "tilt",
            sensor_data["tilt"]
        ),

        "ultrasonic": get_sensor_status(
            "ultrasonic",
            sensor_data["ultrasonic"]
        ),

        "smoke": get_sensor_status(
            "smoke",
            sensor_data["smoke"]
        ),

        "vibration": get_sensor_status(
            "vibration",
            sensor_data["vibration"]
        ),

        "load": get_sensor_status(
            "load",
            sensor_data["load"]
        ),

        "displacement": get_sensor_status(
            "displacement",
            sensor_data["displacement"]
        )

    }


# =========================================================
# CALCULATE OVERALL RISK
#
# Prototype/demo risk scoring.
#
# Each sensor contributes:
#
# NORMAL  = 0
# WARNING = 1
# HIGH    = 3
#
# Overall:
#
# 0-1   = LOW
# 2-5   = MEDIUM
# 6+    = HIGH
# =========================================================

def calculate_risk():

    statuses = get_all_statuses()

    risk_score = 0


    for status in statuses.values():

        if status == "WARNING":

            risk_score += 1

        elif status == "HIGH":

            risk_score += 3


    if risk_score >= 6:

        risk = "HIGH"

    elif risk_score >= 2:

        risk = "MEDIUM"

    else:

        risk = "LOW"


    return risk


# =========================================================
# CREATE SENSOR RESPONSE
#
# This is the main response sent to JavaScript.
# =========================================================

def get_sensor_response():

    statuses = get_all_statuses()

    risk = calculate_risk()


    return {

        "success": True,

        "data": sensor_data.copy(),

        "statuses": statuses,

        "risk": risk,

        "buzzer": buzzer_state,

        "time": get_current_time()

    }


# =========================================================
# HOME PAGE
# =========================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


# =========================================================
# FRONTEND FILES
#
# CSS / JS / images etc.
# =========================================================

@app.route(
    "/<path:filename>"
)
def frontend_files(filename):

    return send_from_directory(
        FRONTEND_FOLDER,
        filename
    )


# =========================================================
# GET SENSOR DATA
#
# GET /api/sensors
# =========================================================

@app.route(
    "/api/sensors",
    methods=["GET"]
)
def get_sensors():

    return jsonify(
        get_sensor_response()
    )


# =========================================================
# UPDATE SENSOR DATA
#
# POST /api/sensors
#
# Example:
#
# {
#     "soil": 65,
#     "tilt": 2.3,
#     "ultrasonic": 25,
#     "smoke": 45,
#     "vibration": 0.21,
#     "load": 7.5,
#     "displacement": 2.5
# }
# =========================================================

@app.route(
    "/api/sensors",
    methods=["POST"]
)
def update_sensors():

    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "No sensor data received"

        }), 400


    try:

        # -------------------------------------------------
        # SOIL
        # -------------------------------------------------

        if "soil" in data:

            sensor_data["soil"] = float(
                data["soil"]
            )


        # -------------------------------------------------
        # SOIL ALIAS
        # -------------------------------------------------

        elif "moisture" in data:

            sensor_data["soil"] = float(
                data["moisture"]
            )


        # -------------------------------------------------
        # TILT
        # -------------------------------------------------

        if "tilt" in data:

            sensor_data["tilt"] = float(
                data["tilt"]
            )


        # -------------------------------------------------
        # ULTRASONIC
        # -------------------------------------------------

        if "ultrasonic" in data:

            sensor_data["ultrasonic"] = float(
                data["ultrasonic"]
            )


        # -------------------------------------------------
        # DISTANCE ALIAS
        # -------------------------------------------------

        elif "distance" in data:

            sensor_data["ultrasonic"] = float(
                data["distance"]
            )


        # -------------------------------------------------
        # SMOKE
        # -------------------------------------------------

        if "smoke" in data:

            sensor_data["smoke"] = float(
                data["smoke"]
            )


        # -------------------------------------------------
        # VIBRATION
        # -------------------------------------------------

        if "vibration" in data:

            sensor_data["vibration"] = float(
                data["vibration"]
            )


        # -------------------------------------------------
        # LOAD
        # -------------------------------------------------

        if "load" in data:

            sensor_data["load"] = float(
                data["load"]
            )


        # -------------------------------------------------
        # WEIGHT ALIAS
        # -------------------------------------------------

        elif "weight" in data:

            sensor_data["load"] = float(
                data["weight"]
            )


        # -------------------------------------------------
        # DISPLACEMENT
        # -------------------------------------------------

        if "displacement" in data:

            sensor_data["displacement"] = float(
                data["displacement"]
            )


        # -------------------------------------------------
        # GROUND DISPLACEMENT ALIAS
        # -------------------------------------------------

        elif "ground_displacement" in data:

            sensor_data["displacement"] = float(
                data["ground_displacement"]
            )


    except (
        ValueError,
        TypeError
    ):

        return jsonify({

            "success": False,

            "message":
                "Sensor values must be numbers"

        }), 400


    response = get_sensor_response()


    response["message"] = (
        "Sensor data updated successfully"
    )


    return jsonify(response)


# =========================================================
# SIMULATE SENSOR DATA
#
# Useful for testing the dashboard before hardware
# is connected.
#
# GET /api/simulate
# =========================================================

@app.route(
    "/api/simulate",
    methods=["GET"]
)
def simulate():

    sensor_data["soil"] = round(
        random.uniform(
            30.0,
            90.0
        ),
        2
    )


    sensor_data["tilt"] = round(
        random.uniform(
            1.0,
            3.5
        ),
        2
    )


    sensor_data["ultrasonic"] = round(
        random.uniform(
            10.0,
            60.0
        ),
        2
    )


    sensor_data["smoke"] = round(
        random.uniform(
            10.0,
            90.0
        ),
        2
    )


    sensor_data["vibration"] = round(
        random.uniform(
            0.10,
            0.30
        ),
        2
    )


    sensor_data["load"] = round(
        random.uniform(
            3.0,
            10.0
        ),
        2
    )


    sensor_data["displacement"] = round(
        random.uniform(
            1.0,
            4.0
        ),
        2
    )


    response = get_sensor_response()


    response["message"] = (
        "Demo sensor data generated"
    )


    return jsonify(response)


# =========================================================
# RESET SENSOR DATA
#
# GET /api/reset
# =========================================================

@app.route(
    "/api/reset",
    methods=["GET"]
)
def reset_sensors():

    global buzzer_state


    sensor_data["soil"] = 42.0

    sensor_data["tilt"] = 1.8

    sensor_data["ultrasonic"] = 45.0

    sensor_data["smoke"] = 20.0

    sensor_data["vibration"] = 0.18

    sensor_data["load"] = 5.0

    sensor_data["displacement"] = 2.4


    buzzer_state = "OFF"


    response = get_sensor_response()


    response["message"] = (
        "Sensor data reset successfully"
    )


    return jsonify(response)


# =========================================================
# GET BUZZER STATE
#
# GET /api/buzzer
# =========================================================

@app.route(
    "/api/buzzer",
    methods=["GET"]
)
def get_buzzer():

    return jsonify({

        "success": True,

        "buzzer": buzzer_state,

        "time": get_current_time()

    })


# =========================================================
# CONTROL BUZZER
#
# POST /api/buzzer
#
# Request:
#
# {
#     "state": "ON"
# }
#
# OR
#
# {
#     "state": "OFF"
# }
# =========================================================

@app.route(
    "/api/buzzer",
    methods=["POST"]
)
def control_buzzer():

    global buzzer_state


    data = request.get_json(
        silent=True
    )


    if not data:

        return jsonify({

            "success": False,

            "message":
                "No buzzer command received"

        }), 400


    state = data.get(
        "state"
    )


    if state is None:

        return jsonify({

            "success": False,

            "message":
                "Buzzer state is required"

        }), 400


    state = str(
        state
    ).upper()


    if state not in [
        "ON",
        "OFF"
    ]:

        return jsonify({

            "success": False,

            "message":
                "Buzzer state must be ON or OFF"

        }), 400


    buzzer_state = state


    return jsonify({

        "success": True,

        "message":
            f"Buzzer turned {buzzer_state}",

        "buzzer":
            buzzer_state,

        "time":
            get_current_time()

    })


# =========================================================
# HEALTH CHECK
#
# GET /api/health
# =========================================================

@app.route(
    "/api/health",
    methods=["GET"]
)
def health():

    return jsonify({

        "success": True,

        "server":
            "Mine Security AI Backend",

        "status":
            "running",

        "time":
            get_current_time()

    })


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))

    print("--------------------------------------------")
    print(" Mine Security AI Backend")
    print(" AI Mine Subsidence Monitoring System")
    print("--------------------------------------------")
    print(f"Server running on port: {port}")
    print("--------------------------------------------")

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )