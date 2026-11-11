# AeroGuard-X1: Autonomous Multi-Mission Drone Project

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Capstone%20Defense%20Ready-emerald.svg)]()
[![Presentation](https://img.shields.io/badge/Presentation-PowerPoint%20.pptx%20%2B%20HTML5-cyan.svg)]()

A complete final year capstone engineering project featuring an autonomous multirotor aerial vehicle with 6-DOF cascaded PID flight control, Blade Element Momentum (BEM) aerodynamic sizing, 6S LiPo power management, 3D A* collision avoidance, and onboard YOLOv8 Edge AI perception for disaster search-and-rescue and precision agriculture.

---

## 🌟 Deliverables & Features

1. **AI Prompt-to-Blueprint & Image Studio (`blueprint.html`)**:
   - Takes any natural language prompt (e.g., *"Heavy-lift agricultural hexacopter with 20L spray tank"*, *"Stealth tactical surveillance quadcopter with FLIR camera"*, *"Solar-assisted search-and-rescue VTOL quadplane"*).
   - Powered by **Google Gemini API** (`GeminiDroneVisionEngine`):
     - **📸 AI Photorealistic Drone Renders**: Generates realistic high-resolution drone concept images.
     - **📐 Technical CAD Blueprints**: Generates authentic ISO-compliant technical CAD blueprints with 4-view orthographic projections (Top Plan, Front Elevation, Side Profile, Isometric 3D), dimension callouts, and title blocks.
     - **🧠 Gemini Engineering Rationale**: Provides AI aerospace analysis of aerodynamic efficiency, structural rigidity, and mission viability.
   - One-click export to **Vector CAD (.SVG)**, **High-Resolution Blueprint / Render Image (.PNG)**, and **JSON Spec Sheet**.

2. **Power Presentation Deck**:
   - **`AeroGuard_X1_Presentation.pptx`**: Genuine 15-slide widescreen PowerPoint presentation with presenter notes for every slide. Open in PowerPoint, Keynote, or Google Slides.
   - **Interactive Web Deck (`presentation.html`)**: High-impact browser presentation with defense timer (press `N` for notes, `O` for overview, `F` for fullscreen, `P` for PDF).

3. **Tactical Ground Control Station (GCS) (`gcs.html`)**:
   - Primary Flight Display (PFD) HUD with artificial horizon, airspeed tape, altimeter tape, and heading compass.
   - 3D Flight Digital Twin with rotating quadcopter, spinning propellers, trajectory trail, and obstacles.
   - Live Gimbal Edge AI perception feed with bounding box tracking.

4. **Engineering Thesis (`FINAL_PROJECT_THESIS.md`)**:
   - 13-chapter comprehensive project thesis complete with mathematical derivations, FEA airframe analysis, propulsion calculations, BOM cost analysis, and external examiner viva Q&A prep.

---

## 🚀 Quick Start

### 1. Launch Ground Station & Presentation Portal
```bash
python3 start.py
```
Opens in your browser:
- **Presentation Deck**: `http://localhost:8090/presentation.html`
- **Ground Control Station**: `http://localhost:8090/gcs.html`
- **Download PowerPoint**: `http://localhost:8090/api/drone/download-pptx`

### 2. Engineering Calculations & AI Blueprint via CLI
```bash
# Generate CAD blueprint and specs from a prompt:
python3 cli.py blueprint --prompt "Heavy-lift agricultural hexacopter with 20L spray tank" --output hexacopter_blueprint.svg

# Calculate aerodynamic & battery performance:
python3 cli.py specs

# Display Bill of Materials & commercial cost breakdown:
python3 cli.py bom

# Run 6-DOF closed-loop PID trajectory simulation:
python3 cli.py simulate --target 10 5 15 --steps 25
```

### 3. Run Automated Unit Tests
```bash
python3 -m unittest discover tests
```

---

## 📁 Project Structure

```
02_Autonomous_Drone_AeroGuard_X1/
├── drone_engine/
│   ├── propulsion_power.py       # Aerodynamics, thrust-to-weight, LiPo endurance
│   ├── physics_6dof.py           # 6-DOF Newton-Euler rigid body dynamics & mixer
│   ├── flight_controller.py      # Cascaded PID attitude, rate & position controllers
│   ├── path_planner.py           # 3D A* obstacle avoidance & SAR/Agri mission planner
│   ├── vision_ai.py              # Onboard YOLOv8 edge vision & NDVI multispectral analysis
│   ├── blueprint_generator.py    # ISO-compliant CAD blueprint synthesis engine
│   └── gemini_vision_generator.py# Google Gemini API AI image & aerospace rationale engine
├── gcs/
│   └── server.py                 # Telemetry streaming server (12.5 Hz SSE & REST)
├── static/
│   ├── index.html                # Project portal landing page
│   ├── blueprint.html            # AI Prompt-to-Blueprint & Image Studio
│   ├── presentation.html         # Interactive 15-Slide Power Defense Deck
│   ├── gcs.html                  # Tactical Ground Control Station (PFD HUD + 3D Twin)
│   ├── images/                   # High-res photorealistic drone render assets
│   ├── css/ (blueprint.css, presentation.css, gcs.css)
│   └── js/  (blueprint.js, presentation.js, gcs_hud.js, gcs_app.js)
├── pptx_generator.py             # Pure Python OpenXML PowerPoint (.pptx) builder
├── AeroGuard_X1_Presentation.pptx # The generated PowerPoint presentation
├── cli.py                        # Command-line engineering calculator & mission runner
├── FINAL_PROJECT_THESIS.md       # Complete final year capstone thesis report
├── tests/test_drone_engine.py    # Automated test suite (11/11 unit tests passing)
└── start.py                      # One-click startup launcher
```

