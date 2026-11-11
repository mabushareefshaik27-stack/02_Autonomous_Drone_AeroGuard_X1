"""
AeroGuard-X1 Ground Control Station (GCS) & Presentation Server.
Provides high-frequency telemetry streaming (SSE), MAVLink-style REST API,
and hosts both the Flight HUD GCS and the Interactive Power Presentation Deck.
"""

import os
import sys
import json
import time
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Dict, Any, List

# Ensure parent directory is on sys.path for direct script execution
_project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_dir not in sys.path:
    sys.path.insert(0, _project_dir)

from drone_engine.propulsion_power import DroneConfiguration, PropulsionEngine
from drone_engine.physics_6dof import Quadcopter6DOF
from drone_engine.flight_controller import CascadedFlightController
from drone_engine.path_planner import PathPlanner, Waypoint
from drone_engine.vision_ai import VisionAIEngine
from drone_engine.blueprint_generator import DroneBlueprintGenerator
from drone_engine.gemini_vision_generator import GeminiDroneVisionEngine

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")

class DroneSystemManager:
    """Singleton manager coordinating physics, flight control, and AI vision"""
    def __init__(self):
        self.config = DroneConfiguration()
        self.drone = Quadcopter6DOF(mass_kg=self.config.all_up_weight_kg)
        self.controller = CascadedFlightController(self.drone)
        self.planner = PathPlanner()
        self.vision = VisionAIEngine()

        # Add mock obstacles
        self.planner.add_obstacle(x=15.0, y=10.0, z_min=0.0, z_max=25.0, radius=4.0, name="Cell Tower")
        self.planner.add_obstacle(x=-18.0, y=-15.0, z_min=0.0, z_max=18.0, radius=5.5, name="High Voltage Pylon")

        self.armed = True
        self.active_waypoints: List[Waypoint] = []
        self.current_wp_index = 0
        self.mission_name = "Hover Hold"

        # Battery state
        self.battery_remaining_pct = 98.5
        self.current_draw_amps = 18.2
        self.flight_start_time = time.time()

        # Initial hover altitude
        self.drone.pos_z = 5.0
        self.controller.set_target(0.0, 0.0, 5.0)

    def load_mission(self, mission_type: str):
        if mission_type == "sar_spiral":
            self.active_waypoints = self.planner.generate_sar_spiral(center_x=0.0, center_y=0.0)
            self.mission_name = "Search & Rescue Spiral"
        elif mission_type == "agri_survey":
            self.active_waypoints = self.planner.generate_agricultural_grid(center_x=0.0, center_y=0.0)
            self.mission_name = "NDVI Agricultural Grid"
        elif mission_type == "perimeter":
            self.active_waypoints = [
                Waypoint(25, 25, 10, "PASS"),
                Waypoint(-25, 25, 10, "PASS"),
                Waypoint(-25, -25, 10, "PASS"),
                Waypoint(25, -25, 10, "PASS"),
                Waypoint(0, 0, 8, "RTL")
            ]
            self.mission_name = "Perimeter Security Patrol"
        
        self.current_wp_index = 0
        if self.active_waypoints:
            wp = self.active_waypoints[0]
            self.controller.set_target(wp.x, wp.y, wp.z)
            self.controller.set_mode("AUTO_WAYPOINT")

    def step(self, dt: float = 0.02):
        if not self.armed:
            self.drone.update_physics([0, 0, 0, 0], dt)
            return

        # Advance waypoints in autonomous mode
        if self.controller.flight_mode == "AUTO_WAYPOINT" and self.active_waypoints:
            curr_wp = self.active_waypoints[self.current_wp_index]
            dist_to_wp = math.sqrt((self.drone.pos_x - curr_wp.x)**2 + 
                                   (self.drone.pos_y - curr_wp.y)**2 + 
                                   (self.drone.pos_z - curr_wp.z)**2)
            if dist_to_wp < 2.0:
                self.current_wp_index = (self.current_wp_index + 1) % len(self.active_waypoints)
                next_wp = self.active_waypoints[self.current_wp_index]
                self.controller.set_target(next_wp.x, next_wp.y, next_wp.z)

        # Compute motor commands from PID controller
        motor_cmds = self.controller.update_control(dt)
        self.drone.update_physics(motor_cmds, dt)

        # Update battery discharge
        avg_rpm = sum(self.drone.motor_rpms) / 4.0
        throttle_pct = avg_rpm / 9500.0
        self.current_draw_amps = max(2.0, 16.0 + (throttle_pct ** 2) * 45.0)
        # Drain battery: Ah = (Amps * dt / 3600)
        capacity_ah = self.config.battery_capacity_mah / 1000.0
        drain_pct = (self.current_draw_amps * (dt / 3600.0) / capacity_ah) * 100.0
        self.battery_remaining_pct = max(0.0, self.battery_remaining_pct - drain_pct)

    def get_full_telemetry(self) -> Dict[str, Any]:
        physics = self.drone.get_telemetry_state()
        vision = self.vision.scan_field_of_view(self.drone.pos_x, self.drone.pos_y, self.drone.pos_z)
        
        # Power & battery metrics
        v_sag = self.current_draw_amps * self.config.battery_internal_resistance
        v_live = (self.config.nominal_voltage * (0.85 + 0.15 * (self.battery_remaining_pct / 100.0))) - v_sag

        return {
            "flight_status": {
                "armed": self.armed,
                "flight_mode": self.controller.flight_mode,
                "mission_name": self.mission_name,
                "current_waypoint": self.current_wp_index + 1,
                "total_waypoints": len(self.active_waypoints),
                "target_position": {
                    "x": round(self.controller.target_x, 2),
                    "y": round(self.controller.target_y, 2),
                    "z": round(self.controller.target_z, 2)
                }
            },
            "physics": physics,
            "power_system": {
                "battery_voltage_v": round(v_live, 2),
                "battery_current_a": round(self.current_draw_amps, 2),
                "battery_power_watts": round(v_live * self.current_draw_amps, 1),
                "battery_pct": round(self.battery_remaining_pct, 1),
                "cell_voltage_avg": round(v_live / self.config.battery_cells_s, 2),
                "esc_temperatures_c": [round(38.0 + (self.current_draw_amps * 0.4), 1)] * 4
            },
            "vision_ai": vision,
            "obstacles": [
                {"name": obs.name, "x": obs.x, "y": obs.y, "radius": obs.radius, "height": obs.z_max}
                for obs in self.planner.obstacles
            ]
        }

# Global singleton
SYSTEM = DroneSystemManager()
SYSTEM_LOCK = threading.Lock()

def physics_loop():
    while True:
        with SYSTEM_LOCK:
            SYSTEM.step(dt=0.03)
        time.sleep(0.03)

class GCSRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def _send_json(self, data: Any, status: int = 200):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/drone/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            try:
                while True:
                    with SYSTEM_LOCK:
                        telemetry = SYSTEM.get_full_telemetry()
                    payload = f"data: {json.dumps(telemetry)}\n\n"
                    self.wfile.write(payload.encode("utf-8"))
                    self.wfile.flush()
                    time.sleep(0.08)  # ~12.5 Hz streaming for responsive HUD
            except (BrokenPipeError, ConnectionResetError):
                return

        elif path == "/api/drone/telemetry":
            with SYSTEM_LOCK:
                t = SYSTEM.get_full_telemetry()
            self._send_json(t)

        elif path == "/api/drone/specs":
            with SYSTEM_LOCK:
                aero = PropulsionEngine.calculate_aerodynamics(SYSTEM.config)
                endur = PropulsionEngine.calculate_battery_endurance(SYSTEM.config, aero["hover_current_amps"])
            self._send_json({
                "config": {
                    "all_up_weight_kg": aero["all_up_weight_kg"],
                    "thrust_to_weight_ratio": aero["thrust_to_weight_ratio"],
                    "hover_throttle_pct": aero["hover_throttle_pct"],
                    "hover_power_w": aero["hover_electrical_power_watts"],
                    "hover_time_mins": endur["hover_flight_time_mins"],
                    "cruise_range_km": endur["operational_range_km"]
                },
                "aerodynamics": aero,
                "endurance": endur
            })

        elif path == "/api/drone/blueprint-presets":
            presets = [
                {
                    "id": "agri_hex",
                    "title": "🌾 Agricultural Spray Hexacopter",
                    "prompt": "Heavy-lift agricultural hexacopter with 20L pesticide spray tank, dual pressure spray booms, and folding carbon fiber arms"
                },
                {
                    "id": "stealth_recon",
                    "title": "🦅 Stealth Tactical Reconnaissance Quad",
                    "prompt": "Stealth tactical surveillance quadcopter with anti-radar matte carbon chassis, low-noise props, and FLIR Boson thermal camera"
                },
                {
                    "id": "vtol_sar",
                    "title": "🚨 Long-Range Search & Rescue VTOL",
                    "prompt": "Solar-assisted long-endurance search and rescue quadplane VTOL with 2.2m wingspan, 12000-lumen searchlight, and satcom link"
                },
                {
                    "id": "cargo_titan",
                    "title": "📦 Heavy Logistics Cargo Octocopter",
                    "prompt": "Heavy-lift cargo logistics octocopter with electric winch, pneumatic container clamps, and redundant 14S dual-battery power"
                },
                {
                    "id": "lidar_inspector",
                    "title": "🔍 3D LiDAR Industrial Inspection Drone",
                    "prompt": "Industrial infrastructure inspection quadcopter with Livox 360-degree LiDAR puck, RTK GPS mast, and collision avoidance sonar"
                },
                {
                    "id": "fpv_cinewhoop",
                    "title": "⚡ Ducted Tactical Micro-Cinewhoop",
                    "prompt": "Compact ducted cinewhoop micro-drone with high-KV motors, protective propeller ducts, and 4K low-latency digital FPV camera"
                }
            ]
            self._send_json({"presets": presets})

        elif path == "/api/drone/download-pptx":
            pptx_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "AeroGuard_X1_Presentation.pptx")
            if os.path.exists(pptx_path):
                self.send_response(200)
                self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.presentationml.presentation")
                self.send_header("Content-Disposition", 'attachment; filename="AeroGuard_X1_Final_Year_Presentation.pptx"')
                self.send_header("Content-Length", str(os.path.getsize(pptx_path)))
                self.end_headers()
                with open(pptx_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._send_json({"error": "PPTX file not yet generated. Run pptx_generator.py"}, status=404)
        else:
            super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_length) if content_length > 0 else b"{}"
        try:
            data = json.loads(post_body.decode("utf-8"))
        except Exception:
            data = {}

        if path == "/api/drone/command":
            cmd = data.get("command")
            with SYSTEM_LOCK:
                if cmd == "ARM":
                    SYSTEM.armed = True
                elif cmd == "DISARM":
                    SYSTEM.armed = False
                elif cmd == "TAKEOFF":
                    SYSTEM.armed = True
                    SYSTEM.controller.set_mode("POS_HOLD")
                    SYSTEM.controller.set_target(SYSTEM.drone.pos_x, SYSTEM.drone.pos_y, 10.0)
                elif cmd == "LAND":
                    SYSTEM.controller.set_mode("ALT_HOLD")
                    SYSTEM.controller.set_target(SYSTEM.drone.pos_x, SYSTEM.drone.pos_y, 0.0)
                elif cmd == "RTL":
                    SYSTEM.controller.set_mode("RETURN_TO_HOME")
                    SYSTEM.controller.set_target(0.0, 0.0, 8.0)
                elif cmd == "SET_MODE":
                    SYSTEM.controller.set_mode(data.get("mode", "POS_HOLD"))
                elif cmd == "SET_TARGET":
                    SYSTEM.controller.set_target(
                        float(data.get("x", 0)),
                        float(data.get("y", 0)),
                        float(data.get("z", 5)),
                        float(data.get("yaw_deg", 0))
                    )
                t = SYSTEM.get_full_telemetry()
            self._send_json({"status": "command_executed", "command": cmd, "telemetry": t})

        elif path == "/api/drone/mission":
            mission_type = data.get("mission_type", "sar_spiral")
            with SYSTEM_LOCK:
                SYSTEM.load_mission(mission_type)
                t = SYSTEM.get_full_telemetry()
            self._send_json({"status": "mission_loaded", "mission": mission_type, "telemetry": t})

        elif path == "/api/drone/generate-blueprint":
            prompt = data.get("prompt", "Heavy-lift agricultural hexacopter with 20L spray tank and folding arms")
            view_mode = data.get("view_mode", "multiview")
            spec = DroneBlueprintGenerator.synthesize_spec_from_prompt(prompt)
            svg = DroneBlueprintGenerator.generate_svg_blueprint(spec, view_mode=view_mode)

            vision_engine = GeminiDroneVisionEngine()
            img_result = vision_engine.generate_drone_image(prompt, spec.to_dict())
            ai_analysis = vision_engine.analyze_design_with_gemini(prompt, spec.to_dict())

            self._send_json({
                "status": "success",
                "prompt": prompt,
                "view_mode": view_mode,
                "spec": spec.to_dict(),
                "svg": svg,
                "image_url": img_result["image_url"],
                "image_meta": img_result,
                "ai_analysis": ai_analysis
            })

        else:
            self._send_json({"error": "Endpoint not found"}, status=404)

def run_gcs_server(port: int = 8090):
    threading.Thread(target=physics_loop, daemon=True).start()
    server = ThreadingHTTPServer(("0.0.0.0", port), GCSRequestHandler)
    print(f"=== AeroGuard-X1 GCS & Presentation Server running at http://localhost:{port} ===")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down AeroGuard GCS server...")
        server.server_close()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8090
    run_gcs_server(port)

