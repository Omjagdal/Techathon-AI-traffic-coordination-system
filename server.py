"""
AI-Powered Smart Traffic Management — FastAPI WebSocket Server
==============================================================
Headless simulation engine broadcasting real-time state to the React dashboard.
"""

import asyncio
import json
import math
import random
import time
import threading
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION (ported from ai_config.py)
# ─────────────────────────────────────────────────────────────────────────────

NO_OF_SIGNALS = 4
DIRECTION_NUMBERS = {0: "right", 1: "down", 2: "left", 3: "up"}
DIRECTION_INDICES = {"right": 0, "down": 1, "left": 2, "up": 3}

DEFAULT_RED = 150
DEFAULT_YELLOW = 5
DEFAULT_GREEN = 20
DEFAULT_MIN = 10
DEFAULT_MAX = 60

SPEEDS = {"car": 2.25, "bus": 1.8, "truck": 1.8, "rickshaw": 2, "bike": 2.5, "ambulance": 3.0}
VEHICLE_TIMES = {"car": 2, "bus": 2.5, "truck": 2.5, "rickshaw": 2.25, "bike": 1, "ambulance": 1.5}

AI_WEIGHTS = {"vehicle_count": 0.4, "wait_time": 0.3, "queue_length": 0.2, "throughput": 0.1, "pollution": 0.15}
EMISSION_RATES = {"car": 2.3, "bus": 5.0, "truck": 6.0, "rickshaw": 1.0, "bike": 0.5, "ambulance": 4.0}
POLLUTION_THRESHOLD = 50.0

# Layout — normalized to a 1400×800 canvas
STOP_LINES = {"right": 590, "down": 330, "left": 800, "up": 535}
DEFAULT_STOPS = {"right": 580, "down": 320, "left": 810, "up": 545}

SPAWN_X = {
    "right": [0, 0, 0],
    "down": [755, 727, 697],
    "left": [1400, 1400, 1400],
    "up": [602, 627, 657],
}
SPAWN_Y = {
    "right": [348, 370, 398],
    "down": [0, 0, 0],
    "left": [498, 466, 436],
    "up": [800, 800, 800],
}

VEHICLE_SIZES = {
    "car": (45, 20),
    "bus": (70, 22),
    "truck": (65, 22),
    "rickshaw": (40, 18),
    "bike": (35, 14),
    "ambulance": (70, 22),
}

GAP = 18
GAP2 = 18
MIN_SAFE_GAP = 8

EMERGENCY_GREEN = 8
EMERGENCY_TIMEOUT = 12

# ─────────────────────────────────────────────────────────────────────────────
# TRAFFIC SIGNAL
# ─────────────────────────────────────────────────────────────────────────────

class TrafficSignal:
    def __init__(self, red: int, yellow: int, green: int):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.totalGreenTime = 0
        self.vehiclesPassedThisCycle = 0

    def state(self) -> str:
        if self.green > 0 and self.yellow == 0 and self.red == 0:
            return "green"
        if self.yellow > 0:
            return "yellow"
        return "red"

    def timer(self) -> int:
        if self.green > 0 and self.red == 0:
            return self.green
        if self.yellow > 0:
            return self.yellow
        return self.red

    def to_dict(self):
        return {
            "green": self.green,
            "yellow": self.yellow,
            "red": self.red,
            "state": self.state(),
            "timer": self.timer(),
        }


# ─────────────────────────────────────────────────────────────────────────────
# VEHICLE
# ─────────────────────────────────────────────────────────────────────────────

_vehicle_id_counter = 0

class Vehicle:
    def __init__(self, lane: int, vehicle_class: str, direction_number: int, direction: str, will_turn: bool):
        global _vehicle_id_counter
        _vehicle_id_counter += 1
        self.id = _vehicle_id_counter
        self.lane = lane
        self.vehicleClass = vehicle_class
        self.speed = SPEEDS[vehicle_class]
        self.direction_number = direction_number
        self.direction = direction
        self.x = float(SPAWN_X[direction][lane])
        self.y = float(SPAWN_Y[direction][lane])
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.isEmergency = (vehicle_class == "ambulance")
        self.waitingTicks = 0
        self.w, self.h = VEHICLE_SIZES.get(vehicle_class, (45, 20))

        # Swap w/h for vertical directions
        if direction in ("down", "up"):
            self.w, self.h = self.h, self.w

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.vehicleClass,
            "dir": self.direction,
            "lane": self.lane,
            "x": round(self.x, 1),
            "y": round(self.y, 1),
            "w": self.w,
            "h": self.h,
            "crossed": self.crossed == 1,
            "isEmergency": self.isEmergency,
            "willTurn": self.willTurn,
            "turned": self.turned == 1,
        }


# ─────────────────────────────────────────────────────────────────────────────
# SIMULATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

class SimulationEngine:
    def __init__(self):
        self.signals: List[TrafficSignal] = []
        self.vehicles: Dict[str, Dict] = {
            d: {0: [], 1: [], 2: [], "crossed": 0} for d in ("right", "down", "left", "up")
        }
        self.stops: Dict[str, List[float]] = {
            d: [DEFAULT_STOPS[d]] * 3 for d in ("right", "down", "left", "up")
        }
        self.spawn_x = {d: list(SPAWN_X[d]) for d in SPAWN_X}
        self.spawn_y = {d: list(SPAWN_Y[d]) for d in SPAWN_Y}

        self.currentGreen = 0
        self.nextGreen = 1
        self.currentYellow = 0
        self.timeElapsed = 0
        self.running = False
        self.tick_rate = 0.033  # ~30 fps (matches pygame vehicle speeds)

        # AI state
        self.aiMode = "NORMAL"
        self.aiData = {
            d: {"waitTime": 0, "queueLength": 0, "throughputHistory": [], "aiScore": 0}
            for d in ("right", "down", "left", "up")
        }
        self.pollutionLevel = {d: 0.0 for d in ("right", "down", "left", "up")}
        self.totalAQI = 0.0

        # Emergency
        self.emergencyMode = False
        self.emergencyDirection = -1
        self.emergencyActive = False
        self.emergencyVehicle = None
        self.emergencyTimer = 0
        self.emergencyQueue: List[dict] = []
        self.emergencyServed = 0
        self._tick_counter = 0

        # Junction coordination
        self.junction2_synced = False
        self.junction2_score = 0.0
        self.junction2_offset = 4.17
        self.junction2_greenTimer = DEFAULT_GREEN

        # Event log for dashboard
        self.events: List[dict] = []
        self._max_events = 50

        # Spawn tracking
        self._spawn_timer = 0
        self._amb_timer = 0
        self._second_accumulator = 0.0

        self._initialize()

    # ── Initialization ────────────────────────────────────────────────────

    def _initialize(self):
        ts1 = TrafficSignal(0, DEFAULT_YELLOW, DEFAULT_GREEN)
        self.signals.append(ts1)
        ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, DEFAULT_YELLOW, DEFAULT_GREEN)
        self.signals.append(ts2)
        ts3 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, DEFAULT_GREEN)
        self.signals.append(ts3)
        ts4 = TrafficSignal(DEFAULT_RED, DEFAULT_YELLOW, DEFAULT_GREEN)
        self.signals.append(ts4)
        self.running = True
        self._add_event("system", "Simulation initialized")

    # ── Event logging ─────────────────────────────────────────────────────

    def _add_event(self, event_type: str, message: str):
        self.events.append({
            "type": event_type,
            "message": message,
            "time": self.timeElapsed,
        })
        if len(self.events) > self._max_events:
            self.events = self.events[-self._max_events:]

    # ── Vehicle spawning ──────────────────────────────────────────────────

    def _spawn_vehicle(self):
        self._amb_timer += 1
        spawn_amb = False
        if self._amb_timer >= random.randint(40, 80):
            spawn_amb = True
            self._amb_timer = 0

        if spawn_amb:
            vtype = "ambulance"
            lane = random.randint(1, 2)
            turn = False
            dirnum = random.randint(0, 3)
        else:
            vtypes = ["car", "bus", "truck", "rickshaw", "bike"]
            vtype = random.choice(vtypes)
            lane = 0 if vtype == "bike" else random.randint(1, 2)
            turn = False
            if lane == 2:
                turn = random.randint(0, 4) <= 2
            tmp = random.randint(0, 999)
            if tmp < 400:
                dirnum = 0
            elif tmp < 800:
                dirnum = 1
            elif tmp < 900:
                dirnum = 2
            else:
                dirnum = 3

        direction = DIRECTION_NUMBERS[dirnum]
        veh = Vehicle(lane, vtype, dirnum, direction, turn)

        # Set stop position
        lane_vehicles = self.vehicles[direction][lane]
        if lane_vehicles and lane_vehicles[-1].crossed == 0:
            prev = lane_vehicles[-1]
            if direction == "right":
                veh.stop = prev.stop - prev.w - GAP
            elif direction == "left":
                veh.stop = prev.stop + prev.w + GAP
            elif direction == "down":
                veh.stop = prev.stop - prev.h - GAP
            elif direction == "up":
                veh.stop = prev.stop + prev.h + GAP
        else:
            veh.stop = DEFAULT_STOPS[direction]

        # Adjust spawn position to not overlap
        if direction == "right":
            if lane_vehicles and lane_vehicles[-1].crossed == 0:
                veh.x = min(veh.x, lane_vehicles[-1].x - veh.w - GAP)
            self.spawn_x[direction][lane] = veh.x - veh.w - GAP
        elif direction == "left":
            if lane_vehicles and lane_vehicles[-1].crossed == 0:
                veh.x = max(veh.x, lane_vehicles[-1].x + lane_vehicles[-1].w + GAP)
            self.spawn_x[direction][lane] = veh.x + veh.w + GAP
        elif direction == "down":
            if lane_vehicles and lane_vehicles[-1].crossed == 0:
                veh.y = min(veh.y, lane_vehicles[-1].y - veh.h - GAP)
            self.spawn_y[direction][lane] = veh.y - veh.h - GAP
        elif direction == "up":
            if lane_vehicles and lane_vehicles[-1].crossed == 0:
                veh.y = max(veh.y, lane_vehicles[-1].y + lane_vehicles[-1].h + GAP)
            self.spawn_y[direction][lane] = veh.y + veh.h + GAP

        lane_vehicles.append(veh)

        if vtype == "ambulance":
            self._add_event("emergency", f"🚑 Ambulance spawned → {direction.upper()}")

    def spawn_ambulance(self, dir_num: int):
        direction = DIRECTION_NUMBERS[dir_num]
        lane = random.randint(1, 2)
        veh = Vehicle(lane, "ambulance", dir_num, direction, False)
        lane_vehicles = self.vehicles[direction][lane]
        if lane_vehicles and lane_vehicles[-1].crossed == 0:
            prev = lane_vehicles[-1]
            if direction == "right":
                veh.stop = prev.stop - prev.w - GAP
                veh.x = min(veh.x, prev.x - veh.w - GAP)
            elif direction == "left":
                veh.stop = prev.stop + prev.w + GAP
                veh.x = max(veh.x, prev.x + prev.w + GAP)
            elif direction == "down":
                veh.stop = prev.stop - prev.h - GAP
                veh.y = min(veh.y, prev.y - veh.h - GAP)
            elif direction == "up":
                veh.stop = prev.stop + prev.h + GAP
                veh.y = max(veh.y, prev.y + prev.h + GAP)
        else:
            veh.stop = DEFAULT_STOPS[direction]
        lane_vehicles.append(veh)
        self._add_event("emergency", f"🚑 Manual ambulance → {direction.upper()}")

    # ── Movement logic ────────────────────────────────────────────────────

    def _move_vehicles(self):
        for dir_name in ("right", "down", "left", "up"):
            for lane in range(3):
                for idx, veh in enumerate(self.vehicles[dir_name][lane]):
                    self._move_vehicle(veh, idx, dir_name, lane)

        # Resolve any overlaps that still occurred
        self._resolve_overlaps()

        # Remove off-screen vehicles
        for dir_name in ("right", "down", "left", "up"):
            for lane in range(3):
                self.vehicles[dir_name][lane] = [
                    v for v in self.vehicles[dir_name][lane]
                    if not self._is_offscreen(v)
                ]

    def _is_offscreen(self, veh: Vehicle) -> bool:
        return (
            veh.x > 1500 or veh.x < -100 or
            veh.y > 900 or veh.y < -100
        )

    def _move_vehicle(self, veh: Vehicle, idx: int, dir_name: str, lane: int):
        lane_vehicles = self.vehicles[dir_name][lane]

        if dir_name == "right":
            self._move_right(veh, idx, lane_vehicles)
        elif dir_name == "down":
            self._move_down(veh, idx, lane_vehicles)
        elif dir_name == "left":
            self._move_left(veh, idx, lane_vehicles)
        elif dir_name == "up":
            self._move_up(veh, idx, lane_vehicles)

    def _has_gap(self, veh: Vehicle, idx: int, lane_vehicles: list, direction: str) -> bool:
        """Check if there's space ahead for ambulance bypass (no overlap)."""
        if idx == 0:
            return True
        prev = lane_vehicles[idx - 1]
        if prev.turned:
            return True
        if direction == "right":
            return veh.x + veh.w + GAP2 < prev.x
        elif direction == "left":
            return veh.x - GAP2 > prev.x + prev.w
        elif direction == "down":
            return veh.y + veh.h + GAP2 < prev.y
        elif direction == "up":
            return veh.y - GAP2 > prev.y + prev.h
        return True

    def _can_move(self, veh: Vehicle, idx: int, lane_vehicles: list, direction: str) -> bool:
        """Check if vehicle can move (not blocked by ANY vehicle ahead)."""
        if idx == 0:
            return True
        # Check all vehicles ahead (indices 0..idx-1), not just immediate predecessor
        for i in range(idx):
            ahead = lane_vehicles[i]
            if ahead.turned:
                continue
            if direction == "right":
                if veh.x + veh.w + MIN_SAFE_GAP >= ahead.x:
                    return False
            elif direction == "left":
                if veh.x - MIN_SAFE_GAP <= ahead.x + ahead.w:
                    return False
            elif direction == "down":
                if veh.y + veh.h + MIN_SAFE_GAP >= ahead.y:
                    return False
            elif direction == "up":
                if veh.y - MIN_SAFE_GAP <= ahead.y + ahead.h:
                    return False
        return True

    def _resolve_overlaps(self):
        """Post-movement pass: forcibly separate overlapping vehicles in each lane."""
        for dir_name in ("right", "down", "left", "up"):
            for lane in range(3):
                lane_vehicles = self.vehicles[dir_name][lane]
                if len(lane_vehicles) < 2:
                    continue
                for i in range(1, len(lane_vehicles)):
                    prev = lane_vehicles[i - 1]
                    curr = lane_vehicles[i]
                    if prev.turned or curr.turned:
                        continue
                    if dir_name == "right":
                        min_x = prev.x - curr.w - GAP2
                        if curr.x > min_x:
                            curr.x = min_x
                    elif dir_name == "left":
                        min_x = prev.x + prev.w + GAP2
                        if curr.x < min_x:
                            curr.x = min_x
                    elif dir_name == "down":
                        min_y = prev.y - curr.h - GAP2
                        if curr.y > min_y:
                            curr.y = min_y
                    elif dir_name == "up":
                        min_y = prev.y + prev.h + GAP2
                        if curr.y < min_y:
                            curr.y = min_y

    def _move_right(self, veh: Vehicle, idx: int, lane_vehicles: list):
        if veh.crossed == 0 and veh.x + veh.w > STOP_LINES["right"]:
            veh.crossed = 1
            self.vehicles["right"]["crossed"] += 1
            self.signals[self.currentGreen].vehiclesPassedThisCycle += 1
            if veh.isEmergency:
                self._clear_emergency()
            return

        # Ambulance bypass: skip stop-line but respect gap with vehicles ahead
        if veh.isEmergency and veh.crossed == 0 and self.emergencyMode and self.emergencyDirection == veh.direction_number:
            if self._has_gap(veh, idx, lane_vehicles, "right"):
                veh.x += veh.speed
            return

        is_green = (self.currentGreen == 0 and self.currentYellow == 0)
        at_stop = veh.x + veh.w <= getattr(veh, "stop", DEFAULT_STOPS["right"])
        can_go = at_stop or veh.crossed == 1 or is_green

        if can_go and self._can_move(veh, idx, lane_vehicles, "right"):
            veh.x += veh.speed
        elif veh.crossed == 0:
            veh.waitingTicks += 1

    def _move_down(self, veh: Vehicle, idx: int, lane_vehicles: list):
        if veh.crossed == 0 and veh.y + veh.h > STOP_LINES["down"]:
            veh.crossed = 1
            self.vehicles["down"]["crossed"] += 1
            self.signals[self.currentGreen].vehiclesPassedThisCycle += 1
            if veh.isEmergency:
                self._clear_emergency()
            return

        # Ambulance bypass: skip stop-line but respect gap with vehicles ahead
        if veh.isEmergency and veh.crossed == 0 and self.emergencyMode and self.emergencyDirection == veh.direction_number:
            if self._has_gap(veh, idx, lane_vehicles, "down"):
                veh.y += veh.speed
            return

        is_green = (self.currentGreen == 1 and self.currentYellow == 0)
        at_stop = veh.y + veh.h <= getattr(veh, "stop", DEFAULT_STOPS["down"])
        can_go = at_stop or veh.crossed == 1 or is_green

        if can_go and self._can_move(veh, idx, lane_vehicles, "down"):
            veh.y += veh.speed
        elif veh.crossed == 0:
            veh.waitingTicks += 1

    def _move_left(self, veh: Vehicle, idx: int, lane_vehicles: list):
        if veh.crossed == 0 and veh.x < STOP_LINES["left"]:
            veh.crossed = 1
            self.vehicles["left"]["crossed"] += 1
            self.signals[self.currentGreen].vehiclesPassedThisCycle += 1
            if veh.isEmergency:
                self._clear_emergency()
            return

        # Ambulance bypass: skip stop-line but respect gap with vehicles ahead
        if veh.isEmergency and veh.crossed == 0 and self.emergencyMode and self.emergencyDirection == veh.direction_number:
            if self._has_gap(veh, idx, lane_vehicles, "left"):
                veh.x -= veh.speed
            return

        is_green = (self.currentGreen == 2 and self.currentYellow == 0)
        at_stop = veh.x >= getattr(veh, "stop", DEFAULT_STOPS["left"])
        can_go = at_stop or veh.crossed == 1 or is_green

        if can_go and self._can_move(veh, idx, lane_vehicles, "left"):
            veh.x -= veh.speed
        elif veh.crossed == 0:
            veh.waitingTicks += 1

    def _move_up(self, veh: Vehicle, idx: int, lane_vehicles: list):
        if veh.crossed == 0 and veh.y < STOP_LINES["up"]:
            veh.crossed = 1
            self.vehicles["up"]["crossed"] += 1
            self.signals[self.currentGreen].vehiclesPassedThisCycle += 1
            if veh.isEmergency:
                self._clear_emergency()
            return

        # Ambulance bypass: skip stop-line but respect gap with vehicles ahead
        if veh.isEmergency and veh.crossed == 0 and self.emergencyMode and self.emergencyDirection == veh.direction_number:
            if self._has_gap(veh, idx, lane_vehicles, "up"):
                veh.y -= veh.speed
            return

        is_green = (self.currentGreen == 3 and self.currentYellow == 0)
        at_stop = veh.y >= getattr(veh, "stop", DEFAULT_STOPS["up"])
        can_go = at_stop or veh.crossed == 1 or is_green

        if can_go and self._can_move(veh, idx, lane_vehicles, "up"):
            veh.y -= veh.speed
        elif veh.crossed == 0:
            veh.waitingTicks += 1

    # ── AI: Adaptive signal timing ────────────────────────────────────────

    def _adaptive_set_time(self):
        if self.emergencyMode:
            return

        dir_name = DIRECTION_NUMBERS[self.nextGreen]
        counts = {t: 0 for t in SPEEDS}
        total_wait = 0
        queue_count = 0

        for lane in range(3):
            for veh in self.vehicles[dir_name][lane]:
                if veh.crossed == 0:
                    counts[veh.vehicleClass] += 1
                    total_wait += veh.waitingTicks
                    queue_count += 1

        base_green = math.ceil(
            sum(counts[t] * VEHICLE_TIMES[t] for t in counts) / 3
        )

        vehicle_count = sum(counts.values())
        avg_wait = (total_wait / max(1, queue_count)) / 60.0
        hist = self.aiData[dir_name]["throughputHistory"]
        recent_tp = sum(hist[-5:]) / max(1, len(hist[-5:])) if hist else 0
        pollution_bonus = max(0, (self.pollutionLevel[dir_name] - POLLUTION_THRESHOLD) * AI_WEIGHTS["pollution"])

        ai_score = (
            AI_WEIGHTS["vehicle_count"] * vehicle_count
            + AI_WEIGHTS["wait_time"] * avg_wait
            + AI_WEIGHTS["queue_length"] * queue_count
            - AI_WEIGHTS["throughput"] * recent_tp
            + pollution_bonus
        )

        green_time = math.ceil(base_green + ai_score * 0.8)
        green_time = max(DEFAULT_MIN, min(DEFAULT_MAX, green_time))

        if self.junction2_synced:
            green_time = min(green_time + 3, DEFAULT_MAX)

        self.aiData[dir_name]["aiScore"] = round(ai_score, 1)
        self.aiData[dir_name]["waitTime"] = round(avg_wait, 1)
        self.aiData[dir_name]["queueLength"] = queue_count

        self.signals[(self.currentGreen + 1) % NO_OF_SIGNALS].green = green_time

        self._add_event("ai", f"🧠 AI Green [{dir_name}]: {green_time}s (score={ai_score:.1f})")

    def _record_throughput(self, dir_name: str, passed: int):
        hist = self.aiData[dir_name]["throughputHistory"]
        hist.append(passed)
        if len(hist) > 20:
            self.aiData[dir_name]["throughputHistory"] = hist[-20:]

    # ── AI: Pollution ─────────────────────────────────────────────────────

    def _update_pollution(self):
        for dir_num in range(NO_OF_SIGNALS):
            dir_name = DIRECTION_NUMBERS[dir_num]
            if dir_num != self.currentGreen:
                for lane in range(3):
                    for veh in self.vehicles[dir_name][lane]:
                        if veh.crossed == 0:
                            rate = EMISSION_RATES.get(veh.vehicleClass, 1.0)
                            self.pollutionLevel[dir_name] += rate * 0.05
            self.pollutionLevel[dir_name] = max(0.0, self.pollutionLevel[dir_name] - 0.3)

        self.totalAQI = sum(self.pollutionLevel.values()) / 4.0

        if not self.emergencyMode:
            if any(p > POLLUTION_THRESHOLD * 1.5 for p in self.pollutionLevel.values()):
                self.aiMode = "POLLUTION_ALERT"
            elif self.aiMode == "POLLUTION_ALERT":
                self.aiMode = "NORMAL"

    # ── AI: Emergency corridor ────────────────────────────────────────────

    def _check_for_emergency(self):
        self._tick_counter += 1
        queued_ids = {id(e["vehicle"]) for e in self.emergencyQueue}

        for dir_num in range(NO_OF_SIGNALS):
            dir_name = DIRECTION_NUMBERS[dir_num]
            for lane in range(3):
                for veh in self.vehicles[dir_name][lane]:
                    if veh.isEmergency and veh.crossed == 0 and id(veh) not in queued_ids:
                        score = self._score_ambulance(veh, dir_num)
                        self.emergencyQueue.append({
                            "dir": dir_num,
                            "vehicle": veh,
                            "arrivalTick": self._tick_counter,
                            "score": score,
                        })
                        queued_ids.add(id(veh))
                        self._add_event("emergency", f"🚑 Queued: {dir_name.upper()} (score={score})")

        self.emergencyQueue = [e for e in self.emergencyQueue if e["vehicle"].crossed == 0]
        self.emergencyQueue.sort(key=lambda e: e["score"], reverse=True)

        if self.emergencyQueue and not self.emergencyMode:
            self._activate_next_in_queue()

    def _score_ambulance(self, veh: Vehicle, dir_num: int) -> float:
        """
        Score ambulance priority based on:
          1. Distance to signal (closer = higher priority)  — 50 pts max
          2. Traffic density (more vehicles = more urgency) — 25 pts max
          3. Waiting time (longer wait = higher priority)   — 25 pts max
        """
        dir_name = DIRECTION_NUMBERS[dir_num]
        score = 0.0

        # 1. Distance to signal stop line (closer → higher score)
        stop_line = STOP_LINES[dir_name]
        if dir_name == "right":
            distance = max(0, stop_line - veh.x)
            max_distance = stop_line  # max possible distance
        elif dir_name == "down":
            distance = max(0, stop_line - veh.y)
            max_distance = stop_line
        elif dir_name == "left":
            distance = max(0, veh.x - stop_line)
            max_distance = 1400 - stop_line
        else:  # up
            distance = max(0, veh.y - stop_line)
            max_distance = 800 - stop_line

        # Invert: closer = higher score (50 pts max)
        proximity = 1.0 - min(distance / max(1, max_distance), 1.0)
        score += proximity * 50.0

        # 2. Traffic density in this direction (more vehicles = harder to clear)
        total_waiting = 0
        for lane in range(3):
            for v in self.vehicles[dir_name][lane]:
                if v.crossed == 0:
                    total_waiting += 1
        # More vehicles waiting → ambulance needs help sooner (25 pts max)
        density_score = min(total_waiting / 15.0, 1.0) * 25.0
        score += density_score

        # 3. Waiting time (25 pts max)
        wait_score = min(veh.waitingTicks / 100.0, 1.0) * 25.0
        score += wait_score

        return round(score, 1)

    def _activate_next_in_queue(self):
        if not self.emergencyQueue:
            self._clear_all_emergency()
            return
        entry = self.emergencyQueue[0]
        self.emergencyMode = True
        self.emergencyDirection = entry["dir"]
        self.emergencyVehicle = entry["vehicle"]
        self.emergencyActive = True
        self.emergencyTimer = 0
        self.aiMode = "EMERGENCY"
        self._activate_green_corridor()

    def _activate_green_corridor(self):
        green_t = EMERGENCY_GREEN if len(self.emergencyQueue) > 1 else DEFAULT_MAX
        for i in range(NO_OF_SIGNALS):
            if i == self.emergencyDirection:
                self.signals[i].green = green_t
                self.signals[i].yellow = 0
                self.signals[i].red = 0
            else:
                self.signals[i].red = green_t + DEFAULT_YELLOW
                self.signals[i].green = 0
                self.signals[i].yellow = 0
        self.currentGreen = self.emergencyDirection
        self.currentYellow = 0
        dir_name = DIRECTION_NUMBERS[self.emergencyDirection]
        self._add_event("emergency", f"🟢 GREEN CORRIDOR → {dir_name.upper()} ({green_t}s)")

    def _clear_emergency(self):
        if not self.emergencyMode:
            return
        self.emergencyServed += 1
        self.emergencyQueue = [e for e in self.emergencyQueue if e["vehicle"].crossed == 0]
        self.emergencyMode = False
        self.emergencyDirection = -1
        self.emergencyActive = False
        self.emergencyVehicle = None
        self.emergencyTimer = 0
        if self.emergencyQueue:
            self._activate_next_in_queue()
        else:
            self.aiMode = "NORMAL"
            self.emergencyServed = 0
            self._add_event("system", "✅ All ambulances served — resuming normal")

    def _clear_all_emergency(self):
        self.emergencyMode = False
        self.emergencyDirection = -1
        self.emergencyActive = False
        self.emergencyVehicle = None
        self.emergencyTimer = 0
        self.emergencyQueue = []
        self.emergencyServed = 0
        self.aiMode = "NORMAL"

    def _tick_emergency(self):
        if not self.emergencyMode:
            return
        self.emergencyTimer += 1
        if self.emergencyTimer >= EMERGENCY_TIMEOUT:
            self.emergencyQueue = [
                e for e in self.emergencyQueue
                if id(e["vehicle"]) != id(self.emergencyVehicle)
            ]
            self.emergencyMode = False
            self.emergencyActive = False
            self.emergencyVehicle = None
            self.emergencyTimer = 0
            if self.emergencyQueue:
                self._activate_next_in_queue()
            else:
                self._clear_all_emergency()

    # ── AI: Junction coordination ─────────────────────────────────────────

    def _update_junction(self):
        if self.signals[self.currentGreen].green > 0:
            time_diff = abs(self.junction2_greenTimer - self.junction2_offset) % DEFAULT_GREEN
            self.junction2_score = max(0.0, 100.0 - time_diff * 10)
            self.junction2_synced = self.junction2_score > 60
            self.junction2_greenTimer = max(1, self.signals[self.currentGreen].green - int(self.junction2_offset))

    # ── Signal cycling ────────────────────────────────────────────────────

    def _update_signals(self):
        """Called every second to advance signal timers."""
        if self.emergencyMode and self.emergencyActive:
            # During emergency, just tick down the green
            if self.signals[self.currentGreen].green > 0:
                self.signals[self.currentGreen].green -= 1
                self.signals[self.currentGreen].totalGreenTime += 1
            else:
                # Emergency green expired — tick emergency timeout
                self._tick_emergency()
            # Tick red on other signals
            for i in range(NO_OF_SIGNALS):
                if i != self.currentGreen and self.signals[i].red > 0:
                    self.signals[i].red -= 1
            return

        # ── Normal signal cycling
        for i in range(NO_OF_SIGNALS):
            if i == self.currentGreen:
                if self.currentYellow == 0:
                    if self.signals[i].green > 0:
                        self.signals[i].green -= 1
                        self.signals[i].totalGreenTime += 1
                    else:
                        # Green exhausted → start yellow
                        self.currentYellow = 1
                        self.signals[i].yellow = DEFAULT_YELLOW

                        # Record throughput
                        dir_name = DIRECTION_NUMBERS[self.currentGreen]
                        self._record_throughput(dir_name, self.signals[i].vehiclesPassedThisCycle)
                        self.signals[i].vehiclesPassedThisCycle = 0

                        # Reset stops
                        for ln in range(3):
                            self.stops[dir_name][ln] = DEFAULT_STOPS[dir_name]
                else:
                    if self.signals[i].yellow > 0:
                        self.signals[i].yellow -= 1
                    else:
                        # Yellow exhausted → advance to next
                        self.currentYellow = 0
                        self.signals[i].green = DEFAULT_GREEN
                        self.signals[i].yellow = DEFAULT_YELLOW
                        self.signals[i].red = DEFAULT_RED

                        self.currentGreen = self.nextGreen
                        self.nextGreen = (self.currentGreen + 1) % NO_OF_SIGNALS
                        self.signals[self.nextGreen].red = DEFAULT_YELLOW + DEFAULT_GREEN

                        self._add_event("signal", f"🔄 Signal → {DIRECTION_NUMBERS[self.currentGreen].upper()}")
            else:
                if self.signals[i].red > 0:
                    self.signals[i].red -= 1

        # Trigger adaptive timing earlier for faster response
        next_sig = self.signals[(self.currentGreen + 1) % NO_OF_SIGNALS]
        if next_sig.red in (8, 4):
            self._adaptive_set_time()

    # ── Main tick ─────────────────────────────────────────────────────────

    def tick(self):
        if not self.running:
            return

        # Move vehicles every tick (10fps)
        self._move_vehicles()

        # Check for emergencies every tick
        self._check_for_emergency()

        # Accumulate for per-second actions
        self._second_accumulator += self.tick_rate

        # Every ~1.0s spawn a vehicle (less congestion = faster flow)
        self._spawn_timer += self.tick_rate
        if self._spawn_timer >= 1.0:
            self._spawn_timer = 0
            try:
                self._spawn_vehicle()
            except Exception:
                pass

        # Every 1s: update signals, pollution, junction, time
        if self._second_accumulator >= 1.0:
            self._second_accumulator -= 1.0
            self._update_signals()
            self._update_pollution()
            self._update_junction()
            self.timeElapsed += 1

    # ── State snapshot ────────────────────────────────────────────────────

    def get_state(self) -> dict:
        all_vehicles = []
        for dir_name in ("right", "down", "left", "up"):
            for lane in range(3):
                for veh in self.vehicles[dir_name][lane]:
                    all_vehicles.append(veh.to_dict())

        waiting = {}
        for dir_name in ("right", "down", "left", "up"):
            w = sum(
                1 for lane in range(3) for v in self.vehicles[dir_name][lane] if v.crossed == 0
            )
            waiting[dir_name] = w

        total_crossed = sum(self.vehicles[d]["crossed"] for d in ("right", "down", "left", "up"))
        throughput = total_crossed / max(1, self.timeElapsed)

        return {
            "signals": [s.to_dict() for s in self.signals],
            "currentGreen": self.currentGreen,
            "currentYellow": self.currentYellow,
            "vehicles": all_vehicles,
            "ai": {
                "mode": self.aiMode,
                "aqi": round(self.totalAQI, 1),
                "scores": {d: self.aiData[d]["aiScore"] for d in self.aiData},
                "waitTimes": {d: self.aiData[d]["waitTime"] for d in self.aiData},
                "queueLengths": {d: self.aiData[d]["queueLength"] for d in self.aiData},
                "pollution": {d: round(self.pollutionLevel[d], 1) for d in self.pollutionLevel},
            },
            "emergency": {
                "active": self.emergencyMode,
                "direction": DIRECTION_NUMBERS.get(self.emergencyDirection, "none"),
                "queueLength": len(self.emergencyQueue),
                "served": self.emergencyServed,
            },
            "junction": {
                "synced": self.junction2_synced,
                "score": round(self.junction2_score, 1),
            },
            "time": self.timeElapsed,
            "crossed": {d: self.vehicles[d]["crossed"] for d in ("right", "down", "left", "up")},
            "totalCrossed": total_crossed,
            "throughput": round(throughput, 2),
            "waiting": waiting,
            "events": self.events[-10:],
        }

    def reset(self):
        global _vehicle_id_counter
        _vehicle_id_counter = 0
        self.__init__()


# ─────────────────────────────────────────────────────────────────────────────
# FASTAPI APPLICATION
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(title="AI Traffic Simulation Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = SimulationEngine()

# Background simulation loop
def run_simulation():
    while True:
        engine.tick()
        time.sleep(engine.tick_rate)

sim_thread = threading.Thread(target=run_simulation, daemon=True)
sim_thread.start()

# WebSocket connections
connected_clients: List[WebSocket] = []

class SpawnRequest(BaseModel):
    direction: int  # 0=right, 1=down, 2=left, 3=up

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True:
            state = engine.get_state()
            await ws.send_json(state)
            await asyncio.sleep(0.033)  # ~30 fps
    except WebSocketDisconnect:
        connected_clients.remove(ws)
    except Exception:
        if ws in connected_clients:
            connected_clients.remove(ws)

@app.post("/api/spawn-ambulance")
async def spawn_ambulance(req: SpawnRequest):
    if 0 <= req.direction <= 3:
        engine.spawn_ambulance(req.direction)
        return {"status": "ok", "direction": DIRECTION_NUMBERS[req.direction]}
    return {"status": "error", "message": "Invalid direction (0-3)"}

@app.post("/api/reset")
async def reset_simulation():
    engine.reset()
    return {"status": "ok"}

@app.get("/api/health")
async def health():
    return {"status": "ok", "time": engine.timeElapsed}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
