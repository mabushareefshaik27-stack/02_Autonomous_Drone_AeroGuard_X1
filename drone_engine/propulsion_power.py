"""
Propulsion, Aerodynamics, and Power Sizing Models for AeroGuard-X1 Quadcopter.
Implements Blade Element Momentum approximations, motor-propeller matching,
LiPo battery discharge dynamics, and flight endurance calculations.
"""

import math
from typing import Dict, Any

# Standard Physical Constants
GRAVITY = 9.80665          # m/s^2
AIR_DENSITY_SEA_LEVEL = 1.225  # kg/m^3

class DroneConfiguration:
    """Default parameters for AeroGuard-X1 Autonomous Quadcopter"""
    def __init__(
        self,
        frame_weight_kg: float = 0.65,        # 500mm Carbon Fiber Quad-X
        motor_weight_each_kg: float = 0.12,   # 4x BLDC Motors
        esc_weight_each_kg: float = 0.035,    # 4x 40A DShot600 ESCs
        battery_capacity_mah: float = 6500.0, # 6S 22.2V 35C LiPo
        battery_cells_s: int = 6,             # 6S = 22.2V nominal
        battery_weight_kg: float = 0.85,      # Battery mass
        avionics_weight_kg: float = 0.28,     # Pixhawk 6C + Jetson Orin Nano + RTK GPS
        payload_weight_kg: float = 0.45,      # 4K 3-Axis Gimbal + Thermal / NDVI sensor
        propeller_diameter_inch: float = 14.0,# 14x4.8 Carbon fiber propellers
        propeller_pitch_inch: float = 4.8,
        motor_kv: float = 380.0,              # Low KV for high torque & efficiency
        motor_internal_res_ohm: float = 0.085,# Motor winding resistance
        battery_c_rating: float = 35.0,
        battery_cell_res_ohm: float = 0.003   # 3 mOhm per cell
    ):
        self.frame_weight_kg = frame_weight_kg
        self.motor_weight_each_kg = motor_weight_each_kg
        self.esc_weight_each_kg = esc_weight_each_kg
        self.battery_capacity_mah = battery_capacity_mah
        self.battery_cells_s = battery_cells_s
        self.battery_weight_kg = battery_weight_kg
        self.avionics_weight_kg = avionics_weight_kg
        self.payload_weight_kg = payload_weight_kg
        self.propeller_diameter_inch = propeller_diameter_inch
        self.propeller_pitch_inch = propeller_pitch_inch
        self.motor_kv = motor_kv
        self.motor_internal_res_ohm = motor_internal_res_ohm
        self.battery_c_rating = battery_c_rating
        self.battery_cell_res_ohm = battery_cell_res_ohm
        self.num_rotors = 4

    @property
    def empty_weight_kg(self) -> float:
        """Structural mass without battery and payload"""
        return (
            self.frame_weight_kg +
            (self.motor_weight_each_kg * self.num_rotors) +
            (self.esc_weight_each_kg * self.num_rotors) +
            self.avionics_weight_kg
        )

    @property
    def all_up_weight_kg(self) -> float:
        """Total Takeoff Weight (AUW) in kilograms"""
        return self.empty_weight_kg + self.battery_weight_kg + self.payload_weight_kg

    @property
    def nominal_voltage(self) -> float:
        """Nominal pack voltage (3.7V per cell)"""
        return self.battery_cells_s * 3.7

    @property
    def max_voltage(self) -> float:
        """Full charge pack voltage (4.2V per cell)"""
        return self.battery_cells_s * 4.2

    @property
    def cutoff_voltage(self) -> float:
        """Safe discharge limit (3.3V per cell)"""
        return self.battery_cells_s * 3.3

    @property
    def battery_internal_resistance(self) -> float:
        """Total battery pack internal resistance"""
        return self.battery_cells_s * self.battery_cell_res_ohm

class PropulsionEngine:
    """
    Computes thrust, power consumption, motor aerodynamics, and battery runtime.
    """

    @staticmethod
    def calculate_aerodynamics(config: DroneConfiguration, air_density: float = AIR_DENSITY_SEA_LEVEL) -> Dict[str, Any]:
        """
        Calculates propeller disc area, required hover thrust, power, and efficiency metrics.
        """
        mass = config.all_up_weight_kg
        weight_n = mass * GRAVITY
        
        # Hover thrust needed per motor
        hover_thrust_per_motor_n = weight_n / config.num_rotors
        hover_thrust_per_motor_g = (hover_thrust_per_motor_n / GRAVITY) * 1000.0

        # Propeller geometry (convert inches to meters)
        d_meters = config.propeller_diameter_inch * 0.0254
        radius_m = d_meters / 2.0
        prop_area_single = math.pi * (radius_m ** 2)
        total_disc_area = prop_area_single * config.num_rotors

        # Disc Loading (Total Weight / Total Disc Area) [N/m^2]
        disc_loading_n_m2 = weight_n / total_disc_area

        # Induced Velocity at hover from Momentum Theory: v_i = sqrt(T / (2 * rho * A))
        induced_velocity_m_s = math.sqrt(weight_n / (2.0 * air_density * total_disc_area))

        # Ideal Induced Power: P_induced = T * v_i
        ideal_hover_power_watts = weight_n * induced_velocity_m_s

        # Figure of Merit (FM) for multirotor propellers typically ~ 0.65 - 0.72
        figure_of_merit = 0.68
        prop_profile_power_factor = 1.15
        actual_aerodynamic_power_watts = (ideal_hover_power_watts / figure_of_merit) * prop_profile_power_factor

        # Electrical power accounting for BLDC motor efficiency (~84%) and ESC efficiency (~95%)
        motor_efficiency = 0.84
        esc_efficiency = 0.95
        total_hover_electrical_power_watts = actual_aerodynamic_power_watts / (motor_efficiency * esc_efficiency)

        # Power per motor
        hover_power_per_motor_w = total_hover_electrical_power_watts / config.num_rotors

        # Hover current draw at nominal voltage
        hover_current_amps = total_hover_electrical_power_watts / config.nominal_voltage

        # Max thrust capability:
        # Standard 14" prop on 380KV @ 6S produces ~2,400g (23.5 N) max thrust per motor
        max_thrust_per_motor_g = 2450.0
        max_thrust_per_motor_n = (max_thrust_per_motor_g / 1000.0) * GRAVITY
        total_max_thrust_n = max_thrust_per_motor_n * config.num_rotors
        total_max_thrust_kg = total_max_thrust_n / GRAVITY

        # Thrust to Weight Ratio (T/W)
        thrust_to_weight_ratio = total_max_thrust_n / weight_n

        # Hover throttle percentage
        hover_throttle_pct = (hover_thrust_per_motor_g / max_thrust_per_motor_g) * 100.0

        return {
            "all_up_weight_kg": round(mass, 3),
            "total_weight_n": round(weight_n, 2),
            "hover_thrust_per_motor_g": round(hover_thrust_per_motor_g, 1),
            "max_thrust_per_motor_g": round(max_thrust_per_motor_g, 1),
            "total_max_thrust_kg": round(total_max_thrust_kg, 2),
            "thrust_to_weight_ratio": round(thrust_to_weight_ratio, 2),
            "hover_throttle_pct": round(hover_throttle_pct, 1),
            "disc_loading_n_m2": round(disc_loading_n_m2, 2),
            "induced_velocity_m_s": round(induced_velocity_m_s, 2),
            "hover_electrical_power_watts": round(total_hover_electrical_power_watts, 1),
            "hover_current_amps": round(hover_current_amps, 2),
            "power_loading_g_per_w": round((mass * 1000.0) / total_hover_electrical_power_watts, 2)
        }

    @staticmethod
    def calculate_battery_endurance(config: DroneConfiguration, hover_current_amps: float) -> Dict[str, Any]:
        """
        Calculates safe battery endurance, flight time at hover, cruise range, and voltage sag.
        Applies standard 80% Depth-of-Discharge (DoD) reserve rule for LiPo safety.
        """
        capacity_ah = config.battery_capacity_mah / 1000.0
        usable_capacity_ah = capacity_ah * 0.80  # 80% DoD

        # Hover flight time in minutes: (Usable Ah / Current A) * 60
        flight_time_hover_mins = (usable_capacity_ah / max(0.1, hover_current_amps)) * 60.0

        # Fast cruise forward flight (typically ~1.25x hover power due to parasitic drag)
        cruise_speed_m_s = 12.0  # 43.2 km/h
        cruise_current_amps = hover_current_amps * 1.22
        flight_time_cruise_mins = (usable_capacity_ah / cruise_current_amps) * 60.0
        flight_range_km = (cruise_speed_m_s * (flight_time_cruise_mins * 60.0)) / 1000.0

        # Maximum Continuous Discharge Current based on C-rating
        max_continuous_current_a = capacity_ah * config.battery_c_rating

        # Voltage Sag under hover current: V_loaded = V_nom - (I * R_internal)
        voltage_sag_hover_v = hover_current_amps * config.battery_internal_resistance
        loaded_hover_voltage_v = config.nominal_voltage - voltage_sag_hover_v

        # Energy density
        battery_energy_wh = capacity_ah * config.nominal_voltage
        energy_density_wh_kg = battery_energy_wh / max(0.01, config.battery_weight_kg)

        return {
            "battery_capacity_mah": config.battery_capacity_mah,
            "battery_cells": f"{config.battery_cells_s}S",
            "nominal_voltage_v": config.nominal_voltage,
            "loaded_hover_voltage_v": round(loaded_hover_voltage_v, 2),
            "voltage_sag_hover_v": round(voltage_sag_hover_v, 2),
            "hover_flight_time_mins": round(flight_time_hover_mins, 1),
            "cruise_flight_time_mins": round(flight_time_cruise_mins, 1),
            "operational_range_km": round(flight_range_km, 2),
            "cruise_speed_km_h": round(cruise_speed_m_s * 3.6, 1),
            "battery_energy_wh": round(battery_energy_wh, 1),
            "energy_density_wh_kg": round(energy_density_wh_kg, 1),
            "max_discharge_current_a": round(max_continuous_current_a, 1)
        }

