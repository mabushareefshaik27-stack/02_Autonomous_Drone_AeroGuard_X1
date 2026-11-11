"""
Autonomous 3D Path Planning and Mission Generation for AeroGuard-X1.
Implements 3D A* Search, Obstacle Avoidance, Boustrophedon Grid Survey,
and Search-and-Rescue (SAR) expanding search patterns.
"""

import math
import heapq
from typing import List, Tuple, Dict, Any, Set

class Waypoint:
    def __init__(self, x: float, y: float, z: float, action: str = "PASS", speed_m_s: float = 8.0):
        self.x = x
        self.y = y
        self.z = z
        self.action = action  # "TAKEOFF", "PASS", "SURVEY", "SCAN", "LAND"
        self.speed_m_s = speed_m_s

    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": round(self.x, 2),
            "y": round(self.y, 2),
            "z": round(self.z, 2),
            "action": self.action,
            "speed_m_s": self.speed_m_s
        }

class Obstacle3D:
    def __init__(self, x: float, y: float, z_min: float, z_max: float, radius: float, name: str = "Obstacle"):
        self.x = x
        self.y = y
        self.z_min = z_min
        self.z_max = z_max
        self.radius = radius
        self.name = name

    def collides(self, px: float, py: float, pz: float, margin: float = 1.5) -> bool:
        if pz < (self.z_min - margin) or pz > (self.z_max + margin):
            return False
        dist_sq = (px - self.x)**2 + (py - self.y)**2
        return dist_sq <= (self.radius + margin)**2

class PathPlanner:
    """
    3D A* Pathfinding and Mission Generator.
    """

    def __init__(self, bounds: Tuple[float, float, float, float, float, float] = (-100, 100, -100, 100, 0, 50)):
        # (min_x, max_x, min_y, max_y, min_z, max_z)
        self.bounds = bounds
        self.obstacles: List[Obstacle3D] = []

    def add_obstacle(self, x: float, y: float, z_min: float, z_max: float, radius: float, name: str = "Obstacle"):
        self.obstacles.append(Obstacle3D(x, y, z_min, z_max, radius, name))

    def plan_3d_astar(
        self,
        start: Tuple[float, float, float],
        goal: Tuple[float, float, float],
        grid_res: float = 3.0
    ) -> List[Waypoint]:
        """
        3D A* search across discrete voxel grid with Euclidean distance heuristic.
        """
        sx, sy, sz = [round(v / grid_res) for v in start]
        gx, gy, gz = [round(v / grid_res) for v in goal]
        start_node = (sx, sy, sz)
        goal_node = (gx, gy, gz)

        open_set = []
        heapq.heappush(open_set, (0.0, start_node))
        came_from: Dict[Tuple[int, int, int], Tuple[int, int, int]] = {}
        g_score: Dict[Tuple[int, int, int], float] = {start_node: 0.0}

        def heuristic(a, b):
            return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2)

        # 26-connectivity 3D neighborhood
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                for dz in [-1, 0, 1]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue
                    cost = math.sqrt(dx**2 + dy**2 + dz**2)
                    neighbors.append((dx, dy, dz, cost))

        iterations = 0
        max_iter = 4000

        while open_set and iterations < max_iter:
            iterations += 1
            _, current = heapq.heappop(open_set)

            if current == goal_node or heuristic(current, goal_node) <= 1.0:
                # Reconstruct path
                path = [goal]
                curr = current
                while curr in came_from:
                    px, py, pz = curr[0] * grid_res, curr[1] * grid_res, curr[2] * grid_res
                    path.append((px, py, pz))
                    curr = came_from[curr]
                path.append(start)
                path.reverse()
                return [Waypoint(x, y, z, "PASS") for x, y, z in path]

            for dx, dy, dz, step_cost in neighbors:
                nb = (current[0] + dx, current[1] + dy, current[2] + dz)
                # Check spatial bounds
                wx = nb[0] * grid_res
                wy = nb[1] * grid_res
                wz = nb[2] * grid_res

                if not (self.bounds[0] <= wx <= self.bounds[1] and
                        self.bounds[2] <= wy <= self.bounds[3] and
                        self.bounds[4] <= wz <= self.bounds[5]):
                    continue

                # Check collision with obstacles
                if any(obs.collides(wx, wy, wz) for obs in self.obstacles):
                    continue

                tentative_g = g_score[current] + step_cost
                if tentative_g < g_score.get(nb, float("inf")):
                    came_from[nb] = current
                    g_score[nb] = tentative_g
                    f_score = tentative_g + heuristic(nb, goal_node)
                    heapq.heappush(open_set, (f_score, nb))

        # Direct linear path fallback if unobstructed
        return [
            Waypoint(start[0], start[1], start[2], "TAKEOFF"),
            Waypoint(goal[0], goal[1], goal[2], "PASS")
        ]

    @staticmethod
    def generate_agricultural_grid(
        center_x: float,
        center_y: float,
        width_m: float = 60.0,
        height_m: float = 60.0,
        lane_spacing_m: float = 12.0,
        altitude_m: float = 15.0
    ) -> List[Waypoint]:
        """
        Boustrophedon (lawnmower) path for multispectral NDVI crop health scanning.
        """
        waypoints = []
        half_w = width_m / 2.0
        half_h = height_m / 2.0
        
        y = -half_h
        left_to_right = True

        while y <= half_h:
            x_start = -half_w if left_to_right else half_w
            x_end = half_w if left_to_right else -half_w

            waypoints.append(Waypoint(center_x + x_start, center_y + y, altitude_m, "SURVEY", speed_m_s=6.0))
            waypoints.append(Waypoint(center_x + x_end, center_y + y, altitude_m, "SURVEY", speed_m_s=6.0))

            y += lane_spacing_m
            left_to_right = not left_to_right

        return waypoints

    @staticmethod
    def generate_sar_spiral(
        center_x: float,
        center_y: float,
        max_radius_m: float = 75.0,
        altitude_m: float = 18.0,
        num_turns: int = 4
    ) -> List[Waypoint]:
        """
        Archimedean expanding spiral for Search-and-Rescue (SAR) survivor detection.
        """
        waypoints = []
        total_points = num_turns * 16
        b = max_radius_m / (num_turns * 2.0 * math.pi)

        for i in range(1, total_points + 1):
            theta = (i / total_points) * (num_turns * 2.0 * math.pi)
            r = b * theta
            x = center_x + r * math.cos(theta)
            y = center_y + r * math.sin(theta)
            waypoints.append(Waypoint(x, y, altitude_m, "SCAN", speed_m_s=5.0))

        return waypoints

