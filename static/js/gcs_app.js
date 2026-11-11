/**
 * AeroGuard-X1 GCS Application Coordinator.
 * Connects telemetry stream, HUD displays, command actuators, and mission executor.
 */

let pfd = null;
let cameraView = null;
let flightTwin = null;
let eventSource = null;

document.addEventListener("DOMContentLoaded", () => {
  pfd = new PrimaryFlightDisplay("hudCanvas");
  cameraView = new CameraVisionDisplay("cameraCanvas");
  flightTwin = new FlightDigitalTwinDisplay("flightCanvas");

  setupEventListeners();
  initTelemetryStream();
});

function initTelemetryStream() {
  if (!!window.EventSource) {
    eventSource = new EventSource("/api/drone/events");
    eventSource.onmessage = (e) => {
      try {
        const telemetry = JSON.parse(e.data);
        handleTelemetry(telemetry);
      } catch (err) {
        console.error("Telemetry parse error:", err);
      }
    };
    eventSource.onerror = () => {
      console.warn("SSE error, fallback polling active");
    };
  } else {
    // Fallback polling
    setInterval(async () => {
      const res = await fetch("/api/drone/telemetry");
      const telemetry = await res.json();
      handleTelemetry(telemetry);
    }, 100);
  }
}

function handleTelemetry(t) {
  // Update Visual Displays
  pfd.update(t);
  cameraView.update(t);
  flightTwin.update(t);

  // Update Flight Status Banner
  document.getElementById("valFlightMode").textContent = t.flight_status.flight_mode;
  document.getElementById("valArmed").textContent = t.flight_status.armed ? "ARMED" : "DISARMED";
  document.getElementById("valArmed").style.color = t.flight_status.armed ? "#10b981" : "#f43f5e";
  document.getElementById("valMission").textContent = t.flight_status.mission_name;

  // Update Power System
  const pwr = t.power_system;
  document.getElementById("valBatteryPct").textContent = `${pwr.battery_pct.toFixed(0)}%`;
  document.getElementById("batteryBar").style.width = `${pwr.battery_pct}%`;
  document.getElementById("valBatteryV").textContent = `${pwr.battery_voltage_v.toFixed(2)} V`;
  document.getElementById("valBatteryA").textContent = `${pwr.battery_current_a.toFixed(1)} A`;
  document.getElementById("valPowerW").textContent = `${pwr.battery_power_watts.toFixed(0)} W`;

  // Update Motors RPM
  const rpms = t.physics.motors_rpm;
  for (let i = 0; i < 4; i++) {
    const el = document.getElementById(`valMotor${i+1}`);
    if (el) el.textContent = `${Math.round(rpms[i])} RPM`;
  }

  // Update Position & Speed
  const pos = t.physics.position;
  const vel = t.physics.velocity;
  document.getElementById("valAltitude").textContent = `${pos.altitude_m.toFixed(1)} m`;
  document.getElementById("valSpeed").textContent = `${vel.ground_speed_km_h.toFixed(1)} km/h`;
  document.getElementById("valClimb").textContent = `${vel.vz_climb_m_s.toFixed(2)} m/s`;

  // Update AI Detections Feed
  const detList = document.getElementById("aiDetectionList");
  if (detList && t.vision_ai.detections) {
    if (t.vision_ai.detections.length === 0) {
      detList.innerHTML = `<div style="font-size: 0.72rem; color: #64748b; padding: 4px;">Zero targets in current footprint.</div>`;
    } else {
      detList.innerHTML = t.vision_ai.detections.map(d => `
        <div class="detection-badge ${d.class_name === 'thermal_hotspot' ? 'fire' : ''}">
          <div style="font-weight: 700; color: #fff;">${d.target_id}: ${d.class_name.toUpperCase()}</div>
          <div>Dist: ${d.distance_m}m | Conf: ${(d.confidence * 100).toFixed(0)}%</div>
          <div style="color: #94a3b8; font-size: 0.68rem;">Coords: (${d.ground_coords.x}, ${d.ground_coords.y})</div>
        </div>
      `).join("");
    }
  }
}

function setupEventListeners() {
  // Command Buttons
  document.getElementById("btnArm").addEventListener("click", () => sendCommand("ARM"));
  document.getElementById("btnDisarm").addEventListener("click", () => sendCommand("DISARM"));
  document.getElementById("btnTakeoff").addEventListener("click", () => sendCommand("TAKEOFF"));
  document.getElementById("btnLand").addEventListener("click", () => sendCommand("LAND"));
  document.getElementById("btnRtl").addEventListener("click", () => sendCommand("RTL"));

  // Mission Selector
  document.getElementById("btnMissionSar").addEventListener("click", () => loadMission("sar_spiral"));
  document.getElementById("btnMissionAgri").addEventListener("click", () => loadMission("agri_survey"));
  document.getElementById("btnMissionPerimeter").addEventListener("click", () => loadMission("perimeter"));
}

async function sendCommand(command) {
  try {
    await fetch("/api/drone/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command })
    });
  } catch (err) {
    console.error("Failed to send command:", err);
  }
}

async function loadMission(mission_type) {
  try {
    await fetch("/api/drone/mission", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mission_type })
    });
  } catch (err) {
    console.error("Failed to load mission:", err);
  }
}

