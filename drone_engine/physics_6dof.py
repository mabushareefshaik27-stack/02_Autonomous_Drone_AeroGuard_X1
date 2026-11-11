"""
6-DOF Rigid Body Flight Dynamics Simulator for AeroGuard-X1 Quadcopter.
Implements Newton-Euler translational and rotational equations of motion,
rotation matrices (Euler Z-Y-X), motor mixer matrix, and environmental drag.
"""

import math
from typing import Dict, Any, List, Tuple

GRAVITY = 9.80665

class Quadcopter6DOF:
    """
    Simulates real-time 6-DOF physics for a Quad-X multicopter.
    Earth Frame: East-North-Up (ENU) convention.
    Body Frame: Forward-Left-Up.
    """

    def __init__(self, mass_kg: float = 2.45, arm_length_m: float = 0.25):
        self.mass = mass_kg
        self.arm_length = arm_length_m  # Distance from CG to each motor

        # Principal Moments of Inertia (kg * m^2) for 500mm Carbon Quad
        self.Ixx = 0.0285
        self.Iyy = 0.0285
        self.Izz = 0.0510

        # Thrust and Torque coefficients
        self.kt = 1.12e-5  # Thrust = kt * omega^2 [N]
        self.kq = 2.35e-7  # Torque = kq * omega^2 [N*m]
        self.drag_coeff_linear = 0.18
        self.drag_coeff_rotational = 0.05

        # State Variables: Position (m) and Velocity (m/s) in World Frame (ENU)
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.pos_z = 0.0  # Altitude (m)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.vel_z = 0.0

        # Attitude: Euler Angles in Radians (Roll, Pitch, Yaw)
        self.roll = 0.0   # phi
        self.pitch = 0.0  # theta
        self.yaw = 0.0    # psi

        # Angular Rates in Body Frame (rad/s)
        self.rate_p = 0.0  # Roll rate
        self.rate_q = 0.0  # Pitch rate
        self.rate_r = 0.0  # Yaw rate

        # Motor Speeds (rad/s) [Motor 1 (Front-Right), 2 (Front-Left), 3 (Rear-Left), 4 (Rear-Right)]
        self.motor_rpms = [0.0, 0.0, 0.0, 0.0]
        self.hover_rpm = math.sqrt((self.mass * GRAVITY / 4.0) / self.kt) * (60.0 / (2.0 * math.pi))

        # Wind disturbances (m/s)
        self.wind_x = 0.0
        self.wind_y = 0.0

    def set_wind(self, wind_x_m_s: float, wind_y_m_s: float):
        self.wind_x = wind_x_m_s
        self.wind_y = wind_y_m_s

    def compute_rotation_matrix(self) -> List[List[float]]:
        """
        Calculates rotation matrix from Body to Earth frame R_body_to_earth (Z-Y-X sequence).
        """
        cr = math.cos(self.roll)
        sr = math.sin(self.roll)
        cp = math.cos(self.pitch)
        sp = math.sin(self.pitch)
        cy = math.cos(self.yaw)
        sy = math.sin(self.yaw)

        # Direct Direction Cosine Matrix (DCM)
        return [
            [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
            [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
            [-sp,     cp * sr,                cp * cr]
        ]

    def update_physics(self, motor_commands_rpm: List[float], dt: float = 0.02):
        """
        Advances the 6-DOF physics by time step dt seconds.
        motor_commands_rpm: list of 4 commanded motor RPMs.
        """
        dt = max(0.001, min(0.1, dt))
        motor_tau = 0.04  # 40ms motor response time lag

        # 1. Update motor speeds with first-order actuator lag
        for i in range(4):
            cmd = max(0.0, min(10500.0, motor_commands_rpm[i]))
            self.motor_rpms[i] += (cmd - self.motor_rpms[i]) * (dt / motor_tau)

        # Convert RPM to angular velocity (rad/s)
        w = [rpm * (2.0 * math.pi / 60.0) for rpm in self.motor_rpms]
        w_sq = [speed ** 2 for speed in w]

        # Individual Motor Thrusts (N)
        f1 = self.kt * w_sq[0]
        f2 = self.kt * w_sq[1]
        f3 = self.kt * w_sq[2]
        f4 = self.kt * w_sq[3]

        # Total Collective Thrust in Body Z-axis (pointing UP)
        total_thrust_body = f1 + f2 + f3 + f4

        # Quad-X Torques in Body Frame:
        # Arm angle for Quad-X is 45 degrees: sin(45) = cos(45) = d = L * sqrt(2)/2
        d = self.arm_length * (math.sqrt(2.0) / 2.0)

        # Roll torque tau_x (Motor 2 & 3 right vs 1 & 4 left)
        tau_roll = d * (-f1 + f2 + f3 - f4)
        # Pitch torque tau_y (Motor 1 & 2 front vs 3 & 4 rear)
        tau_pitch = d * (-f1 - f2 + f3 + f4)
        # Yaw torque tau_z (Reactive counter-torque from clockwise/counter-clockwise props)
        # Motors 1 & 3 CCW (+), Motors 2 & 4 CW (-)
        tau_yaw = self.kq * (-w_sq[0] + w_sq[1] - w_sq[2] + w_sq[3])

        # 2. Rotational Dynamics (Euler's equations)
        # p_dot = (tau_roll + (Iyy - Izz) * q * r) / Ixx
        # q_dot = (tau_pitch + (Izz - Ixx) * p * r) / Iyy
        # r_dot = (tau_yaw + (Ixx - Iyy) * p * q) / Izz
        p_dot = (tau_roll + (self.Iyy - self.Izz) * self.rate_q * self.rate_r - self.drag_coeff_rotational * self.rate_p) / self.Ixx
        q_dot = (tau_pitch + (self.Izz - self.Ixx) * self.rate_p * self.rate_r - self.drag_coeff_rotational * self.rate_q) / self.Iyy
        r_dot = (tau_yaw + (self.Ixx - self.Iyy) * self.rate_p * self.rate_q - self.drag_coeff_rotational * self.rate_r) / self.Izz

        self.rate_p += p_dot * dt
        self.rate_q += q_dot * dt
        self.rate_r += r_dot * dt

        # Kinematic equations (Angular rates -> Euler angle rates)
        # phi_dot = p + (q * sin(phi) + r * cos(phi)) * tan(theta)
        # theta_dot = q * cos(phi) - r * sin(phi)
        # psi_dot = (q * sin(phi) + r * cos(phi)) / cos(theta)
        cp = max(0.01, math.cos(self.pitch))
        sp = math.sin(self.pitch)
        sr = math.sin(self.roll)
        cr = math.cos(self.roll)

        roll_dot = self.rate_p + (self.rate_q * sr + self.rate_r * cr) * (sp / cp)
        pitch_dot = self.rate_q * cr - self.rate_r * sr
        yaw_dot = (self.rate_q * sr + self.rate_r * cr) / cp

        self.roll += roll_dot * dt
        self.pitch += pitch_dot * dt
        self.yaw += yaw_dot * dt

        # Keep yaw in [-pi, pi]
        self.yaw = (self.yaw + math.pi) % (2.0 * math.pi) - math.pi

        # 3. Translational Dynamics (Newton's 2nd Law)
        R = self.compute_rotation_matrix()

        # Thrust vector in world coordinates (Body Z is [0, 0, total_thrust_body])
        # World thrust = R * [0, 0, total_thrust_body]
        thrust_world_x = R[0][2] * total_thrust_body
        thrust_world_y = R[1][2] * total_thrust_body
        thrust_world_z = R[2][2] * total_thrust_body

        # Aerodynamic drag relative to apparent wind
        rel_vel_x = self.vel_x - self.wind_x
        rel_vel_y = self.vel_y - self.wind_y
        rel_vel_z = self.vel_z

        drag_x = 0.5 * self.drag_coeff_linear * rel_vel_x * abs(rel_vel_x)
        drag_y = 0.5 * self.drag_coeff_linear * rel_vel_y * abs(rel_vel_y)
        drag_z = 0.5 * self.drag_coeff_linear * rel_vel_z * abs(rel_vel_z)

        # Accelerations in World Frame
        acc_x = (thrust_world_x - drag_x) / self.mass
        acc_y = (thrust_world_y - drag_y) / self.mass
        acc_z = (thrust_world_z - (self.mass * GRAVITY) - drag_z) / self.mass

        # Ground contact collision constraint
        if self.pos_z <= 0.0 and acc_z < 0.0:
            self.pos_z = 0.0
            self.vel_z = 0.0
            acc_z = 0.0
            # Ground friction damps lateral velocities
            self.vel_x *= 0.8
            self.vel_y *= 0.8

        self.vel_x += acc_x * dt
        self.vel_y += acc_y * dt
        self.vel_z += acc_z * dt

        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt
        self.pos_z += self.vel_z * dt

        # Prevent underground penetration
        if self.pos_z < 0.0:
            self.pos_z = 0.0
            self.vel_z = 0.0

    def get_telemetry_state(self) -> Dict[str, Any]:
        """Returns instantaneous 6-DOF flight state in human and engineering units"""
        ground_speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
        total_speed = math.sqrt(self.vel_x**2 + self.vel_y**2 + self.vel_z**2)
        
        return {
            "position": {
                "x_m": round(self.pos_x, 2),
                "y_m": round(self.pos_y, 2),
                "altitude_m": round(self.pos_z, 2)
            },
            "velocity": {
                "vx_m_s": round(self.vel_x, 2),
                "vy_m_s": round(self.vel_y, 2),
                "vz_climb_m_s": round(self.vel_z, 2),
                "ground_speed_km_h": round(ground_speed * 3.6, 1),
                "airspeed_m_s": round(total_speed, 2)
            },
            "attitude_degrees": {
                "roll_deg": round(math.degrees(self.roll), 2),
                "pitch_deg": round(math.degrees(self.pitch), 2),
                "yaw_deg": round(math.degrees(self.yaw), 2)
            },
            "angular_rates_deg_s": {
                "p_roll_rate": round(math.degrees(self.rate_p), 2),
                "q_pitch_rate": round(math.degrees(self.rate_q), 2),
                "r_yaw_rate": round(math.degrees(self.rate_r), 2)
            },
            "motors_rpm": [round(rpm, 0) for rpm in self.motor_rpms],
            "hover_rpm_baseline": round(self.hover_rpm, 0)
        }

