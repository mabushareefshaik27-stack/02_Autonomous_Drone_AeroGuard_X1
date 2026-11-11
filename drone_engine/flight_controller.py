"""
Cascaded PID Flight Control System for AeroGuard-X1 Multicopter.
Implements dual-loop attitude rate & angle controllers, altitude hold,
and horizontal position tracking with anti-windup integrators.
"""

import math
from typing import Dict, Any, List, Tuple
from .physics_6dof import Quadcopter6DOF, GRAVITY

class PID:
    """Standard PID Controller with derivative filtering and integrator anti-windup"""
    def __init__(self, kp: float, ki: float, kd: float, limit_min: float, limit_max: float):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.limit_min = limit_min
        self.limit_max = limit_max
        self.integral = 0.0
        self.prev_error = 0.0

    def reset(self):
        self.integral = 0.0
        self.prev_error = 0.0

    def update(self, error: float, dt: float) -> float:
        dt = max(0.001, dt)
        # Proportional
        p = self.kp * error
        # Integral with anti-windup clamp
        self.integral += error * dt
        i = self.ki * self.integral
        # Derivative
        d = self.kd * (error - self.prev_error) / dt
        self.prev_error = error

        output = p + i + d
        # Clamp output
        clamped = max(self.limit_min, min(self.limit_max, output))
        # Anti-windup: clamp back integrator if saturated
        if (output != clamped) and (self.ki > 0):
            self.integral -= error * dt
        return clamped

class CascadedFlightController:
    """
    PX4/ArduPilot-style Cascaded Flight Controller.
    Outer Loops: Position -> Velocity -> Attitude.
    Inner Loops: Attitude -> Angular Rates -> Motor Mixer.
    """

    def __init__(self, drone: Quadcopter6DOF):
        self.drone = drone

        # Rate Loop PIDs (Inner fastest loop: rad/s -> Torques)
        self.pid_roll_rate = PID(kp=0.18, ki=0.08, kd=0.006, limit_min=-0.8, limit_max=0.8)
        self.pid_pitch_rate = PID(kp=0.18, ki=0.08, kd=0.006, limit_min=-0.8, limit_max=0.8)
        self.pid_yaw_rate = PID(kp=0.25, ki=0.05, kd=0.002, limit_min=-0.4, limit_max=0.4)

        # Angle Loop PIDs (Middle loop: rad error -> rad/s command)
        self.pid_roll_angle = PID(kp=6.5, ki=0.0, kd=0.15, limit_min=-math.radians(35), limit_max=math.radians(35))
        self.pid_pitch_angle = PID(kp=6.5, ki=0.0, kd=0.15, limit_min=-math.radians(35), limit_max=math.radians(35))
        self.pid_yaw_angle = PID(kp=3.5, ki=0.0, kd=0.05, limit_min=-math.radians(120), limit_max=math.radians(120))

        # Altitude PIDs (Z Position -> Z Velocity -> Collective Thrust)
        self.pid_alt_pos = PID(kp=1.8, ki=0.0, kd=0.1, limit_min=-3.0, limit_max=4.0)
        self.pid_alt_vel = PID(kp=8.5, ki=2.5, kd=0.4, limit_min=-15.0, limit_max=25.0)

        # Horizontal Position PIDs (X, Y Position -> Velocity -> Desired Tilt)
        self.pid_pos_x = PID(kp=1.2, ki=0.0, kd=0.05, limit_min=-6.0, limit_max=6.0)
        self.pid_vel_x = PID(kp=0.22, ki=0.04, kd=0.03, limit_min=-math.radians(25), limit_max=math.radians(25))

        self.pid_pos_y = PID(kp=1.2, ki=0.0, kd=0.05, limit_min=-6.0, limit_max=6.0)
        self.pid_vel_y = PID(kp=0.22, ki=0.04, kd=0.03, limit_min=-math.radians(25), limit_max=math.radians(25))

        # Flight Modes: 'MANUAL', 'ALT_HOLD', 'POS_HOLD', 'AUTO_WAYPOINT', 'RETURN_TO_HOME'
        self.flight_mode = "POS_HOLD"
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 5.0  # Default 5 meters hover
        self.target_yaw = 0.0

    def set_target(self, x: float, y: float, z: float, yaw_deg: float = 0.0):
        self.target_x = x
        self.target_y = y
        self.target_z = max(0.0, z)
        self.target_yaw = math.radians(yaw_deg)

    def set_mode(self, mode: str):
        if mode in ["MANUAL", "ALT_HOLD", "POS_HOLD", "AUTO_WAYPOINT", "RETURN_TO_HOME"]:
            self.flight_mode = mode

    def update_control(self, dt: float = 0.02) -> List[float]:
        """
        Executes cascaded control loop and returns 4 motor RPM commands.
        """
        drone = self.drone

        # 1. Position & Velocity Loop (Earth Frame)
        if self.flight_mode in ["POS_HOLD", "AUTO_WAYPOINT", "RETURN_TO_HOME"]:
            err_x = self.target_x - drone.pos_x
            err_y = self.target_y - drone.pos_y

            cmd_vx = self.pid_pos_x.update(err_x, dt)
            cmd_vy = self.pid_pos_y.update(err_y, dt)

            err_vx = cmd_vx - drone.vel_x
            err_vy = cmd_vy - drone.vel_y

            acc_des_x = self.pid_vel_x.update(err_vx, dt)
            acc_des_y = self.pid_vel_y.update(err_vy, dt)

            # Map Earth horizontal accelerations to desired Euler roll/pitch
            cy = math.cos(drone.yaw)
            sy = math.sin(drone.yaw)
            # Desired pitch tilts forward/back along body heading
            desired_pitch = acc_des_x * cy + acc_des_y * sy
            # Desired roll tilts left/right along body lateral
            desired_roll = acc_des_x * sy - acc_des_y * cy
        else:
            desired_roll = 0.0
            desired_pitch = 0.0

        # 2. Altitude Loop
        if self.flight_mode in ["ALT_HOLD", "POS_HOLD", "AUTO_WAYPOINT", "RETURN_TO_HOME"]:
            err_z = self.target_z - drone.pos_z
            cmd_vz = self.pid_alt_pos.update(err_z, dt)
            err_vz = cmd_vz - drone.vel_z
            thrust_adjustment = self.pid_alt_vel.update(err_vz, dt)
        else:
            thrust_adjustment = 0.0

        # Baseline hover thrust counteracts gravity
        # Projected along tilted body Z axis: T = (m * g + thrust_adj) / (cos(roll) * cos(pitch))
        tilt_factor = max(0.7, math.cos(drone.roll) * math.cos(drone.pitch))
        total_thrust_cmd = ((drone.mass * GRAVITY) + thrust_adjustment) / tilt_factor

        # 3. Attitude Loop (Angle -> Desired Angular Rates)
        err_roll = desired_roll - drone.roll
        err_pitch = desired_pitch - drone.pitch
        
        # Shortest angular distance for yaw
        err_yaw = (self.target_yaw - drone.yaw + math.pi) % (2.0 * math.pi) - math.pi

        des_rate_p = self.pid_roll_angle.update(err_roll, dt)
        des_rate_q = self.pid_pitch_angle.update(err_pitch, dt)
        des_rate_r = self.pid_yaw_angle.update(err_yaw, dt)

        # 4. Angular Rate Loop (Rates -> Control Torques)
        err_p = des_rate_p - drone.rate_p
        err_q = des_rate_q - drone.rate_q
        err_r = des_rate_r - drone.rate_r

        torque_cmd_roll = self.pid_roll_rate.update(err_p, dt)
        torque_cmd_pitch = self.pid_pitch_rate.update(err_q, dt)
        torque_cmd_yaw = self.pid_yaw_rate.update(err_r, dt)

        # 5. Quad-X Motor Mixer
        # Motor 1 (Front-Right, CCW): +Thrust -Roll -Pitch -Yaw
        # Motor 2 (Front-Left, CW):   +Thrust +Roll -Pitch +Yaw
        # Motor 3 (Rear-Left, CCW):   +Thrust +Roll +Pitch -Yaw
        # Motor 4 (Rear-Right, CW):   +Thrust -Roll +Pitch +Yaw
        base_thrust_per_motor = max(0.0, total_thrust_cmd / 4.0)

        # Torque scaling factor to thrust differences
        d = drone.arm_length * (math.sqrt(2.0) / 2.0)
        roll_force = torque_cmd_roll / (4.0 * d)
        pitch_force = torque_cmd_pitch / (4.0 * d)
        yaw_force = torque_cmd_yaw / (4.0 * (drone.kq / drone.kt))

        t1 = base_thrust_per_motor - roll_force - pitch_force - yaw_force
        t2 = base_thrust_per_motor + roll_force - pitch_force + yaw_force
        t3 = base_thrust_per_motor + roll_force + pitch_force - yaw_force
        t4 = base_thrust_per_motor - roll_force + pitch_force + yaw_force

        motor_thrusts = [max(0.0, t) for t in [t1, t2, t3, t4]]

        # Convert thrust to motor RPM: RPM = sqrt(T / kt) * (60 / 2pi)
        motor_rpms = []
        for t in motor_thrusts:
            omega = math.sqrt(t / drone.kt)
            rpm = omega * (60.0 / (2.0 * math.pi))
            motor_rpms.append(max(0.0, min(10500.0, rpm)))

        return motor_rpms

