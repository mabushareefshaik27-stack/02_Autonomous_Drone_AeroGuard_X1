"""
Simulated Edge AI Perception Pipeline for AeroGuard-X1.
Models YOLOv8 object detection on NVIDIA Jetson Orin Nano,
thermal hotspot tracking, and multispectral NDVI crop health index analysis.
"""

import math
import random
from typing import Dict, Any, List

class VisionAIEngine:
    """
    Perception engine running edge inference onboard the drone companion computer.
    """

    def __init__(self):
        # Simulated ground targets
        self.targets = [
            {"id": "SURV_01", "type": "human_survivor", "x": 18.5, "y": 24.0, "status": "WAVING_FOR_HELP", "temp_c": 36.8},
            {"id": "SURV_02", "type": "human_survivor", "x": -32.0, "y": 45.0, "status": "TRAPPED_DEBRIS", "temp_c": 36.4},
            {"id": "FIRE_01", "type": "thermal_hotspot", "x": 5.0, "y": -40.0, "status": "ACTIVE_SMOLDER", "temp_c": 142.5},
            {"id": "CROP_ZONE_A", "type": "crop_field", "x": -25.0, "y": -20.0, "ndvi": 0.74, "status": "HEALTHY_VIGOROUS"},
            {"id": "CROP_ZONE_B", "type": "crop_field", "x": 40.0, "y": 10.0, "ndvi": 0.28, "status": "WATER_STRESSED"}
        ]
        self.inference_fps = 28.5  # Jetson Orin Nano INT8 TensorRT inference
        self.detections_log: List[Dict[str, Any]] = []

    def scan_field_of_view(
        self,
        drone_x: float,
        drone_y: float,
        drone_alt: float,
        gimbal_pitch_deg: float = -45.0,
        fov_deg: float = 84.0
    ) -> Dict[str, Any]:
        """
        Simulates camera frustum projected onto the ground plane.
        Identifies targets within field of view and computes bounding boxes.
        """
        # Ground footprint radius based on altitude
        footprint_radius = max(5.0, drone_alt * math.tan(math.radians(fov_deg / 2.0)))
        
        current_detections = []
        for t in self.targets:
            dist = math.sqrt((t["x"] - drone_x)**2 + (t["y"] - drone_y)**2)
            if dist <= footprint_radius:
                # Target visible!
                confidence = round(random.uniform(0.88, 0.98), 3)
                
                # Bounding box in normalized screen coordinates [ymin, xmin, ymax, xmax]
                # Center relative to FOV
                dx = (t["x"] - drone_x) / footprint_radius
                dy = (t["y"] - drone_y) / footprint_radius
                cx = 0.5 + (dx * 0.4)
                cy = 0.5 + (dy * 0.4)
                w = 0.12 * (15.0 / max(5.0, drone_alt))
                h = 0.16 * (15.0 / max(5.0, drone_alt))

                bbox = [
                    round(max(0.05, cy - h/2), 2),
                    round(max(0.05, cx - w/2), 2),
                    round(min(0.95, cy + h/2), 2),
                    round(min(0.95, cx + w/2), 2)
                ]

                detection_info = {
                    "target_id": t["id"],
                    "class_name": t["type"],
                    "confidence": confidence,
                    "ground_coords": {"x": t["x"], "y": t["y"]},
                    "distance_m": round(dist, 1),
                    "bbox_norm": bbox,
                    "metadata": {}
                }

                if t["type"] == "human_survivor":
                    detection_info["metadata"] = {
                        "status": t["status"],
                        "body_temp_c": t["temp_c"],
                        "alert_level": "CRITICAL_RESCUE_REQUIRED"
                    }
                elif t["type"] == "thermal_hotspot":
                    detection_info["metadata"] = {
                        "core_temp_c": t["temp_c"],
                        "hazard": "FIRE_IGNITION_HAZARD"
                    }
                elif t["type"] == "crop_field":
                    detection_info["metadata"] = {
                        "ndvi_index": t["ndvi"],
                        "vegetation_health": t["status"]
                    }

                current_detections.append(detection_info)

        return {
            "inference_fps": self.inference_fps,
            "footprint_radius_m": round(footprint_radius, 1),
            "detections_count": len(current_detections),
            "detections": current_detections
        }

