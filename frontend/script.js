/* =========================================================
   BHOOMIRAKSHAK - FRONTEND JAVASCRIPT

   This file:
   1. Gets data from Flask
   2. Updates sensor cards
   3. Updates risk
   4. Updates connection status
   5. Adds recent readings
   ========================================================= */


/* ================= FLASK API URL ================= */

const API_URL = "http://127.0.0.1:5000/api/sensors";


/* ================= SETTINGS ================= */

// Dashboard refresh interval
// 5000 = 5 seconds
const REFRESH_INTERVAL = 5000;


/* ================= READING HISTORY ================= */

// Stores recent dashboard readings
let recentReadings = [];


/* ================= GET ELEMENT ================= */

function getElement(id) {

    return document.getElementById(id);

}


/* ================= UPDATE CONNECTION ================= */

function updateConnectionStatus(online) {

    const status = getElement("connectionStatus");
    const backendStatus = getElement("backendStatus");
    const summaryConnection = getElement("summaryConnection");

    if (online) {

        status.innerText = "● ONLINE";

        status.className = "status-online";

        backendStatus.innerText = "● Connected";

        backendStatus.className = "info-status";

        summaryConnection.innerText = "Online";

    } else {

        status.innerText = "● OFFLINE";

        status.className = "status-offline";

        backendStatus.innerText = "● Disconnected";

        backendStatus.className = "info-status offline-text";

        summaryConnection.innerText = "Offline";

    }

}


/* ================= UPDATE SENSOR STATUS ================= */

function updateSensorStatus(id, value, warningLimit, dangerLimit) {

    const element = getElement(id);

    if (!element) {
        return;
    }


    if (value >= dangerLimit) {

        element.innerText = "High";

        element.className = "card-status danger-status";

    } else if (value >= warningLimit) {

        element.innerText = "Warning";

        element.className = "card-status warning-status";

    } else {

        element.innerText = "Normal";

        element.className = "card-status normal";

    }

}


/* ================= UPDATE RISK ================= */

function updateRisk(risk) {

    const riskLevel = getElement("riskLevel");
    const riskBox = getElement("riskBox");
    const riskMessage = getElement("riskMessage");

    const summaryRisk = getElement("summaryRisk");

    const alertTitle = getElement("alertTitle");
    const alertMessage = getElement("alertMessage");

    const predictionStatus = getElement("predictionStatus");
    const predictionMovement = getElement("predictionMovement");


    if (!risk) {
        return;
    }


    // Convert to uppercase
    risk = String(risk).toUpperCase();


    /* ---------- LOW ---------- */

    if (risk === "LOW" || risk === "SAFE") {

        riskLevel.innerText = "LOW";

        riskBox.className = "risk risk-low";

        riskMessage.innerText =
            "Current ground condition is within monitored limits.";

        summaryRisk.innerText = "LOW";

        summaryRisk.style.color = "#166534";

        alertTitle.innerText = "AI Prediction";

        alertMessage.innerText =
            "No critical subsidence pattern detected at present.";

        predictionStatus.innerText = "Stable";

        predictionStatus.className = "prediction-stable";

        predictionMovement.innerText = "Low probability";

    }


    /* ---------- MEDIUM ---------- */

    else if (risk === "MEDIUM" || risk === "WARNING") {

        riskLevel.innerText = "MEDIUM";

        riskBox.className = "risk risk-medium";

        riskMessage.innerText =
            "Some monitored parameters require attention.";

        summaryRisk.innerText = "MEDIUM";

        summaryRisk.style.color = "#92400e";

        alertTitle.innerText = "⚠ Warning";

        alertMessage.innerText =
            "Abnormal sensor conditions are being monitored.";

        predictionStatus.innerText = "Monitor";

        predictionStatus.className = "";

        predictionMovement.innerText = "Moderate probability";

    }


    /* ---------- HIGH ---------- */

    else if (risk === "HIGH" || risk === "DANGER") {

        riskLevel.innerText = "HIGH";

        riskBox.className = "risk risk-high";

        riskMessage.innerText =
            "Sensor readings indicate a high-risk condition.";

        summaryRisk.innerText = "HIGH";

        summaryRisk.style.color = "#991b1b";

        alertTitle.innerText = "🚨 Alert";

        alertMessage.innerText =
            "High-risk sensor readings detected. Immediate monitoring is recommended.";

        predictionStatus.innerText = "Attention Required";

        predictionStatus.className = "";

        predictionMovement.innerText = "High probability";

    }

}


/* ================= ADD RECENT READING ================= */

function addRecentReading(data, risk, time) {

    const table = getElement("readingsTable");


    // Create a new reading
    const reading = {

        time: time,

        node: "Node 01",

        displacement: data.displacement,

        vibration: data.vibration,

        tilt: data.tilt,

        risk: risk

    };


    // Add latest reading at beginning
    recentReadings.unshift(reading);


    // Keep only 5 readings
    if (recentReadings.length > 5) {

        recentReadings.pop();

    }


    // Clear table
    table.innerHTML = "";


    // Create table rows
    recentReadings.forEach(function (item) {

        const row = document.createElement("tr");


        let riskClass = "safe";

        let riskText = "SAFE";


        const currentRisk = String(item.risk).toUpperCase();


        if (
            currentRisk === "MEDIUM" ||
            currentRisk === "WARNING"
        ) {

            riskClass = "warning";

            riskText = "WARNING";

        }


        if (
            currentRisk === "HIGH" ||
            currentRisk === "DANGER"
        ) {

            riskClass = "danger";

            riskText = "HIGH";

        }


        row.innerHTML = `

            <td>${item.time}</td>

            <td>${item.node}</td>

            <td>${formatNumber(item.displacement)} mm</td>

            <td>${formatNumber(item.vibration)} g</td>

            <td>${formatNumber(item.tilt)}°</td>

            <td>
                <span class="table-status ${riskClass}">
                    ${riskText}
                </span>
            </td>

        `;


        table.appendChild(row);

    });

}


/* ================= FORMAT NUMBER ================= */

function formatNumber(value) {

    const number = Number(value);


    if (Number.isNaN(number)) {

        return "--";

    }


    return number.toFixed(2);

}


/* ================= REFRESH DATA ================= */

async function refreshData() {

    const refreshButton = getElement("refreshButton");


    try {

        // Disable button during request
        refreshButton.disabled = true;

        refreshButton.innerText = "Updating...";


        // Request data from Flask
        const response = await fetch(API_URL);


        // Check HTTP response
        if (!response.ok) {

            throw new Error(
                "Flask server returned HTTP " + response.status
            );

        }


        // Convert response to JSON
        const result = await response.json();


        // Check returned data
        if (!result.success) {

            throw new Error("Backend returned an error.");

        }


        const data = result.data;


        /* ================= UPDATE SENSOR VALUES ================= */

        getElement("displacement").innerText =
            formatNumber(data.displacement);


        getElement("vibration").innerText =
            formatNumber(data.vibration);


        getElement("tilt").innerText =
            formatNumber(data.tilt);


        getElement("moisture").innerText =
            formatNumber(data.moisture);


        /* ================= UPDATE SENSOR STATUS ================= */

        updateSensorStatus(
            "displacementStatus",
            Number(data.displacement),
            2.0,
            3.0
        );


        updateSensorStatus(
            "vibrationStatus",
            Number(data.vibration),
            0.20,
            0.25
        );


        updateSensorStatus(
            "tiltStatus",
            Number(data.tilt),
            2.0,
            3.0
        );


        updateSensorStatus(
            "moistureStatus",
            Number(data.moisture),
            60,
            80
        );


        /* ================= UPDATE RISK ================= */

        updateRisk(result.risk);


        /* ================= UPDATE TIME ================= */

        let currentTime = result.time;


        if (!currentTime) {

            const now = new Date();

            currentTime = now.toLocaleTimeString();

        }


        getElement("lastUpdated").innerText =
            currentTime;


        /* ================= ADD READING ================= */

        addRecentReading(
            data,
            result.risk,
            currentTime
        );


        /* ================= CONNECTION ================= */

        updateConnectionStatus(true);


        console.log(
            "Sensor data updated successfully:",
            result
        );


    } catch (error) {

        console.error(
            "Backend connection error:",
            error
        );


        updateConnectionStatus(false);

    } finally {

        // Enable button
        refreshButton.disabled = false;

        refreshButton.innerText = "Refresh Data";

    }

}


/* ================= START DASHBOARD ================= */

function startDashboard() {

    // Get initial data
    refreshData();


    // Automatically refresh every 5 seconds
    setInterval(
        refreshData,
        REFRESH_INTERVAL
    );

}


/* ================= PAGE LOAD ================= */

document.addEventListener(
    "DOMContentLoaded",
    startDashboard
);