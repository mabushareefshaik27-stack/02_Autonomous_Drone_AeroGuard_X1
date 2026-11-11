"""
AI Drone Blueprint & Image Generator Engine for AeroGuard-X1.
Synthesizes prompt inputs into parametric CAD blueprints, multi-view orthographic drawings,
dimensioned technical schematics, and high-resolution visual renderings.
"""

import math
import json
import re
from typing import Dict, Any, List, Tuple

class DroneDesignSpec:
    """Parametric specification synthesized from a natural language prompt."""
    def __init__(
        self,
        name: str,
        configuration: str,  # "quadcopter", "hexacopter", "octocopter", "vtol_quadplane", "cinewhoop_ducted"
        mission_type: str,   # "agriculture", "surveillance", "search_and_rescue", "heavy_lift", "inspection", "racing"
        wheelbase_mm: float,
        propeller_dia_inch: float,
        auw_kg: float,
        payload_capacity_kg: float,
        battery_type: str,
        flight_time_mins: float,
        motor_kv: int,
        max_speed_kmh: float,
        color_accent: str,
        key_features: List[str]
    ):
        self.name = name
        self.configuration = configuration
        self.mission_type = mission_type
        self.wheelbase_mm = wheelbase_mm
        self.propeller_dia_inch = propeller_dia_inch
        self.auw_kg = auw_kg
        self.payload_capacity_kg = payload_capacity_kg
        self.battery_type = battery_type
        self.flight_time_mins = flight_time_mins
        self.motor_kv = motor_kv
        self.max_speed_kmh = max_speed_kmh
        self.color_accent = color_accent
        self.key_features = key_features

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "configuration": self.configuration,
            "mission_type": self.mission_type,
            "wheelbase_mm": self.wheelbase_mm,
            "propeller_dia_inch": self.propeller_dia_inch,
            "auw_kg": self.auw_kg,
            "payload_capacity_kg": self.payload_capacity_kg,
            "battery_type": self.battery_type,
            "flight_time_mins": self.flight_time_mins,
            "motor_kv": self.motor_kv,
            "max_speed_kmh": self.max_speed_kmh,
            "color_accent": self.color_accent,
            "key_features": self.key_features
        }


class DroneBlueprintGenerator:
    """
    Parses natural language prompts and generates parametric aerospace blueprints,
    SVG multi-view technical drawings, and dimensioned CAD schematics.
    """

    @classmethod
    def synthesize_spec_from_prompt(cls, prompt: str) -> DroneDesignSpec:
        """
        Parses user prompt and synthesizes aerospace engineering parameters.
        """
        p = prompt.lower()

        # 1. Detect Configuration
        if any(w in p for w in ["hexa", "6 rotor", "6-rotor", "six rotor"]):
            config = "hexacopter"
            default_wb = 750.0
            default_prop = 16.0
            default_auw = 6.8
            default_payload = 4.0
            default_kv = 320
        elif any(w in p for w in ["octo", "8 rotor", "8-rotor", "eight rotor", "x8", "coaxial"]):
            config = "octocopter"
            default_wb = 950.0
            default_prop = 18.0
            default_auw = 12.5
            default_payload = 8.5
            default_kv = 210
        elif any(w in p for w in ["vtol", "plane", "fixed-wing", "fixed wing", "quadplane", "glider"]):
            config = "vtol_quadplane"
            default_wb = 800.0
            default_prop = 14.0
            default_auw = 5.2
            default_payload = 2.5
            default_kv = 400
        elif any(w in p for w in ["micro", "pocket", "nano", "ducted", "cinewhoop", "fpv", "mini", "cage"]):
            config = "cinewhoop_ducted"
            default_wb = 180.0
            default_prop = 3.5
            default_auw = 0.65
            default_payload = 0.25
            default_kv = 2400
        else:
            config = "quadcopter"
            default_wb = 500.0
            default_prop = 14.0
            default_auw = 2.85
            default_payload = 0.8
            default_kv = 380

        # 2. Detect Mission Profile & Features
        key_features = []
        if any(w in p for w in ["agri", "spray", "crop", "pesticide", "farm", "fertilizer", "ndvi"]):
            mission = "agriculture"
            name = "AeroCrop-X" if config != "hexacopter" else "AeroSpray-H6"
            color_accent = "#10b981"  # Emerald Green
            key_features.extend(["Dual Pressure Spray Booms", "Centrifugal Atomizer Nozzles", "NDVI Multispectral Pod", "Quick-Detach 16L Liquid Tank"])
            default_payload = max(default_payload, 5.0)
            default_auw = max(default_auw, 8.5)
            default_prop = max(default_prop, 18.0)
            battery = "12S 22000mAh Smart LiPo"
            flight_time = 24.0
            speed = 35.0

        elif any(w in p for w in ["stealth", "tactical", "surveil", "defense", "military", "recon", "covert"]):
            mission = "surveillance"
            name = "AeroGhost-T1" if config != "vtol_quadplane" else "AeroVanguard-VTOL"
            color_accent = "#38bdf8"  # Cyber Sky Cyan
            key_features.extend(["Anti-Radar Matte Carbon Coating", "Ultra-Low Acoustic Noise Propellers", "FLIR Boson 640 Thermal Core", "Encrypted AES-256 Satcom Link"])
            battery = "6S 8500mAh Solid-State Li-Ion"
            flight_time = 38.0
            speed = 75.0

        elif any(w in p for w in ["rescue", "sar", "search", "disaster", "survivor", "flood", "earthquake"]):
            mission = "search_and_rescue"
            name = "AeroRescue-SAR"
            color_accent = "#f59e0b"  # High-Vis Rescue Amber
            key_features.extend(["12000-Lumen Xenon Searchlight", "Directional Loudhailer & Two-Way Audio", "Dual LWIR/Visual Tracking Gimbal", "CO2 & Thermal Life-Signs Radar"])
            battery = "6S 10000mAh Semi-Solid Cell"
            flight_time = 32.0
            speed = 65.0

        elif any(w in p for w in ["cargo", "heavy", "lift", "delivery", "transport", "package", "logistics"]):
            mission = "heavy_lift"
            name = "AeroLift-Titan"
            color_accent = "#f43f5e"  # Industrial Crimson
            key_features.extend(["Electric Servo Winch System", "Pneumatic Cargo Clamps", "Redundant Dual-Battery Failover", "Active CG Balancing Gimbal"])
            default_payload = max(default_payload, 10.0)
            default_auw = max(default_auw, 16.0)
            battery = "14S 30000mAh LiPo Pack"
            flight_time = 28.0
            speed = 55.0

        elif any(w in p for w in ["lidar", "inspect", "mapping", "cad", "survey", "structure", "bridge"]):
            mission = "inspection"
            name = "AeroSurvey-L4"
            color_accent = "#a855f7"  # Deep Purple
            key_features.extend(["Livox Mid-360 3D LiDAR Puck", "Millimeter-Accuracy RTK Base Link", "Omnidirectional Sonar & ToF Array", "Downward Orthomosaic PhaseOne Mount"])
            battery = "6S 6500mAh High-Density LiPo"
            flight_time = 30.0
            speed = 48.0

        elif any(w in p for w in ["race", "racing", "speed", "fast", "aerobatic", "freestyle"]):
            mission = "racing"
            name = "AeroSpeed-X9"
            color_accent = "#ef4444"
            key_features.extend(["Ultra-Light Toray T800 Carbon", "DShot1200 65A ESC Stack", "Furious 6S 1500mAh 150C Graphene Pack", "HD Low-Latency Digital Video System"])
            default_wb = min(default_wb, 220.0)
            default_prop = min(default_prop, 5.1)
            default_auw = 0.58
            default_payload = 0.15
            default_kv = 1950
            battery = "6S 1400mAh 150C Graphene"
            flight_time = 8.5
            speed = 185.0

        else:
            mission = "multi_mission"
            name = f"AeroGuard-Custom ({config.capitalize()})"
            color_accent = "#06b6d4"
            key_features.extend(["Modular Carbon Airframe", "Pixhawk 6C STM32F7 Autopilot", "3-Axis 4K Stabilized Gimbal", "Centimeter RTK GPS Positioning"])
            battery = "6S 6500mAh 35C LiPo"
            flight_time = 28.5
            speed = 52.0

        # Check for user-specified numbers in prompt
        # Extract wheelbase if mentioned e.g. "650mm"
        wb_match = re.search(r'(\d+)\s*mm', p)
        if wb_match:
            default_wb = float(wb_match.group(1))

        # Extract payload if mentioned e.g. "15kg" or "20l"
        pay_match = re.search(r'(\d+)\s*(kg|liters|litre|l)', p)
        if pay_match:
            default_payload = float(pay_match.group(1))
            default_auw = max(default_auw, default_payload * 1.8)

        return DroneDesignSpec(
            name=name,
            configuration=config,
            mission_type=mission,
            wheelbase_mm=default_wb,
            propeller_dia_inch=default_prop,
            auw_kg=round(default_auw, 2),
            payload_capacity_kg=round(default_payload, 2),
            battery_type=battery,
            flight_time_mins=round(flight_time, 1),
            motor_kv=default_kv,
            max_speed_kmh=round(speed, 1),
            color_accent=color_accent,
            key_features=key_features
        )

    @classmethod
    def generate_svg_blueprint(cls, spec: DroneDesignSpec, view_mode: str = "multiview") -> str:
        """
        Renders a full ISO-compliant technical CAD blueprint in SVG format.
        Supports: "multiview" (4-view projection), "top", "front", "side", "isometric".
        """
        width = 1600
        height = 1000

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: #07152b; font-family: \'Courier New\', Courier, monospace;">',
            # Embedded Styles & Marker Definitions
            '''
            <defs>
              <!-- Fine Blueprint Grid Pattern -->
              <pattern id="smallGrid" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#0e2a54" stroke-width="0.75"/>
              </pattern>
              <pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse">
                <rect width="100" height="100" fill="url(#smallGrid)"/>
                <path d="M 100 0 L 0 0 0 100" fill="none" stroke="#18427e" stroke-width="1.5"/>
              </pattern>

              <!-- Dimension Arrow Markers -->
              <marker id="arrowStart" viewBox="0 0 10 10" refX="0" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 10 0 L 0 5 L 10 10 z" fill="#38bdf8"/>
              </marker>
              <marker id="arrowEnd" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="6" markerHeight="6" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8"/>
              </marker>
              <marker id="dotMarker" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5">
                <circle cx="5" cy="5" r="4" fill="#f59e0b"/>
              </marker>
            </defs>
            ''',
            # Background blueprint grid
            f'<rect width="{width}" height="{height}" fill="url(#grid)"/>',
            # Drawing Sheet Outer & Inner Border
            f'<rect x="25" y="25" width="{width - 50}" height="{height - 50}" fill="none" stroke="#1d4e89" stroke-width="2"/>',
            f'<rect x="35" y="35" width="{width - 70}" height="{height - 70}" fill="none" stroke="#38bdf8" stroke-width="1"/>'
        ]

        if view_mode == "multiview":
            # 4-Quadrant Viewport Dividers
            mid_x = (width - 70) / 2 + 35
            mid_y = (height - 70) / 2 + 35
            svg_parts.append(f'<line x1="{mid_x}" y1="35" x2="{mid_x}" y2="{height - 35}" stroke="#1d4e89" stroke-dasharray="8,6" stroke-width="1"/>')
            svg_parts.append(f'<line x1="35" y1="{mid_y}" x2="{width - 35}" y2="{mid_y}" stroke="#1d4e89" stroke-dasharray="8,6" stroke-width="1"/>')

            # Render Quadrant 1: TOP PLAN VIEW (Top-Left)
            svg_parts.append(cls._render_top_view(spec, cx=410, cy=270, scale=0.48))
            # Render Quadrant 2: ISOMETRIC 3D CAD PROJECTION (Top-Right)
            svg_parts.append(cls._render_isometric_view(spec, cx=1180, cy=270, scale=0.48))
            # Render Quadrant 3: FRONT ELEVATION VIEW (Bottom-Left)
            svg_parts.append(cls._render_front_view(spec, cx=410, cy=740, scale=0.48))
            # Render Quadrant 4: SIDE PROFILE VIEW (Bottom-Right)
            svg_parts.append(cls._render_side_view(spec, cx=950, cy=740, scale=0.48))

        elif view_mode == "top":
            svg_parts.append(cls._render_top_view(spec, cx=width/2 - 100, cy=height/2, scale=0.85))
        elif view_mode == "front":
            svg_parts.append(cls._render_front_view(spec, cx=width/2 - 100, cy=height/2, scale=0.85))
        elif view_mode == "side":
            svg_parts.append(cls._render_side_view(spec, cx=width/2 - 100, cy=height/2, scale=0.85))
        elif view_mode == "isometric":
            svg_parts.append(cls._render_isometric_view(spec, cx=width/2 - 100, cy=height/2, scale=0.85))

        # Title Block at Bottom-Right
        svg_parts.append(cls._render_title_block(spec, x=width - 430, y=height - 180, w=390, h=140))

        # Specifications Callout Box (Top-Left Corner Header)
        svg_parts.append(cls._render_spec_table(spec, x=50, y=50))

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)

    @classmethod
    def _render_top_view(cls, spec: DroneDesignSpec, cx: float, cy: float, scale: float) -> str:
        """Renders Top Plan View with rotor arms, motors, center fuselage, and props."""
        out = [
            f'<g id="top_view">',
            f'<text x="{cx - 200}" y="{cy - 190}" fill="#38bdf8" font-size="13" font-weight="bold" letter-spacing="1">VIEW A-A : TOP PLAN PROJECTION</text>',
            f'<text x="{cx - 200}" y="{cy - 175}" fill="#64748b" font-size="10">SCALE: 1:10 | THIRD-ANGLE PROJECTION</text>'
        ]

        wb_px = (spec.wheelbase_mm / 1000.0) * 350.0 * scale
        prop_radius_px = (spec.propeller_dia_inch * 25.4 / 1000.0) * 350.0 * scale * 0.5

        # Center Fuselage Body
        body_radius = 42 * scale
        out.append(f'<rect x="{cx - body_radius}" y="{cy - body_radius * 1.3}" width="{body_radius * 2}" height="{body_radius * 2.6}" rx="12" fill="#0d2448" stroke="#38bdf8" stroke-width="2"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{body_radius * 0.7}" fill="none" stroke="#1d4e89" stroke-width="1.5" stroke-dasharray="4,3"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="3" fill="#f59e0b"/>')  # Center of Gravity (CG)
        out.append(f'<text x="{cx + 6}" y="{cy - 6}" fill="#f59e0b" font-size="8">C.G.</text>')

        # Forward Direction Nose Arrow
        out.append(f'<polygon points="{cx},{cy - body_radius * 1.3 - 12} {cx - 6},{cy - body_radius * 1.3 - 2} {cx + 6},{cy - body_radius * 1.3 - 2}" fill="#f43f5e"/>')

        # Determine arm angles based on config
        angles = []
        if spec.configuration == "hexacopter":
            angles = [30, 90, 150, 210, 270, 330]
        elif spec.configuration == "octocopter":
            angles = [22.5, 67.5, 112.5, 157.5, 202.5, 247.5, 292.5, 337.5]
        else:
            angles = [45, 135, 225, 315]

        # Draw Arms & Motors
        r_arm = wb_px / 2.0
        for i, deg in enumerate(angles):
            rad = math.radians(deg)
            mx = cx + r_arm * math.cos(rad)
            my = cy + r_arm * math.sin(rad)

            # Carbon fiber arm tube
            out.append(f'<line x1="{cx}" y1="{cy}" x2="{mx}" y2="{my}" stroke="#38bdf8" stroke-width="5"/>')
            out.append(f'<line x1="{cx}" y1="{cy}" x2="{mx}" y2="{my}" stroke="#0b172a" stroke-width="2"/>')

            # Motor Mount
            out.append(f'<circle cx="{mx}" cy="{my}" r="12" fill="#0b172a" stroke="#38bdf8" stroke-width="1.5"/>')
            out.append(f'<circle cx="{mx}" cy="{my}" r="5" fill="{spec.color_accent}"/>')

            # Propeller Disc Perimeter
            is_ccw = (i % 2 == 0)
            out.append(f'<circle cx="{mx}" cy="{my}" r="{prop_radius_px}" fill="none" stroke="rgba(56, 189, 248, 0.35)" stroke-width="1" stroke-dasharray="5,4"/>')

            # Rotation direction arrow
            arrow_txt = "CCW ↺" if is_ccw else "CW ↻"
            out.append(f'<text x="{mx - 14}" y="{my + 4}" fill="#94a3b8" font-size="7">{arrow_txt}</text>')

        # VTOL Wings if quadplane
        if spec.configuration == "vtol_quadplane":
            wing_w = 260 * scale
            wing_h = 28 * scale
            out.append(f'<rect x="{cx - wing_w}" y="{cy - wing_h/2}" width="{wing_w * 2}" height="{wing_h}" rx="6" fill="rgba(16, 185, 129, 0.15)" stroke="#10b981" stroke-width="1.5"/>')
            out.append(f'<text x="{cx + wing_w - 40}" y="{cy - wing_h/2 - 4}" fill="#10b981" font-size="8">MAIN WING: 2.2m</text>')

        # Dimension Lines: Wheelbase
        m1_rad = math.radians(angles[0])
        m2_rad = math.radians(angles[len(angles)//2])
        p1x, p1y = cx + r_arm * math.cos(m1_rad), cy + r_arm * math.sin(m1_rad)
        p2x, p2y = cx + r_arm * math.cos(m2_rad), cy + r_arm * math.sin(m2_rad)

        out.append(cls._draw_dimension_line(p1x, p1y + 25, p2x, p2y + 25, f"Ø {spec.wheelbase_mm:.0f} mm (WHEELBASE)"))

        out.append('</g>')
        return "\n".join(out)

    @classmethod
    def _render_front_view(cls, spec: DroneDesignSpec, cx: float, cy: float, scale: float) -> str:
        """Renders Front Elevation View with landing skids, motor clearance, and payload."""
        out = [
            f'<g id="front_view">',
            f'<text x="{cx - 200}" y="{cy - 120}" fill="#38bdf8" font-size="13" font-weight="bold" letter-spacing="1">VIEW B-B : FRONT ELEVATION</text>',
            f'<text x="{cx - 200}" y="{cy - 105}" fill="#64748b" font-size="10">VERTICAL CLEARANCE & STRUT GEOMETRY</text>'
        ]

        wb_half = (spec.wheelbase_mm / 1000.0) * 175.0 * scale
        prop_rad = (spec.propeller_dia_inch * 25.4 / 1000.0) * 350.0 * scale * 0.5
        fuselage_h = 45 * scale
        skid_h = 75 * scale

        ground_y = cy + skid_h
        # Ground datum line
        out.append(f'<line x1="{cx - wb_half - prop_rad - 20}" y1="{ground_y}" x2="{cx + wb_half + prop_rad + 20}" y2="{ground_y}" stroke="#64748b" stroke-width="1.5" stroke-dasharray="10,4"/>')
        out.append(f'<text x="{cx + wb_half + prop_rad + 25}" y="{ground_y + 3}" fill="#64748b" font-size="8">GROUND DATUM</text>')

        # Landing Gear Skids
        skid_w = wb_half * 0.75
        out.append(f'<line x1="{cx - skid_w}" y1="{cy + 10}" x2="{cx - skid_w - 15}" y2="{ground_y}" stroke="#38bdf8" stroke-width="3"/>')
        out.append(f'<line x1="{cx + skid_w}" y1="{cy + 10}" x2="{cx + skid_w + 15}" y2="{ground_y}" stroke="#38bdf8" stroke-width="3"/>')
        out.append(f'<line x1="{cx - skid_w - 35}" y1="{ground_y}" x2="{cx - skid_w + 20}" y2="{ground_y}" stroke="#38bdf8" stroke-width="4"/>')
        out.append(f'<line x1="{cx + skid_w - 20}" y1="{ground_y}" x2="{cx + skid_w + 35}" y2="{ground_y}" stroke="#38bdf8" stroke-width="4"/>')

        # Fuselage Center Box
        out.append(f'<rect x="{cx - 40 * scale}" y="{cy - fuselage_h}" width="{80 * scale}" height="{fuselage_h + 10}" rx="6" fill="#0d2448" stroke="#38bdf8" stroke-width="2"/>')

        # Horizontal Arm Tube
        out.append(f'<line x1="{cx - wb_half}" y1="{cy}" x2="{cx + wb_half}" y2="{cy}" stroke="#38bdf8" stroke-width="5"/>')

        # Left & Right Motors
        for mx in [cx - wb_half, cx + wb_half]:
            out.append(f'<rect x="{mx - 8}" y="{cy - 16}" width="16" height="16" fill="#0b172a" stroke="#38bdf8" stroke-width="1.5"/>')
            # Propeller horizontal disc line
            out.append(f'<line x1="{mx - prop_rad}" y1="{cy - 18}" x2="{mx + prop_rad}" y2="{cy - 18}" stroke="{spec.color_accent}" stroke-width="2"/>')
            out.append(f'<ellipse cx="{mx}" cy="{cy - 18}" rx="{prop_rad}" ry="4" fill="none" stroke="rgba(56,189,248,0.3)" stroke-dasharray="4,3"/>')

        # Gimbal / Payload beneath fuselage
        out.append(f'<circle cx="{cx}" cy="{cy + 18}" r="12" fill="#0b172a" stroke="#f59e0b" stroke-width="2"/>')
        out.append(f'<line x1="{cx}" y1="{cy + 5}" x2="{cx}" y2="{cy + 18}" stroke="#f59e0b" stroke-width="2"/>')

        # Vertical Height Dimension
        out.append(cls._draw_dimension_vertical(cx - wb_half - prop_rad - 15, cy - 18, ground_y, f"{spec.wheelbase_mm * 0.42:.0f} mm (HEIGHT)"))

        out.append('</g>')
        return "\n".join(out)

    @classmethod
    def _render_side_view(cls, spec: DroneDesignSpec, cx: float, cy: float, scale: float) -> str:
        """Renders Side Elevation View."""
        out = [
            f'<g id="side_view">',
            f'<text x="{cx - 180}" y="{cy - 120}" fill="#38bdf8" font-size="13" font-weight="bold" letter-spacing="1">VIEW C-C : SIDE PROFILE</text>',
            f'<text x="{cx - 180}" y="{cy - 105}" fill="#64748b" font-size="10">AERODYNAMIC PROFILE & CAMBER</text>'
        ]

        length_half = (spec.wheelbase_mm / 1000.0) * 150.0 * scale
        skid_h = 75 * scale
        ground_y = cy + skid_h

        # Fuselage Aerodynamic Teardrop Contour
        out.append(f'<path d="M {cx - length_half * 0.7} {cy} Q {cx} {cy - 50 * scale} {cx + length_half * 0.8} {cy - 8} Q {cx} {cy + 25 * scale} {cx - length_half * 0.7} {cy} Z" fill="#0d2448" stroke="#38bdf8" stroke-width="2"/>')

        # Landing Skid (Side view - elongated runner)
        out.append(f'<line x1="{cx - length_half * 0.6}" y1="{ground_y}" x2="{cx + length_half * 0.6}" y2="{ground_y}" stroke="#38bdf8" stroke-width="4"/>')
        out.append(f'<line x1="{cx - 30 * scale}" y1="{cy + 10}" x2="{cx - 40 * scale}" y2="{ground_y}" stroke="#38bdf8" stroke-width="2.5"/>')
        out.append(f'<line x1="{cx + 30 * scale}" y1="{cy + 10}" x2="{cx + 40 * scale}" y2="{ground_y}" stroke="#38bdf8" stroke-width="2.5"/>')

        # Camera Gimbal looking forward
        out.append(f'<circle cx="{cx + length_half * 0.65}" cy="{cy + 15}" r="11" fill="#0b172a" stroke="#f59e0b" stroke-width="2"/>')
        # Lens orientation ray
        out.append(f'<line x1="{cx + length_half * 0.65}" y1="{cy + 15}" x2="{cx + length_half * 0.65 + 18}" y2="{cy + 24}" stroke="#f59e0b" stroke-dasharray="3,2" stroke-width="1.5"/>')

        # GPS Mast
        out.append(f'<line x1="{cx - 20 * scale}" y1="{cy - 30 * scale}" x2="{cx - 20 * scale}" y2="{cy - 55 * scale}" stroke="#38bdf8" stroke-width="2"/>')
        out.append(f'<circle cx="{cx - 20 * scale}" cy="{cy - 55 * scale}" r="7" fill="#0d2448" stroke="#38bdf8" stroke-width="1.5"/>')

        out.append('</g>')
        return "\n".join(out)

    @classmethod
    def _render_isometric_view(cls, spec: DroneDesignSpec, cx: float, cy: float, scale: float) -> str:
        """Renders 3D Isometric CAD Wireframe Projection."""
        out = [
            f'<g id="iso_view">',
            f'<text x="{cx - 160}" y="{cy - 190}" fill="#38bdf8" font-size="13" font-weight="bold" letter-spacing="1">ISOMETRIC 3D CAD PROJECTION</text>',
            f'<text x="{cx - 160}" y="{cy - 175}" fill="#64748b" font-size="10">AXONOMETRIC 30° / 30° PERSPECTIVE</text>'
        ]

        # 3D Arm Vectors in Isometric (x_iso = (x - y)*cos(30), y_iso = (x + y)*sin(30) - z)
        cos30 = 0.866
        sin30 = 0.500
        arm_len = (spec.wheelbase_mm / 1000.0) * 160.0 * scale

        # Central 3D Pod Box
        box_w, box_h = 35 * scale, 18 * scale
        out.append(f'<polygon points="{cx},{cy - box_h - 10} {cx + box_w * cos30},{cy - box_h + box_w * sin30 - 10} {cx},{cy - box_h + box_w * sin30 * 2 - 10} {cx - box_w * cos30},{cy - box_h + box_w * sin30 - 10}" fill="#0d2448" stroke="#38bdf8" stroke-width="2"/>')
        out.append(f'<polygon points="{cx - box_w * cos30},{cy - box_h + box_w * sin30 - 10} {cx},{cy - box_h + box_w * sin30 * 2 - 10} {cx},{cy + box_w * sin30 * 2} {cx - box_w * cos30},{cy + box_w * sin30}" fill="#081830" stroke="#38bdf8" stroke-width="1.5"/>')
        out.append(f'<polygon points="{cx},{cy - box_h + box_w * sin30 * 2 - 10} {cx + box_w * cos30},{cy - box_h + box_w * sin30 - 10} {cx + box_w * cos30},{cy + box_w * sin30} {cx},{cy + box_w * sin30 * 2}" fill="#0f2e5a" stroke="#38bdf8" stroke-width="1.5"/>')

        # Draw 4 Arms in Isometric Projection
        iso_coords = [
            (arm_len * cos30, arm_len * sin30),      # Front-Right
            (-arm_len * cos30, arm_len * sin30),     # Front-Left
            (-arm_len * cos30, -arm_len * sin30),    # Rear-Left
            (arm_len * cos30, -arm_len * sin30)      # Rear-Right
        ]

        prop_rx = 34 * scale
        prop_ry = 12 * scale

        for i, (ix, iy) in enumerate(iso_coords):
            mx, my = cx + ix, cy + iy
            # Arm
            out.append(f'<line x1="{cx}" y1="{cy}" x2="{mx}" y2="{my}" stroke="#38bdf8" stroke-width="4"/>')
            out.append(f'<line x1="{cx}" y1="{cy}" x2="{mx}" y2="{my}" stroke="#0b172a" stroke-width="1.5"/>')

            # Motor Cylinder in 3D
            out.append(f'<ellipse cx="{mx}" cy="{my}" rx="8" ry="4" fill="#0b172a" stroke="#38bdf8" stroke-width="1.5"/>')
            out.append(f'<rect x="{mx - 8}" y="{my - 8}" width="16" height="8" fill="#0b172a" stroke="#38bdf8" stroke-width="1"/>')
            out.append(f'<ellipse cx="{mx}" cy="{my - 8}" rx="8" ry="4" fill="{spec.color_accent}" stroke="#38bdf8" stroke-width="1"/>')

            # Tilted Propeller Ring
            out.append(f'<ellipse cx="{mx}" cy="{my - 8}" rx="{prop_rx}" ry="{prop_ry}" fill="none" stroke="{spec.color_accent}" stroke-width="1.5" stroke-dasharray="6,4"/>')

        out.append('</g>')
        return "\n".join(out)

    @classmethod
    def _draw_dimension_line(cls, x1: float, y1: float, x2: float, y2: float, text: str) -> str:
        """Draws dimension line with extension arrows and centered text."""
        mid_x = (x1 + x2) / 2.0
        mid_y = (y1 + y2) / 2.0
        return f'''
        <g stroke="#38bdf8" stroke-width="1">
          <line x1="{x1}" y1="{y1 - 6}" x2="{x1}" y2="{y1 + 6}"/>
          <line x1="{x2}" y1="{y2 - 6}" x2="{x2}" y2="{y2 + 6}"/>
          <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" marker-start="url(#arrowStart)" marker-end="url(#arrowEnd)"/>
        </g>
        <rect x="{mid_x - 70}" y="{mid_y - 8}" width="140" height="15" fill="#07152b"/>
        <text x="{mid_x}" y="{mid_y + 3}" fill="#ffffff" font-size="9" text-anchor="middle" font-weight="bold">{text}</text>
        '''

    @classmethod
    def _draw_dimension_vertical(cls, x: float, y1: float, y2: float, text: str) -> str:
        mid_y = (y1 + y2) / 2.0
        return f'''
        <g stroke="#38bdf8" stroke-width="1">
          <line x1="{x - 6}" y1="{y1}" x2="{x + 6}" y2="{y1}"/>
          <line x1="{x - 6}" y1="{y2}" x2="{x + 6}" y2="{y2}"/>
          <line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" marker-start="url(#arrowStart)" marker-end="url(#arrowEnd)"/>
        </g>
        <rect x="{x - 8}" y="{mid_y - 45}" width="16" height="90" fill="#07152b"/>
        <text x="{x + 3}" y="{mid_y}" fill="#ffffff" font-size="9" text-anchor="middle" font-weight="bold" transform="rotate(-90, {x}, {mid_y})">{text}</text>
        '''

    @classmethod
    def _render_title_block(cls, spec: DroneDesignSpec, x: float, y: float, w: float, h: float) -> str:
        """ISO Technical Drawing Title Block at Bottom Right."""
        return f'''
        <g id="title_block" transform="translate({x}, {y})">
          <rect width="{w}" height="{h}" fill="#091c36" stroke="#38bdf8" stroke-width="1.5"/>
          <line x1="0" y1="32" x2="{w}" y2="32" stroke="#1d4e89" stroke-width="1"/>
          <line x1="0" y1="68" x2="{w}" y2="68" stroke="#1d4e89" stroke-width="1"/>
          <line x1="0" y1="104" x2="{w}" y2="104" stroke="#1d4e89" stroke-width="1"/>
          <line x1="{w * 0.6}" y1="32" x2="{w * 0.6}" y2="{h}" stroke="#1d4e89" stroke-width="1"/>

          <!-- Title Header -->
          <text x="12" y="22" fill="#38bdf8" font-size="12" font-weight="bold" letter-spacing="1">AEROGUARD AUTONOMOUS AEROSPACE SYSTEMS</text>
          
          <!-- Drawing Title -->
          <text x="12" y="50" fill="#94a3b8" font-size="8">DESIGNATION & MODEL:</text>
          <text x="12" y="62" fill="#ffffff" font-size="10" font-weight="bold">{spec.name.upper()}</text>

          <text x="{w * 0.6 + 10}" y="50" fill="#94a3b8" font-size="8">AIRFRAME CONFIG:</text>
          <text x="{w * 0.6 + 10}" y="62" fill="{spec.color_accent}" font-size="9" font-weight="bold">{spec.configuration.upper()}</text>

          <!-- Engineering Specs line -->
          <text x="12" y="85" fill="#94a3b8" font-size="8">DRAWING NUMBER:</text>
          <text x="12" y="97" fill="#38bdf8" font-size="9" font-weight="bold">AG-CAD-2026-X1</text>

          <text x="{w * 0.6 + 10}" y="85" fill="#94a3b8" font-size="8">STATUS & REV:</text>
          <text x="{w * 0.6 + 10}" y="97" fill="#10b981" font-size="9" font-weight="bold">RELEASED (REV C.4)</text>

          <!-- Approval line -->
          <text x="12" y="123" fill="#64748b" font-size="8">ENGINEER: AI AEROSPACE CORE | SHEET 01 OF 01</text>
          <text x="{w * 0.6 + 10}" y="123" fill="#64748b" font-size="8">UNITS: METRIC (mm)</text>
        </g>
        '''

    @classmethod
    def _render_spec_table(cls, spec: DroneDesignSpec, x: float, y: float) -> str:
        """Engineering Specification Summary Box."""
        items = [
            f"WHEELBASE:        {spec.wheelbase_mm:.0f} mm",
            f"PROPELLERS:       {spec.propeller_dia_inch:.1f} inch Carbon",
            f"TAKEOFF WT (AUW): {spec.auw_kg:.2f} kg",
            f"PAYLOAD CAP:      {spec.payload_capacity_kg:.2f} kg",
            f"BATTERY PACK:     {spec.battery_type}",
            f"EST. ENDURANCE:   {spec.flight_time_mins:.1f} mins",
            f"TOP SPEED:        {spec.max_speed_kmh:.0f} km/h"
        ]

        rows = []
        for i, item in enumerate(items):
            rows.append(f'<text x="{x + 12}" y="{y + 40 + i * 16}" fill="#cbd5e1" font-size="9">{item}</text>')

        box_h = 45 + len(items) * 16
        return f'''
        <g id="spec_box">
          <rect x="{x}" y="{y}" width="280" height="{box_h}" fill="rgba(9, 28, 54, 0.85)" stroke="#1d4e89" stroke-width="1"/>
          <rect x="{x}" y="{y}" width="280" height="24" fill="#0d2448"/>
          <text x="{x + 12}" y="{y + 16}" fill="#38bdf8" font-size="10" font-weight="bold" letter-spacing="1">PARAMETRIC ENGINEERING SPECS</text>
          {"".join(rows)}
        </g>
        '''

