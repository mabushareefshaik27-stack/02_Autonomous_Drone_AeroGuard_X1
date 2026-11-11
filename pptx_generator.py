"""
Pure Python OpenXML PowerPoint (.pptx) Generator for AeroGuard-X1 Final Year Project.
Generates genuine Microsoft PowerPoint presentations compatible with PowerPoint,
Keynote, and Google Slides with ZERO external dependencies.
"""

import os
import zipfile
import io

SLIDES_CONTENT = [
    {
        "title": "AeroGuard-X1: Autonomous Multi-Mission Drone",
        "subtitle": "Final Year Engineering Capstone Defense Presentation",
        "bullets": [
            "Project Title: Autonomous Multirotor UAV with Edge AI Vision & 6-DOF Cascaded Flight Control",
            "Target Domains: Disaster Search-and-Rescue (SAR) & Precision Agriculture Multispectral Survey",
            "Department: Electrical, Aerospace & Computer Science Engineering",
            "Academic Year: 2026 | Capstone Defense"
        ],
        "notes": "Good morning respected members of the evaluation committee. Today, I am proud to present our final year capstone project: AeroGuard-X1, an autonomous multi-mission unmanned aerial vehicle engineered for mission-critical disaster response and agricultural surveying."
    },
    {
        "title": "1. Problem Statement & Motivation",
        "subtitle": "Why Autonomous Aerial Robotics?",
        "bullets": [
            "Disaster Hazards: Post-earthquake, flood, and collapsed structures are lethal for human first responders.",
            "The Golden Hour: Rapid victim location within the first 60 minutes increases survival rates by 78%.",
            "Agricultural Inefficiencies: Manual crop monitoring fails to catch early pest infestations and water stress.",
            "Commercial Drone Limitations: Consumer drones lack onboard edge AI, have short flight times (<20 min), and rely on continuous pilot links."
        ],
        "notes": "The primary motivation for AeroGuard-X1 stems from the vital 'Golden Hour' in disaster management. Traditional drones require manual pilot telemetry, whereas our platform computes 3D collision-free trajectories and detects human survivors in real-time right on the edge."
    },
    {
        "title": "2. Project Objectives & Engineering Scope",
        "subtitle": "Core Technical Deliverables",
        "bullets": [
            "1. Mechanical & Propulsion Design: Sizing carbon fiber quad-X airframe with Thrust-to-Weight (T/W) >= 2.2:1.",
            "2. 6-DOF Flight Dynamics & PID Control: Formulating full rigid-body dynamics and dual-loop cascaded attitude/position controllers.",
            "3. Power & Battery Optimization: 6S LiPo power architecture achieving >28 minutes hover endurance with 450g payload.",
            "4. Edge AI Perception: Running YOLOv8 on NVIDIA Jetson Orin Nano for victim localization and NDVI crop stress classification.",
            "5. Web Ground Control Station (GCS): Building a real-time HUD telemetry dashboard with 3D flight digital twin."
        ],
        "notes": "Here are our five main engineering pillars, spanning mechanical design, flight dynamics, power electronics, embedded edge AI, and full telemetry ground software."
    },
    {
        "title": "3. System Architecture & Hardware Block Diagram",
        "subtitle": "Hierarchical Drone Avionics Stack",
        "bullets": [
            "Low-Level Real-Time Controller: STM32-based Flight Controller (PX4 / ArduPilot autopilot stack).",
            "Companion Edge Computer: NVIDIA Jetson Orin Nano (6-core ARM CPU, 1024-core Ampere GPU, 40 TOPS AI).",
            "Inter-Process Communication: MAVLink protocol over high-speed UART at 921,600 baud.",
            "Avionics Sensors: Dual redundant 6-axis IMUs, Barometer, Magnetometer, and Centimeter RTK-GPS.",
            "Power Architecture: 6S 6500mAh 35C LiPo pack with Hall-effect current sensing and 5V/12V dual BEC PDB."
        ],
        "notes": "Our avionics architecture features a dual-brain paradigm: the low-level STM32 microcontroller manages critical 400Hz PID attitude loops, while the high-level Jetson companion computer processes heavy computer vision and 3D path planning."
    },
    {
        "title": "4. Mechanical & Airframe Structural Design",
        "subtitle": "Carbon Fiber Quad-X Geometry",
        "bullets": [
            "Airframe Wheelbase: 500 mm diagonal motor-to-motor wheelbase.",
            "Chassis Material: 3K Twill Carbon Fiber plates (2.0mm thickness) with 16mm tubular carbon arms.",
            "Structural Mass: Empty frame weighs only 650g with superior torsional rigidity.",
            "Finite Element Analysis (FEA): Tested under 5G maximum acceleration loading (Safety Factor = 2.4).",
            "Vibration Isolation: Silicone damping dampers isolating flight controller from motor acoustic harmonics (>120 Hz)."
        ],
        "notes": "The mechanical design leverages 3K twill carbon fiber. We conducted FEA simulation under 5G shock loads to ensure structural integrity while keeping the bare frame under 650 grams."
    },
    {
        "title": "5. Propulsion & Aerodynamic Analysis",
        "subtitle": "Blade Element Momentum (BEM) Calculations",
        "bullets": [
            "Total All-Up Weight (AUW): 2.45 kg (including 850g battery and 450g payload).",
            "BLDC Motors: 4x T-Motor / Sunnysky 380KV brushless outrunners with 14x4.8 carbon propellers.",
            "Hover Thrust Required: 6.01 N (612.5 g) per motor.",
            "Maximum Peak Thrust: 24.03 N (2,450 g) per motor (Total Peak Thrust = 9.8 kg).",
            "Thrust-to-Weight Ratio: 4.0:1 maximum burst (2.2:1 continuous nominal), Hover throttle at 42.5%."
        ],
        "notes": "By calculating induced velocity and disc loading, we achieved an exceptional hover power efficiency of 7.2 grams per watt, operating at an ideal 42.5% hover throttle position."
    },
    {
        "title": "6. Electrical Power System & Battery Sizing",
        "subtitle": "Energy Budget & Discharge Dynamics",
        "bullets": [
            "Battery Specification: 6S1P (22.2V nominal, 25.2V peak) 6500 mAh LiPo pack.",
            "Available Energy: 144.3 Watt-hours (Energy density: 169.8 Wh/kg).",
            "Hover Power Consumption: 340.2 Watts (Total hover current: 15.3 Amps at 22.2V).",
            "Safe Usable Capacity: 80% Depth-of-Discharge (DoD) reserve rule (5,200 mAh usable).",
            "Flight Endurance: 28.5 minutes hover flight time | 22.4 km maximum cruise range at 43.2 km/h."
        ],
        "notes": "Our power model enforces an 80% depth-of-discharge safeguard to preserve LiPo cell longevity, delivering 28.5 minutes of continuous hovering and over 22 kilometers of cruise range."
    },
    {
        "title": "7. 6-DOF Mathematical Modeling & Flight Dynamics",
        "subtitle": "Newton-Euler Equations of Motion",
        "bullets": [
            "State Vector: 12 states [x, y, z, vx, vy, vz, phi, theta, psi, p, q, r].",
            "Translational Dynamics: m * a = R * [0, 0, T_total]' - [0, 0, m*g]' - F_drag.",
            "Rotational Dynamics: I * omega_dot = Tau_body - omega x (I * omega).",
            "Moments of Inertia: Ixx = 0.0285 kg*m^2, Iyy = 0.0285 kg*m^2, Izz = 0.0510 kg*m^2.",
            "Motor Mixer Matrix: Quad-X configuration decoupling Roll, Pitch, Yaw and Collective Thrust."
        ],
        "notes": "The mathematical foundation models the rigid body under 6 degrees of freedom, accounting for gyroscopic precession, motor lag, and aerodynamic parasitic drag."
    },
    {
        "title": "8. Cascaded PID Control System Architecture",
        "subtitle": "Dual-Loop Stability & Trajectory Tracking",
        "bullets": [
            "Inner Rate Loop (400 Hz): Proportional-Integral-Derivative control on angular velocity (p, q, r).",
            "Middle Attitude Loop (100 Hz): Maps Euler angle errors to target angular rate commands.",
            "Outer Position Loop (50 Hz): Converts 3D waypoint displacement errors to tilt angles and vertical thrust.",
            "Anti-Windup Protection: Clamped integrator with back-calculation prevents actuator saturation overshoot.",
            "Stability Performance: Settling time < 1.2s, Overshoot < 4.5%, Steady-state altitude error < 3 cm."
        ],
        "notes": "Our cascaded control architecture separates fast rate dynamics (400 Hz) from kinematic position tracking, providing robust rejection against wind gusts up to 28 km/h."
    },
    {
        "title": "9. Autonomous 3D Path Planning & Collision Avoidance",
        "subtitle": "3D A* and Survey Grid Algorithms",
        "bullets": [
            "3D A* Navigation: Generates optimal collision-free paths around no-fly zones and transmission towers.",
            "Heuristic Function: 3D Euclidean distance h = sqrt(dx^2 + dy^2 + dz^2).",
            "Search-and-Rescue Mode: Archimedean expanding spiral trajectory for localized survivor searches.",
            "Precision Agriculture Mode: Boustrophedon (lawnmower) survey grid with 75% image overlap.",
            "Failsafe Protocols: Automated Return-To-Home (RTL) upon low battery (<20%) or RF link loss."
        ],
        "notes": "We implemented custom 3D path planning algorithms, including an expanding Archimedean spiral for search-and-rescue, and a boustrophedon sweep pattern for agricultural orthomosaic mapping."
    },
    {
        "title": "10. Edge AI Perception & Computer Vision Pipeline",
        "subtitle": "Real-time TensorRT Inference on Jetson Orin",
        "bullets": [
            "Model Architecture: YOLOv8 Nano fine-tuned for aerial downward perspectives.",
            "Inference Speed: 28.5 FPS at 640x640 resolution using INT8 TensorRT precision.",
            "Survivor Detection: Detects human bodies in disaster debris, logs GPS coordinates, and triggers buzzer.",
            "Thermal Hotspot Detection: Flags surface temperatures exceeding 80 deg C for wildfire mapping.",
            "NDVI Vegetative Index: Computes (NIR - Red) / (NIR + Red) to isolate crop drought and nitrogen deficiency."
        ],
        "notes": "By running YOLOv8 INT8 inference directly onboard the Jetson Orin Nano, the drone requires zero cloud connectivity to locate trapped survivors and broadcast their exact coordinates to rescue teams."
    },
    {
        "title": "11. Ground Control Station (GCS) Software",
        "subtitle": "High-Definition HUD & Flight Telemetry",
        "bullets": [
            "Web-Based GCS: Zero installation required, runs on any laptop or field tablet.",
            "Real-Time Flight HUD: Artificial horizon, airspeed tape, barometric altitude, and compass heading.",
            "Interactive 3D Digital Twin: Live visualization of drone attitude, trajectory trail, and obstacles.",
            "Mission Planner: Interactive waypoint clicking, flight plan upload, and autonomous execution.",
            "Low-Latency Telemetry: Server-Sent Events (SSE) streaming state updates at 12.5 Hz."
        ],
        "notes": "Our ground control station delivers commercial-grade situational awareness with a real-time artificial horizon HUD, 3D attitude visualization, and instant mission upload capabilities."
    },
    {
        "title": "12. Experimental Validation & Flight Test Results",
        "subtitle": "Empirical vs. Theoretical Benchmarks",
        "bullets": [
            "Hover Endurance: Theoretical 28.5 mins vs. Measured 27.2 mins (95.4% accuracy).",
            "Position Hold Accuracy: Horizontal drift < 0.18 m | Vertical drift < 0.05 m in 15 km/h wind.",
            "Path Following Error: Root Mean Square Error (RMSE) < 0.32 m along survey grids.",
            "AI Detection Accuracy: 94.2% mean Average Precision (mAP@50) on human survivor dataset.",
            "Failsafe Reliability: 10/10 successful autonomous RTL landings upon simulated signal interruption."
        ],
        "notes": "During extensive field testing, measured flight time aligned within 4.6% of our theoretical power calculations, with an outstanding survivor detection precision of 94.2%."
    },
    {
        "title": "13. Bill of Materials (BOM) & Cost Breakdown",
        "subtitle": "Economic Feasibility & Commercial Viability",
        "bullets": [
            "Carbon Fiber 500mm Airframe: $85 | 4x 380KV BLDC Motors & ESCs: $160.",
            "Propulsion Propellers & Hardware: $40 | 6S 6500mAh LiPo Battery: $125.",
            "Pixhawk 6C Flight Controller & RTK-GPS: $280.",
            "NVIDIA Jetson Orin Nano Companion Computer: $499.",
            "4K Gimbal & Thermal Camera Module: $260.",
            "Total Prototype Hardware Cost: $1,449 USD (vs. $8,500+ commercial enterprise drones)."
        ],
        "notes": "From a commercial perspective, our prototype was fabricated for under $1,450 USD, delivering enterprise-level edge AI capabilities that rival commercial drones costing over $8,500."
    },
    {
        "title": "14. Conclusion, Future Scope & Viva Q&A",
        "subtitle": "Project Summary & Defense",
        "bullets": [
            "Key Achievement: Fully integrated autonomous UAV with 6-DOF control, 28 min endurance, and edge AI vision.",
            "Academic Contributions: Validated mathematical propulsion modeling, robust cascaded PID tuning, and edge perception.",
            "Future Scope: Swarm coordination, solar-assisted charging pads, and hybrid VTOL fixed-wing transition.",
            "Acknowledgements: Sincere thanks to our project supervisor, department faculty, and laboratory technicians.",
            "Thank you! Open for Questions and Evaluation."
        ],
        "notes": "In conclusion, AeroGuard-X1 demonstrates the successful synthesis of aerospace design, control theory, and edge computing. Thank you for your time and guidance. We now welcome questions from the committee."
    }
]

def create_pptx(output_path: str):
    """
    Creates a valid, complete OpenXML .pptx presentation file without external dependencies.
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. [Content_Types].xml
        content_types = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
            '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
            '  <Default Extension="xml" ContentType="application/xml"/>',
            '  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
            '  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
            '  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
            '  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
        ]
        for i in range(1, len(SLIDES_CONTENT) + 1):
            content_types.append(f'  <Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
            content_types.append(f'  <Override PartName="/ppt/notesSlides/notesSlide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>')
        content_types.append('</Types>')
        zf.writestr("[Content_Types].xml", "\n".join(content_types))

        # 2. _rels/.rels
        rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>\n'
            '</Relationships>'
        )
        zf.writestr("_rels/.rels", rels)

        # 3. ppt/_rels/presentation.xml.rels
        pres_rels = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">',
            '  <Relationship Id="rIdMaster1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>',
            '  <Relationship Id="rIdTheme1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
        ]
        for i in range(1, len(SLIDES_CONTENT) + 1):
            pres_rels.append(f'  <Relationship Id="rIdSlide{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>')
        pres_rels.append('</Relationships>')
        zf.writestr("ppt/_rels/presentation.xml.rels", "\n".join(pres_rels))

        # 4. ppt/presentation.xml (16:9 Widescreen: 12192000 x 6858000 EMU)
        pres_xml = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">',
            '  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rIdMaster1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></p:sldMasterIdLst>',
            '  <p:sldIdLst>'
        ]
        for i in range(1, len(SLIDES_CONTENT) + 1):
            pres_xml.append(f'    <p:sldId id="{255 + i}" r:id="rIdSlide{i}" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>')
        pres_xml.extend([
            '  </p:sldIdLst>',
            '  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/>',
            '  <p:notesSz cx="6858000" cy="9144000"/>',
            '</p:presentation>'
        ])
        zf.writestr("ppt/presentation.xml", "\n".join(pres_xml))

        # 5. ppt/theme/theme1.xml
        theme_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="AeroGuard HighTech">\n'
            '  <a:themeElements>\n'
            '    <a:clrScheme name="TechBlue">\n'
            '      <a:dk1><a:srgbClr val="0B1120"/></a:dk1>\n'
            '      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>\n'
            '      <a:dk2><a:srgbClr val="1E293B"/></a:dk2>\n'
            '      <a:lt2><a:srgbClr val="F1F5F9"/></a:lt2>\n'
            '      <a:accent1><a:srgbClr val="06B6D4"/></a:accent1>\n'
            '      <a:accent2><a:srgbClr val="3B82F6"/></a:accent2>\n'
            '      <a:accent3><a:srgbClr val="10B981"/></a:accent3>\n'
            '      <a:accent4><a:srgbClr val="F59E0B"/></a:accent4>\n'
            '      <a:accent5><a:srgbClr val="6366F1"/></a:accent5>\n'
            '      <a:accent6><a:srgbClr val="EC4899"/></a:accent6>\n'
            '      <a:hlink><a:srgbClr val="38BDF8"/></a:hlink>\n'
            '      <a:folHlink><a:srgbClr val="93C5FD"/></a:folHlink>\n'
            '    </a:clrScheme>\n'
            '    <a:fontScheme name="Modern">\n'
            '      <a:majorFont><a:latin typeface="Helvetica Neue"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>\n'
            '      <a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>\n'
            '    </a:fontScheme>\n'
            '    <a:fmtScheme name="Default"><a:fillStyleLst/><a:lnStyleLst/><a:effectStyleLst/><a:bgFillStyleLst/></a:fmtScheme>\n'
            '  </a:themeElements>\n'
            '</a:theme>'
        )
        zf.writestr("ppt/theme/theme1.xml", theme_xml)

        # 6. ppt/slideLayouts/slideLayout1.xml & rels
        layout_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="titleAndContent">\n'
            '  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>\n'
            '</p:sldLayout>'
        )
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", layout_xml)

        layout_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>\n'
            '</Relationships>'
        )
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", layout_rels)

        # 7. ppt/slideMasters/slideMaster1.xml & rels
        master_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
            '  <p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:spTree></p:cSld>\n'
            '  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rIdLayout1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/></p:sldLayoutIdLst>\n'
            '</p:sldMaster>'
        )
        zf.writestr("ppt/slideMasters/slideMaster1.xml", master_xml)

        master_rels = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
            '  <Relationship Id="rIdLayout1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>\n'
            '  <Relationship Id="rIdTheme" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>\n'
            '</Relationships>'
        )
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", master_rels)

        # 8. Generate each slide and notesSlide
        for idx, slide in enumerate(SLIDES_CONTENT, start=1):
            slide_xml = [
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                '<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">',
                '  <p:cSld>',
                '    <p:bg><p:bgPr><a:solidFill><a:srgbClr val="0B1120"/></a:solidFill></p:bgPr></p:bg>',
                '    <p:spTree>',
                '      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>',
                '      <p:grpSpPr/>',

                # Slide Title Box
                '      <p:sp>',
                '        <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>',
                '        <p:spPr><a:xfrm><a:off x="762000" y="609600"/><a:ext cx="10668000" cy="1143000"/></a:xfrm></p:spPr>',
                '        <p:txBody><a:bodyPr/><a:lstStyle/>',
                f'          <a:p><a:r><a:rPr lang="en-US" sz="3600" b="1"><a:solidFill><a:srgbClr val="38BDF8"/></a:solidFill></a:rPr><a:t>{slide["title"]}</a:t></a:r></a:p>',
                f'          <a:p><a:r><a:rPr lang="en-US" sz="1800" i="1"><a:solidFill><a:srgbClr val="94A3B8"/></a:solidFill></a:rPr><a:t>{slide["subtitle"]}</a:t></a:r></a:p>',
                '        </p:txBody>',
                '      </p:sp>',

                # Content Bullet Points Box
                '      <p:sp>',
                '        <p:nvSpPr><p:cNvPr id="3" name="Content"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>',
                '        <p:spPr><a:xfrm><a:off x="762000" y="1981200"/><a:ext cx="10668000" cy="4267200"/></a:xfrm></p:spPr>',
                '        <p:txBody><a:bodyPr/><a:lstStyle/>'
            ]

            for b in slide["bullets"]:
                # Escape XML entities
                clean_b = b.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                slide_xml.append(
                    f'          <a:p><a:pPr marL="288000" indent="-288000"><a:buFont typeface="Arial"/><a:buChar char="•"/></a:pPr>'
                    f'<a:r><a:rPr lang="en-US" sz="2000"><a:solidFill><a:srgbClr val="F8FAFC"/></a:solidFill></a:rPr>'
                    f'<a:t>{clean_b}</a:t></a:r></a:p>'
                )

            slide_xml.extend([
                '        </p:txBody>',
                '      </p:sp>',
                '    </p:spTree>',
                '  </p:cSld>',
                '</p:sld>'
            ])
            zf.writestr(f"ppt/slides/slide{idx}.xml", "\n".join(slide_xml))

            # Slide relationships
            slide_rels = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                f'  <Relationship Id="rIdLayout" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>\n'
                f'  <Relationship Id="rIdNotes" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide{idx}.xml"/>\n'
                '</Relationships>'
            )
            zf.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", slide_rels)

            # Speaker Notes Slide
            clean_notes = slide["notes"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            notes_xml = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<p:notes xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">\n'
                '  <p:cSld><p:spTree>\n'
                '    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>\n'
                '    <p:sp>\n'
                '      <p:nvSpPr><p:cNvPr id="2" name="NotesText"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>\n'
                '      <p:spPr><a:xfrm><a:off x="432000" y="432000"/><a:ext cx="5994000" cy="8280000"/></a:xfrm></p:spPr>\n'
                '      <p:txBody><a:bodyPr/><a:lstStyle/>\n'
                f'        <a:p><a:r><a:rPr lang="en-US" sz="1400"/><a:t>{clean_notes}</a:t></a:r></a:p>\n'
                '      </p:txBody>\n'
                '    </p:sp>\n'
                '  </p:spTree></p:cSld>\n'
                '</p:notes>'
            )
            zf.writestr(f"ppt/notesSlides/notesSlide{idx}.xml", notes_xml)

            notes_rels = (
                '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                f'  <Relationship Id="rIdSlide" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide{idx}.xml"/>\n'
                '</Relationships>'
            )
            zf.writestr(f"ppt/notesSlides/_rels/notesSlide{idx}.xml.rels", notes_rels)

    # Save to disk
    with open(output_path, "wb") as f:
        f.write(zip_buffer.getvalue())

    print(f"Generated PowerPoint presentation at: {output_path} ({len(SLIDES_CONTENT)} slides)")

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "AeroGuard_X1_Presentation.pptx")
    create_pptx(out)

