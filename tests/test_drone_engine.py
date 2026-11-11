"""
Unit & Integration Test Suite for AeroGuard-X1 Drone Project.
"""

import unittest
import os
import zipfile
import math

from drone_engine.propulsion_power import DroneConfiguration, PropulsionEngine
from drone_engine.physics_6dof import Quadcopter6DOF
from drone_engine.flight_controller import CascadedFlightController
from drone_engine.path_planner import PathPlanner
from drone_engine.vision_ai import VisionAIEngine
from drone_engine.blueprint_generator import DroneBlueprintGenerator
from drone_engine.gemini_vision_generator import GeminiDroneVisionEngine
from pptx_generator import create_pptx

class TestDroneEngine(unittest.TestCase):

    def test_aerodynamics_and_thrust(self):
        cfg = DroneConfiguration()
        aero = PropulsionEngine.calculate_aerodynamics(cfg)
        self.assertGreater(aero["thrust_to_weight_ratio"], 2.0)
        self.assertGreater(aero["hover_thrust_per_motor_g"], 400.0)
        self.assertGreater(aero["power_loading_g_per_w"], 5.0)

    def test_battery_endurance(self):
        cfg = DroneConfiguration(battery_capacity_mah=6500)
        aero = PropulsionEngine.calculate_aerodynamics(cfg)
        endur = PropulsionEngine.calculate_battery_endurance(cfg, aero["hover_current_amps"])
        self.assertGreater(endur["hover_flight_time_mins"], 18.0)
        self.assertGreater(endur["operational_range_km"], 10.0)

    def test_6dof_rotation_matrix_orthogonality(self):
        drone = Quadcopter6DOF()
        drone.roll = 0.2
        drone.pitch = -0.15
        drone.yaw = 0.8
        R = drone.compute_rotation_matrix()

        # Check R * R^T = I
        for i in range(3):
            for j in range(3):
                dot_product = sum(R[i][k] * R[j][k] for k in range(3))
                expected = 1.0 if i == j else 0.0
                self.assertAlmostEqual(dot_product, expected, places=4)

    def test_cascaded_pid_controller(self):
        drone = Quadcopter6DOF()
        ctrl = CascadedFlightController(drone)
        ctrl.set_target(0.0, 0.0, 10.0)
        rpms = ctrl.update_control(dt=0.02)
        self.assertEqual(len(rpms), 4)
        for rpm in rpms:
            self.assertGreater(rpm, 2000.0)
            self.assertLessEqual(rpm, 10500.0)

    def test_path_planner_astar(self):
        planner = PathPlanner()
        planner.add_obstacle(x=10.0, y=10.0, z_min=0, z_max=30, radius=5.0)
        waypoints = planner.plan_3d_astar(start=(0, 0, 5), goal=(20, 20, 10))
        self.assertGreater(len(waypoints), 1)

    def test_vision_ai_inference(self):
        vision = VisionAIEngine()
        # Scan over survivor 1 location (18.5, 24.0)
        res = vision.scan_field_of_view(drone_x=18.5, drone_y=24.0, drone_alt=15.0)
        self.assertGreaterEqual(res["detections_count"], 1)

    def test_pptx_generation(self):
        out_path = os.path.join(os.path.dirname(__file__), "test_presentation.pptx")
        create_pptx(out_path)
        self.assertTrue(os.path.exists(out_path))
        zf = zipfile.ZipFile(out_path)
        self.assertIn("[Content_Types].xml", zf.namelist())
        self.assertIn("ppt/presentation.xml", zf.namelist())
        zf.close()
        os.remove(out_path)

    def test_blueprint_generation(self):
        spec = DroneBlueprintGenerator.synthesize_spec_from_prompt("Heavy-lift agricultural hexacopter with 20L spray tank")
        self.assertEqual(spec.configuration, "hexacopter")
        self.assertEqual(spec.mission_type, "agriculture")
        self.assertEqual(spec.payload_capacity_kg, 20.0)

        svg = DroneBlueprintGenerator.generate_svg_blueprint(spec, "multiview")
        self.assertTrue(svg.startswith("<svg"))
        self.assertTrue(svg.endswith("</svg>"))
        self.assertIn("AEROSPRAY-H6", svg.upper())

    def test_gemini_vision_engine_image_generation(self):
        engine = GeminiDroneVisionEngine()
        spec = DroneBlueprintGenerator.synthesize_spec_from_prompt("Long-range stealth reconnaissance quadcopter").to_dict()
        res = engine.generate_drone_image("Long-range stealth reconnaissance quadcopter", spec)
        self.assertIn("image_url", res)
        self.assertIn("source", res)
        self.assertTrue(res["image_url"].startswith("data:image") or res["image_url"].startswith("http") or res["image_url"].endswith(".png"))

    def test_gemini_vision_engine_static_assets(self):
        engine = GeminiDroneVisionEngine()
        agri_spec = DroneBlueprintGenerator.synthesize_spec_from_prompt("Heavy-lift agricultural hexacopter with 20L spray tank").to_dict()
        agri_res = engine.generate_drone_image("Heavy-lift agricultural hexacopter", agri_spec)
        self.assertEqual(agri_res["image_url"], "images/agricultural_hexacopter.png")

        cargo_spec = DroneBlueprintGenerator.synthesize_spec_from_prompt("Heavy logistics cargo octocopter with winch").to_dict()
        cargo_res = engine.generate_drone_image("Heavy logistics cargo octocopter", cargo_spec)
        self.assertEqual(cargo_res["image_url"], "images/heavy_cargo_drone.png")

    def test_gemini_engineering_rationale(self):
        engine = GeminiDroneVisionEngine()
        spec = DroneBlueprintGenerator.synthesize_spec_from_prompt("Compact ducted cinewhoop FPV drone").to_dict()
        analysis = engine.analyze_design_with_gemini("Compact ducted cinewhoop FPV drone", spec)
        self.assertIsInstance(analysis, str)
        self.assertGreater(len(analysis), 30)

if __name__ == "__main__":
    unittest.main()

