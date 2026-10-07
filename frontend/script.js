/* =========================================================
   MINE SECURITY AI
   FRONTEND JAVASCRIPT
   ========================================================= */


/* =========================================================
   API
   ========================================================= */

const API_URL = "/api/sensors";
const BUZZER_API_URL = "/api/buzzer";

const REFRESH_INTERVAL = 5000;


/* =========================================================
   GLOBAL DATA
   ========================================================= */

let recentReadings = [];


/* =========================================================
   GET ELEMENT
   ========================================================= */

function getElement(id) {

    return document.getElementById(id);

}


/* =========================================================
   CONNECTION STATUS
   ========================================================= */

function updateConnectionStatus(connected) {

    const element =
        getElement("connectionStatus");

    if (element) {

        if (connected) {

            element.innerText =
                "● ONLINE";

            element.className =
                "status-online";

        }
        else {

            element.innerText =
                "● OFFLINE";

            element.className =
                "status-offline";

        }

    }


    const summary =
        getElement("summaryConnection");

    if (summary) {

        summary.innerText =
            connected ? "Online" : "Offline";

    }


    const backend =
        getElement("backendStatus");

    if (backend) {

        backend.innerText =
            connected
                ? "● Connected"
                : "● Offline";

    }

}


/* =========================================================
   GET SENSOR VALUE
   ========================================================= */

function getSensorValue(data, keys) {

    if (!data) {

        return "--";

    }


    for (const key of keys) {

        if (
            data[key] !== undefined &&
            data[key] !== null
        ) {

            return data[key];

        }

    }


    return "--";

}


/* =========================================================
   FORMAT NUMBER
   ========================================================= */

function formatNumber(value) {

    if (
        value === undefined ||
        value === null ||
        value === "--" ||
        value === ""
    ) {

        return "--";

    }


    const number =
        Number(value);


    if (Number.isNaN(number)) {

        return "--";

    }


    return number.toFixed(2);

}


/* =========================================================
   BACKEND SENSOR STATUS
   ========================================================= */

function applyBackendStatus(id, status) {

    const element =
        getElement(id);


    if (!element || !status) {

        return;

    }


    const normalized =
        String(status).toUpperCase();


    if (
        normalized === "HIGH" ||
        normalized === "DANGER"
    ) {

        element.innerText =
            "High";

        element.className =
            "card-status danger-status";

    }

    else if (
        normalized === "WARNING" ||
        normalized === "MEDIUM"
    ) {

        element.innerText =
            "Warning";

        element.className =
            "card-status warning-status";

    }

    else {

        element.innerText =
            "Normal";

        element.className =
            "card-status normal";

    }

}


/* =========================================================
   FRONTEND FALLBACK STATUS
   ========================================================= */

function updateSensorStatus(
    id,
    value,
    warning,
    danger
) {

    const element =
        getElement(id);


    if (!element) {

        return;

    }


    const number =
        Number(value);


    if (Number.isNaN(number)) {

        element.innerText =
            "Normal";

        element.className =
            "card-status normal";

        return;

    }


    if (number >= danger) {

        element.innerText =
            "High";

        element.className =
            "card-status danger-status";

    }

    else if (number >= warning) {

        element.innerText =
            "Warning";

        element.className =
            "card-status warning-status";

    }

    else {

        element.innerText =
            "Normal";

        element.className =
            "card-status normal";

    }

}


/* =========================================================
   ULTRASONIC STATUS
   LOWER DISTANCE = HIGHER RISK
   ========================================================= */

function updateDistanceStatus(
    id,
    value,
    warning,
    danger
) {

    const element =
        getElement(id);


    if (!element) {

        return;

    }


    const number =
        Number(value);


    if (Number.isNaN(number)) {

        element.innerText =
            "Normal";

        element.className =
            "card-status normal";

        return;

    }


    if (number <= danger) {

        element.innerText =
            "High";

        element.className =
            "card-status danger-status";

    }

    else if (number <= warning) {

        element.innerText =
            "Warning";

        element.className =
            "card-status warning-status";

    }

    else {

        element.innerText =
            "Normal";

        element.className =
            "card-status normal";

    }

}


/* =========================================================
   UPDATE SENSOR CARDS
   ========================================================= */

function updateSensorCards(
    data,
    statuses = {}
) {

    console.log(
        "Updating sensor cards:",
        data
    );


    /* =====================================================
       SOIL
       ===================================================== */

    const soil =
        getSensorValue(
            data,
            [
                "soil",
                "soil_moisture",
                "moisture"
            ]
        );


    const soilElement =
        getElement("soil");


    if (soilElement) {

        soilElement.innerText =
            formatNumber(soil);

    }


    if (statuses.soil) {

        applyBackendStatus(
            "soilStatus",
            statuses.soil
        );

    }
    else {

        updateSensorStatus(
            "soilStatus",
            soil,
            60,
            80
        );

    }


    /* =====================================================
       TILT
       ===================================================== */

    const tilt =
        getSensorValue(
            data,
            [
                "tilt",
                "mpu6050",
                "tilt_angle",
                "angle"
            ]
        );


    const tiltElement =
        getElement("tilt");


    if (tiltElement) {

        tiltElement.innerText =
            formatNumber(tilt);

    }


    if (statuses.tilt) {

        applyBackendStatus(
            "tiltStatus",
            statuses.tilt
        );

    }
    else {

        updateSensorStatus(
            "tiltStatus",
            tilt,
            2.0,
            3.0
        );

    }


    /* =====================================================
       ULTRASONIC
       ===================================================== */

    const ultrasonic =
        getSensorValue(
            data,
            [
                "ultrasonic",
                "distance",
                "ultrasonic_distance"
            ]
        );


    const ultrasonicElement =
        getElement("ultrasonic");


    if (ultrasonicElement) {

        ultrasonicElement.innerText =
            formatNumber(ultrasonic);

    }


    if (statuses.ultrasonic) {

        applyBackendStatus(
            "ultrasonicStatus",
            statuses.ultrasonic
        );

    }
    else {

        updateDistanceStatus(
            "ultrasonicStatus",
            ultrasonic,
            30,
            15
        );

    }


    /* =====================================================
       SMOKE
       ===================================================== */

    const smoke =
        getSensorValue(
            data,
            [
                "smoke",
                "smoke_level",
                "smoke_sensor",
                "gas"
            ]
        );


    const smokeElement =
        getElement("smoke");


    if (smokeElement) {

        smokeElement.innerText =
            formatNumber(smoke);

    }


    if (statuses.smoke) {

        applyBackendStatus(
            "smokeStatus",
            statuses.smoke
        );

    }
    else {

        updateSensorStatus(
            "smokeStatus",
            smoke,
            40,
            70
        );

    }


    /* =====================================================
       VIBRATION
       ===================================================== */

    const vibration =
        getSensorValue(
            data,
            [
                "vibration",
                "vibration_value"
            ]
        );


    const vibrationElement =
        getElement("vibration");


    if (vibrationElement) {

        vibrationElement.innerText =
            formatNumber(vibration);

    }


    if (statuses.vibration) {

        applyBackendStatus(
            "vibrationStatus",
            statuses.vibration
        );

    }
    else {

        updateSensorStatus(
            "vibrationStatus",
            vibration,
            0.20,
            0.25
        );

    }


    /* =====================================================
       LOAD
       ===================================================== */

    const load =
        getSensorValue(
            data,
            [
                "load",
                "load_value",
                "weight",
                "load_weight"
            ]
        );


    const loadElement =
        getElement("load");


    if (loadElement) {

        loadElement.innerText =
            formatNumber(load);

    }


    if (statuses.load) {

        applyBackendStatus(
            "loadStatus",
            statuses.load
        );

    }
    else {

        updateSensorStatus(
            "loadStatus",
            load,
            7,
            9
        );

    }


    /* =====================================================
       GROUND DISPLACEMENT
       ===================================================== */

    const displacement =
        getSensorValue(
            data,
            [
                "displacement",
                "ground_displacement"
            ]
        );


    const displacementElement =
        getElement("displacement");


    if (displacementElement) {

        displacementElement.innerText =
            formatNumber(displacement);

    }


    if (statuses.displacement) {

        applyBackendStatus(
            "displacementStatus",
            statuses.displacement
        );

    }
    else {

        updateSensorStatus(
            "displacementStatus",
            displacement,
            2.0,
            3.0
        );

    }


    /* =====================================================
       RETURN DATA
       ===================================================== */

    return {

        soil: soil,

        tilt: tilt,

        ultrasonic: ultrasonic,

        smoke: smoke,

        vibration: vibration,

        load: load,

        displacement: displacement

    };

}


/* =========================================================
   UPDATE RISK
   ========================================================= */

function updateRisk(risk) {

    const riskBox =
        getElement("riskBox");

    const riskLevel =
        getElement("riskLevel");

    const riskMessage =
        getElement("riskMessage");

    const summaryRisk =
        getElement("summaryRisk");

    const alertTitle =
        getElement("alertTitle");

    const alertMessage =
        getElement("alertMessage");

    const predictionStatus =
        getElement("predictionStatus");

    const predictionMovement =
        getElement("predictionMovement");


    const currentRisk =
        String(
            risk || "LOW"
        ).toUpperCase();


    if (currentRisk === "HIGH") {

        if (riskLevel) {

            riskLevel.innerText =
                "HIGH";

        }


        if (riskBox) {

            riskBox.className =
                "risk risk-high";

        }


        if (riskMessage) {

            riskMessage.innerText =
                "Sensor readings indicate a high-risk condition.";

        }


        if (summaryRisk) {

            summaryRisk.innerText =
                "HIGH";

        }


        if (alertTitle) {

            alertTitle.innerText =
                "🚨 Alert";

        }


        if (alertMessage) {

            alertMessage.innerText =
                "High-risk sensor readings detected.";

        }


        if (predictionStatus) {

            predictionStatus.innerText =
                "Attention Required";

        }


        if (predictionMovement) {

            predictionMovement.innerText =
                "High probability";

        }

    }

    else if (
        currentRisk === "MEDIUM" ||
        currentRisk === "WARNING"
    ) {

        if (riskLevel) {

            riskLevel.innerText =
                "MEDIUM";

        }


        if (riskBox) {

            riskBox.className =
                "risk risk-medium";

        }


        if (riskMessage) {

            riskMessage.innerText =
                "Abnormal sensor conditions are being monitored.";

        }


        if (summaryRisk) {

            summaryRisk.innerText =
                "MEDIUM";

        }


        if (alertTitle) {

            alertTitle.innerText =
                "⚠ Warning";

        }


        if (alertMessage) {

            alertMessage.innerText =
                "Abnormal sensor conditions are being monitored.";

        }


        if (predictionStatus) {

            predictionStatus.innerText =
                "Monitor";

        }


        if (predictionMovement) {

            predictionMovement.innerText =
                "Moderate probability";

        }

    }

    else {

        if (riskLevel) {

            riskLevel.innerText =
                "LOW";

        }


        if (riskBox) {

            riskBox.className =
                "risk risk-low";

        }


        if (riskMessage) {

            riskMessage.innerText =
                "Current ground condition is within monitored limits.";

        }


        if (summaryRisk) {

            summaryRisk.innerText =
                "LOW";

        }


        if (alertTitle) {

            alertTitle.innerText =
                "AI Prediction";

        }


        if (alertMessage) {

            alertMessage.innerText =
                "No critical subsidence pattern detected at present.";

        }


        if (predictionStatus) {

            predictionStatus.innerText =
                "Stable";

        }


        if (predictionMovement) {

            predictionMovement.innerText =
                "Low probability";

        }

    }

}


/* =========================================================
   UPDATE BUZZER
   ========================================================= */

function updateBuzzerUI(state) {

    const element =
        getElement("buzzerStatus");


    if (!element) {

        return;

    }


    const normalized =
        String(
            state || "OFF"
        ).toUpperCase();


    element.innerText =
        normalized;


    if (normalized === "ON") {

        element.className =
            "buzzer-on";

    }
    else {

        element.className =
            "buzzer-off";

    }

}


/* =========================================================
   BUZZER CONTROL
   ========================================================= */

async function setBuzzer(state) {

    try {

        const response =
            await fetch(
                BUZZER_API_URL,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            state: state
                        })
                }
            );


        const result =
            await response.json();


        if (!response.ok) {

            throw new Error(
                result.message ||
                "Buzzer request failed"
            );

        }


        updateBuzzerUI(
            result.buzzer
        );


        console.log(
            "Buzzer:",
            result
        );

    }

    catch (error) {

        console.error(
            "Buzzer error:",
            error
        );

    }

}


/* =========================================================
   RECENT SENSOR READING
   ========================================================= */

function addRecentReading(
    data,
    risk,
    time
) {

    const table =
        getElement(
            "readingsTable"
        );


    if (!table) {

        return;

    }


    const reading = {

        time:
            time ||
            new Date().toLocaleTimeString(),

        displacement:
            data.displacement,

        vibration:
            data.vibration,

        tilt:
            data.tilt,

        risk:
            risk || "LOW"

    };


    recentReadings.unshift(
        reading
    );


    if (
        recentReadings.length > 5
    ) {

        recentReadings.pop();

    }


    table.innerHTML =
        "";


    recentReadings.forEach(
        function (item) {

            const row =
                document.createElement(
                    "tr"
                );


            let riskClass =
                "safe";

            let riskText =
                "SAFE";


            const currentRisk =
                String(
                    item.risk
                ).toUpperCase();


            if (
                currentRisk === "MEDIUM" ||
                currentRisk === "WARNING"
            ) {

                riskClass =
                    "warning";

                riskText =
                    "WARNING";

            }


            if (
                currentRisk === "HIGH" ||
                currentRisk === "DANGER"
            ) {

                riskClass =
                    "danger";

                riskText =
                    "HIGH";

            }


            row.innerHTML = `

                <td>
                    ${item.time}
                </td>

                <td>
                    Node 01
                </td>

                <td>
                    ${formatNumber(item.displacement)} mm
                </td>

                <td>
                    ${formatNumber(item.vibration)} g
                </td>

                <td>
                    ${formatNumber(item.tilt)}°
                </td>

                <td>
                    <span class="table-status ${riskClass}">
                        ${riskText}
                    </span>
                </td>

            `;


            table.appendChild(
                row
            );

        }
    );

}


/* =========================================================
   REFRESH DATA
   ========================================================= */

async function refreshData() {

    const refreshButton =
        getElement(
            "refreshButton"
        );


    try {

        console.log(
            "Requesting sensor data..."
        );


        if (refreshButton) {

            refreshButton.disabled =
                true;

            refreshButton.innerText =
                "Updating...";

        }


        /* =====================================================
           GET DATA FROM FLASK
           ===================================================== */

        const response =
            await fetch(
                API_URL,
                {
                    method: "GET",
                    cache: "no-store"
                }
            );


        console.log(
            "API response:",
            response.status
        );


        if (!response.ok) {

            throw new Error(
                "HTTP " +
                response.status
            );

        }


        /* =====================================================
           JSON
           ===================================================== */

        const result =
            await response.json();


        console.log(
            "Backend JSON:",
            result
        );


        if (
            result.success !== true
        ) {

            throw new Error(
                "Backend returned unsuccessful response"
            );

        }


        /* =====================================================
           SENSOR DATA
           ===================================================== */

        const data =
            result.data || {};


        /* =====================================================
           UPDATE ALL 7 SENSOR CARDS
           ===================================================== */

        const sensorData =
            updateSensorCards(
                data,
                result.statuses || {}
            );


        /* =====================================================
           UPDATE RISK
           ===================================================== */

        updateRisk(
            result.risk
        );


        /* =====================================================
           UPDATE BUZZER
           ===================================================== */

        if (
            result.buzzer !== undefined
        ) {

            updateBuzzerUI(
                result.buzzer
            );

        }


        /* =====================================================
           LAST UPDATED
           ===================================================== */

        const lastUpdated =
            getElement(
                "lastUpdated"
            );


        if (lastUpdated) {

            lastUpdated.innerText =
                result.time ||
                new Date().toLocaleTimeString();

        }


        /* =====================================================
           RECENT READING
           ===================================================== */

        addRecentReading(
            sensorData,
            result.risk,
            result.time
        );


        /* =====================================================
           CONNECTION
           ===================================================== */

        updateConnectionStatus(
            true
        );


        console.log(
            "Dashboard updated successfully."
        );

    }


    catch (error) {

        console.error(
            "ERROR:",
            error
        );


        updateConnectionStatus(
            false
        );

    }


    finally {

        if (refreshButton) {

            refreshButton.disabled =
                false;

            refreshButton.innerText =
                "Refresh Data";

        }

    }

}


/* =========================================================
   START DASHBOARD
   ========================================================= */

function startDashboard() {

    console.log(
        "Mine Security AI Dashboard started."
    );


    refreshData();


    setInterval(
        refreshData,
        REFRESH_INTERVAL
    );

}


/* =========================================================
   PAGE LOAD
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        startDashboard();

    }
);