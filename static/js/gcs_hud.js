/**
 * Aviation Primary Flight Display (PFD) HUD, Camera Feed, and 3D Flight Canvas.
 */

class PrimaryFlightDisplay {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.roll = 0;   // radians
    this.pitch = 0;  // radians
    this.altitude = 0;
    this.airspeed = 0;
    this.heading = 0;

    this.initSize();
    window.addEventListener("resize", () => this.initSize());
  }

  initSize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  update(telemetry) {
    if (!telemetry || !telemetry.physics) return;
    const att = telemetry.physics.attitude_degrees;
    this.roll = att.roll_deg * (Math.PI / 180.0);
    this.pitch = att.pitch_deg * (Math.PI / 180.0);
    this.altitude = telemetry.physics.position.altitude_m;
    this.airspeed = telemetry.physics.velocity.airspeed_m_s;
    this.heading = att.yaw_deg;
    this.render();
  }

  render() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const cx = w / 2;
    const cy = h / 2;

    ctx.clearRect(0, 0, w, h);

    // 1. Artificial Horizon (Sky & Ground)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-this.roll);

    const pitchOffset = this.pitch * (h * 0.8);
    ctx.translate(0, pitchOffset);

    // Sky
    ctx.fillStyle = "#0c2a4d";
    ctx.fillRect(-w, -h * 2, w * 2, h * 2);

    // Ground
    ctx.fillStyle = "#382410";
    ctx.fillRect(-w, 0, w * 2, h * 2);

    // Horizon line
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-w, 0);
    ctx.lineTo(w, 0);
    ctx.stroke();

    // Pitch Ladder
    ctx.strokeStyle = "rgba(255, 255, 255, 0.7)";
    ctx.fillStyle = "rgba(255, 255, 255, 0.9)";
    ctx.font = "9px monospace";
    ctx.textAlign = "right";

    const pitchStepPx = (10 * Math.PI / 180) * (h * 0.8);
    for (let deg = -30; deg <= 30; deg += 10) {
      if (deg === 0) continue;
      const py = -deg * (pitchStepPx / 10);
      const barW = deg % 20 === 0 ? 35 : 20;

      ctx.beginPath();
      ctx.moveTo(-barW, py);
      ctx.lineTo(-barW / 3, py);
      ctx.moveTo(barW / 3, py);
      ctx.lineTo(barW, py);
      ctx.stroke();

      ctx.fillText(`${deg}°`, -barW - 4, py + 3);
    }
    ctx.restore();

    // 2. Fixed Aircraft Symbol (Reticle)
    ctx.strokeStyle = "#f59e0b";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(cx - 30, cy);
    ctx.lineTo(cx - 10, cy);
    ctx.lineTo(cx - 10, cy + 6);
    ctx.moveTo(cx + 10, cy + 6);
    ctx.lineTo(cx + 10, cy);
    ctx.lineTo(cx + 30, cy);
    ctx.stroke();

    ctx.fillStyle = "#f59e0b";
    ctx.beginPath();
    ctx.arc(cx, cy, 3, 0, Math.PI * 2);
    ctx.fill();

    // 3. Airspeed Tape (Left)
    ctx.fillStyle = "rgba(11, 19, 36, 0.75)";
    ctx.fillRect(4, 20, 48, h - 40);
    ctx.strokeStyle = "#1e2f4f";
    ctx.strokeRect(4, 20, 48, h - 40);

    ctx.fillStyle = "#38bdf8";
    ctx.font = "bold 11px monospace";
    ctx.textAlign = "center";
    ctx.fillText(`${this.airspeed.toFixed(1)}`, 28, cy - 2);
    ctx.font = "8px sans-serif";
    ctx.fillStyle = "#94a3b8";
    ctx.fillText("m/s", 28, cy + 10);

    // 4. Altitude Tape (Right)
    ctx.fillStyle = "rgba(11, 19, 36, 0.75)";
    ctx.fillRect(w - 52, 20, 48, h - 40);
    ctx.strokeRect(w - 52, 20, 48, h - 40);

    ctx.fillStyle = "#10b981";
    ctx.font = "bold 11px monospace";
    ctx.textAlign = "center";
    ctx.fillText(`${this.altitude.toFixed(1)}`, w - 28, cy - 2);
    ctx.font = "8px sans-serif";
    ctx.fillStyle = "#94a3b8";
    ctx.fillText("ALT (m)", w - 28, cy + 10);

    // 5. Heading Compass
    ctx.fillStyle = "#fff";
    ctx.font = "10px monospace";
    ctx.fillText(`HDG: ${Math.round((this.heading + 360) % 360)}°`, cx, h - 8);
  }
}

class CameraVisionDisplay {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.detections = [];

    this.initSize();
    window.addEventListener("resize", () => this.initSize());
  }

  initSize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  update(telemetry) {
    if (!telemetry || !telemetry.vision_ai) return;
    this.detections = telemetry.vision_ai.detections || [];
    this.render();
  }

  render() {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;

    // Simulated terrain camera view (dark ground gradient)
    const grad = ctx.createLinearGradient(0, 0, w, h);
    grad.addColorStop(0, "#1e293b");
    grad.addColorStop(1, "#0f172a");
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);

    // Subtle terrain texture
    ctx.strokeStyle = "rgba(255, 255, 255, 0.03)";
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 25) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }

    // Crosshair in center
    ctx.strokeStyle = "rgba(255, 255, 255, 0.3)";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(w / 2 - 15, h / 2);
    ctx.lineTo(w / 2 + 15, h / 2);
    ctx.moveTo(w / 2, h / 2 - 15);
    ctx.lineTo(w / 2, h / 2 + 15);
    ctx.stroke();

    // Draw AI Bounding Boxes
    this.detections.forEach(det => {
      const [ymin, xmin, ymax, xmax] = det.bbox_norm;
      const bx = xmin * w;
      const by = ymin * h;
      const bw = (xmax - xmin) * w;
      const bh = (ymax - ymin) * h;

      const isFire = det.class_name === "thermal_hotspot";
      const isCrop = det.class_name === "crop_field";
      const color = isFire ? "#f43f5e" : (isCrop ? "#a855f7" : "#10b981");

      // Bounding box
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.strokeRect(bx, by, bw, bh);

      // Label badge
      ctx.fillStyle = color;
      ctx.fillRect(bx, by - 16, Math.max(70, bw), 16);
      ctx.fillStyle = "#000";
      ctx.font = "bold 9px sans-serif";
      ctx.textAlign = "left";
      ctx.fillText(`${det.class_name.toUpperCase()} ${(det.confidence * 100).toFixed(0)}%`, bx + 4, by - 4);
    });

    if (this.detections.length === 0) {
      ctx.fillStyle = "rgba(255, 255, 255, 0.4)";
      ctx.font = "10px monospace";
      ctx.textAlign = "center";
      ctx.fillText("Scanning ground area (FOV Active)...", w / 2, h - 14);
    }
  }
}

class FlightDigitalTwinDisplay {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    this.ctx = this.canvas.getContext("2d");
    this.trail = [];
    this.propellerAngle = 0;

    this.initSize();
    window.addEventListener("resize", () => this.initSize());
  }

  initSize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.width = rect.width;
    this.height = rect.height;
    this.canvas.width = this.width * dpr;
    this.canvas.height = this.height * dpr;
    this.ctx.scale(dpr, dpr);
  }

  update(telemetry) {
    if (!telemetry || !telemetry.physics) return;
    const pos = telemetry.physics.position;
    this.trail.push({ x: pos.x_m, y: pos.y_m, z: pos.altitude_m });
    if (this.trail.length > 50) this.trail.shift();

    this.propellerAngle += 0.4;
    this.render(telemetry);
  }

  render(telemetry) {
    const ctx = this.ctx;
    const w = this.width;
    const h = this.height;
    const cx = w / 2;
    const cy = h / 2;

    ctx.clearRect(0, 0, w, h);

    const pos = telemetry.physics.position;
    const att = telemetry.physics.attitude_degrees;
    const rollRad = att.roll_deg * (Math.PI / 180.0);
    const pitchRad = att.pitch_deg * (Math.PI / 180.0);
    const yawRad = att.yaw_deg * (Math.PI / 180.0);

    // Perspective Ground Grid
    const scale = 5.0; // pixels per meter
    ctx.strokeStyle = "rgba(56, 189, 248, 0.12)";
    ctx.lineWidth = 1;

    for (let x = -80; x <= 80; x += 10) {
      ctx.beginPath();
      ctx.moveTo(cx + (x - pos.x_m) * scale, 0);
      ctx.lineTo(cx + (x - pos.x_m) * scale, h);
      ctx.stroke();
    }
    for (let y = -80; y <= 80; y += 10) {
      ctx.beginPath();
      ctx.moveTo(0, cy + (y - pos.y_m) * scale);
      ctx.lineTo(w, cy + (y - pos.y_m) * scale);
      ctx.stroke();
    }

    // Origin / Home marker (0, 0)
    const homePx = cx - pos.x_m * scale;
    const homePy = cy - pos.y_m * scale;
    ctx.strokeStyle = "#38bdf8";
    ctx.strokeRect(homePx - 10, homePy - 10, 20, 20);
    ctx.fillStyle = "#38bdf8";
    ctx.font = "9px sans-serif";
    ctx.fillText("HOME", homePx - 12, homePy - 14);

    // Draw Obstacles
    if (telemetry.obstacles) {
      telemetry.obstacles.forEach(obs => {
        const ox = cx + (obs.x - pos.x_m) * scale;
        const oy = cy + (obs.y - pos.y_m) * scale;
        const radPx = obs.radius * scale;

        ctx.fillStyle = "rgba(244, 63, 94, 0.2)";
        ctx.strokeStyle = "#f43f5e";
        ctx.beginPath();
        ctx.arc(ox, oy, radPx, 0, Math.PI * 2);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle = "#f43f5e";
        ctx.font = "8px sans-serif";
        ctx.fillText(obs.name, ox - 15, oy - radPx - 4);
      });
    }

    // Flight Path Trail
    if (this.trail.length > 1) {
      ctx.strokeStyle = "rgba(56, 189, 248, 0.6)";
      ctx.lineWidth = 2;
      ctx.beginPath();
      for (let i = 0; i < this.trail.length; i++) {
        const tx = cx + (this.trail[i].x - pos.x_m) * scale;
        const ty = cy + (this.trail[i].y - pos.y_m) * scale;
        if (i === 0) ctx.moveTo(tx, ty);
        else ctx.lineTo(tx, ty);
      }
      ctx.stroke();
    }

    // Target Waypoint line
    const target = telemetry.flight_status.target_position;
    if (target) {
      const tgtX = cx + (target.x - pos.x_m) * scale;
      const tgtY = cy + (target.y - pos.y_m) * scale;

      ctx.strokeStyle = "#10b981";
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(tgtX, tgtY);
      ctx.stroke();
      ctx.setLineDash([]);

      ctx.fillStyle = "#10b981";
      ctx.beginPath();
      ctx.arc(tgtX, tgtY, 5, 0, Math.PI * 2);
      ctx.fill();
    }

    // 3D Quadcopter Vehicle at center (cx, cy)
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(-yawRad);

    const armLen = 28;
    // Diagonal arms (Quad-X)
    ctx.strokeStyle = "#94a3b8";
    ctx.lineWidth = 4;
    ctx.beginPath();
    // Arm 1 to 3
    ctx.moveTo(-armLen, -armLen);
    ctx.lineTo(armLen, armLen);
    // Arm 2 to 4
    ctx.moveTo(armLen, -armLen);
    ctx.lineTo(-armLen, armLen);
    ctx.stroke();

    // Central Pod
    ctx.fillStyle = "#0284c7";
    ctx.beginPath();
    ctx.arc(0, 0, 10, 0, Math.PI * 2);
    ctx.fill();
    // Forward orientation arrow (Red nose)
    ctx.fillStyle = "#f43f5e";
    ctx.beginPath();
    ctx.moveTo(0, -12);
    ctx.lineTo(-4, -4);
    ctx.lineTo(4, -4);
    ctx.closePath();
    ctx.fill();

    // Motors & Spinning Propellers
    const motorLocs = [
      [armLen, -armLen],   // M1 Front-Right
      [-armLen, -armLen],  // M2 Front-Left
      [-armLen, armLen],   // M3 Rear-Left
      [armLen, armLen]     // M4 Rear-Right
    ];

    motorLocs.forEach((m, idx) => {
      // Motor mount
      ctx.fillStyle = "#1e293b";
      ctx.beginPath();
      ctx.arc(m[0], m[1], 5, 0, Math.PI * 2);
      ctx.fill();

      // Spinning Propeller Blur Disc
      ctx.strokeStyle = "rgba(56, 189, 248, 0.4)";
      ctx.lineWidth = 1.5;
      ctx.beginPath();
      ctx.arc(m[0], m[1], 14, 0, Math.PI * 2);
      ctx.stroke();

      // Propeller blade line
      ctx.save();
      ctx.translate(m[0], m[1]);
      ctx.rotate(this.propellerAngle * (idx % 2 === 0 ? 1 : -1));
      ctx.strokeStyle = "#38bdf8";
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(-13, 0);
      ctx.lineTo(13, 0);
      ctx.stroke();
      ctx.restore();
    });

    ctx.restore();
  }
}

