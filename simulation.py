# ==============================================================================
# AI-Powered Smart Traffic Management System — Main Simulation
# ==============================================================================
#
# AI modules (separate files):
#   ai_config.py                 – constants, weights, shared state
#   ai_green_corridor.py         – ambulance priority / emergency preemption
#   ai_adaptive_timing.py        – weighted multi-factor signal timing
#   ai_pollution.py              – CO₂ emission tracking & alerts
#   ai_junction_coordination.py  – multi-junction green-wave sync
#   ai_hud.py                    – real-time dashboard overlay
# ==============================================================================

import random
import math
import time
import threading
import pygame
import sys
import os

# ── AI modules ───────────────────────────────────────────────────────────────
import ai_config as cfg
import ai_green_corridor as corridor
import ai_adaptive_timing as adaptive
import ai_pollution as pollution
import ai_junction_coordination as junction
import ai_hud as hud
from image_loader import load_image

# ==============================================================================
# LAYOUT COORDINATES
# ==============================================================================

x = {'right': [0, 0, 0], 'down': [755, 727, 697],
     'left': [1400, 1400, 1400], 'up': [602, 627, 657]}
y = {'right': [348, 370, 398], 'down': [0, 0, 0],
     'left': [498, 466, 436], 'up': [800, 800, 800]}

vehicles = {
    'right': {0: [], 1: [], 2: [], 'crossed': 0},
    'down':  {0: [], 1: [], 2: [], 'crossed': 0},
    'left':  {0: [], 1: [], 2: [], 'crossed': 0},
    'up':    {0: [], 1: [], 2: [], 'crossed': 0},
}

signalCoods      = [(530, 230), (810, 230), (810, 570), (530, 570)]
signalTimerCoods = [(530, 210), (810, 210), (810, 550), (530, 550)]
vehicleCountCoods= [(480, 210), (880, 210), (880, 550), (480, 550)]
vehicleCountTexts= ["0", "0", "0", "0"]

stopLines   = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops       = {'right': [580, 580, 580], 'down': [320, 320, 320],
               'left':  [810, 810, 810], 'up':   [545, 545, 545]}

mid = {'right': {'x': 705, 'y': 445}, 'down': {'x': 695, 'y': 450},
       'left':  {'x': 695, 'y': 425}, 'up':   {'x': 695, 'y': 400}}
rotationAngle = 3

gap  = 15   # stopping gap
gap2 = 15   # moving gap

# ==============================================================================
# GLOBALS
# ==============================================================================

signals     = []
simTime     = 300
timeElapsed = 0

currentGreen  = 0
nextGreen     = (currentGreen + 1) % cfg.noOfSignals
currentYellow = 0

junction1 = None
junction2 = None

pygame.init()
simulation = pygame.sprite.Group()

# ==============================================================================
# TRAFFIC SIGNAL
# ==============================================================================

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red     = red
        self.yellow  = yellow
        self.green   = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0
        self.vehiclesPassedThisCycle = 0   # for adaptive throughput tracking

# ==============================================================================
# VEHICLE
# ==============================================================================

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane             = lane
        self.vehicleClass     = vehicleClass
        self.speed            = cfg.speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction        = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed      = 0
        self.willTurn     = will_turn
        self.turned       = 0
        self.rotateAngle  = 0
        self.isEmergency  = (vehicleClass == 'ambulance')
        self.waitingTicks = 0

        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1

        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = load_image(path)
        self.currentImage  = load_image(path)

        # ── set stop position depending on direction ─────────────────────
        if direction == 'right':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                prev = vehicles[direction][lane][self.index - 1]
                self.stop = prev.stop - prev.currentImage.get_rect().width - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp

        elif direction == 'left':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                prev = vehicles[direction][lane][self.index - 1]
                self.stop = prev.stop + prev.currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp

        elif direction == 'down':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                prev = vehicles[direction][lane][self.index - 1]
                self.stop = prev.stop - prev.currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp

        elif direction == 'up':
            if len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index - 1].crossed == 0:
                prev = vehicles[direction][lane][self.index - 1]
                self.stop = prev.stop + prev.currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp

        simulation.add(self)

    # ── rendering ────────────────────────────────────────────────────────
    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    # ── movement ─────────────────────────────────────────────────────────
    def move(self):
        if self.direction == 'right':
            self._move_right()
        elif self.direction == 'down':
            self._move_down()
        elif self.direction == 'left':
            self._move_left()
        elif self.direction == 'up':
            self._move_up()

    # ── direction helpers ────────────────────────────────────────────────
    def _has_gap_right(self):
        """Check if there's space ahead in this lane (right direction)."""
        if self.index == 0:
            return True
        prev = vehicles[self.direction][self.lane][self.index - 1]
        if prev.turned == 1:
            return True
        return self.x + self.currentImage.get_rect().width < prev.x - gap2

    def _move_right(self):
        w = self.currentImage.get_rect().width
        if self.crossed == 0 and self.x + w > stopLines[self.direction]:
            self.crossed = 1
            vehicles[self.direction]['crossed'] += 1
            if self.isEmergency:
                corridor.clear_emergency()
        # ── Ambulance bypass: skip stop-line but respect gap with vehicles ──
        if self.isEmergency and self.crossed == 0 and cfg.emergencyMode and cfg.emergencyDirection == self.direction_number:
            if self._has_gap_right():
                self.x += self.speed
            return
        if self.willTurn == 1:
            if self.crossed == 0 or self.x + w < mid[self.direction]['x']:
                if (self.x + w <= self.stop or (currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and \
                   (self.index == 0 or self.x + w < vehicles[self.direction][self.lane][self.index - 1].x - gap2 or
                    vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                    self.x += self.speed
                else:
                    self.waitingTicks += 1
            else:
                if self.turned == 0:
                    self.rotateAngle += rotationAngle
                    self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                    self.x += 2; self.y += 1.8
                    if self.rotateAngle == 90:
                        self.turned = 1
                else:
                    prev = vehicles[self.direction][self.lane][self.index - 1] if self.index > 0 else None
                    if prev is None or (self.y + self.currentImage.get_rect().height < prev.y - gap2) or \
                       (self.x + w < prev.x - gap2):
                        self.y += self.speed
        else:
            if (self.x + w <= self.stop or self.crossed == 1 or (currentGreen == 0 and currentYellow == 0)) and \
               (self.index == 0 or self.x + w < vehicles[self.direction][self.lane][self.index - 1].x - gap2 or
                vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                self.x += self.speed
            else:
                self.waitingTicks += 1

    def _has_gap_down(self):
        """Check if there's space ahead in this lane (down direction)."""
        if self.index == 0:
            return True
        prev = vehicles[self.direction][self.lane][self.index - 1]
        if prev.turned == 1:
            return True
        return self.y + self.currentImage.get_rect().height < prev.y - gap2

    def _move_down(self):
        h = self.currentImage.get_rect().height
        if self.crossed == 0 and self.y + h > stopLines[self.direction]:
            self.crossed = 1
            vehicles[self.direction]['crossed'] += 1
            if self.isEmergency:
                corridor.clear_emergency()
        # ── Ambulance bypass: skip stop-line but respect gap with vehicles ──
        if self.isEmergency and self.crossed == 0 and cfg.emergencyMode and cfg.emergencyDirection == self.direction_number:
            if self._has_gap_down():
                self.y += self.speed
            return
        if self.willTurn == 1:
            if self.crossed == 0 or self.y + h < mid[self.direction]['y']:
                if (self.y + h <= self.stop or (currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and \
                   (self.index == 0 or self.y + h < vehicles[self.direction][self.lane][self.index - 1].y - gap2 or
                    vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                    self.y += self.speed
                else:
                    self.waitingTicks += 1
            else:
                if self.turned == 0:
                    self.rotateAngle += rotationAngle
                    self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                    self.x -= 2.5; self.y += 2
                    if self.rotateAngle == 90:
                        self.turned = 1
                else:
                    prev = vehicles[self.direction][self.lane][self.index - 1] if self.index > 0 else None
                    if prev is None or (self.x > prev.x + prev.currentImage.get_rect().width + gap2) or \
                       (self.y < prev.y - gap2):
                        self.x -= self.speed
        else:
            if (self.y + h <= self.stop or self.crossed == 1 or (currentGreen == 1 and currentYellow == 0)) and \
               (self.index == 0 or self.y + h < vehicles[self.direction][self.lane][self.index - 1].y - gap2 or
                vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                self.y += self.speed
            else:
                self.waitingTicks += 1

    def _has_gap_left(self):
        """Check if there's space ahead in this lane (left direction)."""
        if self.index == 0:
            return True
        prev = vehicles[self.direction][self.lane][self.index - 1]
        if prev.turned == 1:
            return True
        return self.x > prev.x + prev.currentImage.get_rect().width + gap2

    def _move_left(self):
        w = self.currentImage.get_rect().width
        if self.crossed == 0 and self.x < stopLines[self.direction]:
            self.crossed = 1
            vehicles[self.direction]['crossed'] += 1
            if self.isEmergency:
                corridor.clear_emergency()
        # ── Ambulance bypass: skip stop-line but respect gap with vehicles ──
        if self.isEmergency and self.crossed == 0 and cfg.emergencyMode and cfg.emergencyDirection == self.direction_number:
            if self._has_gap_left():
                self.x -= self.speed
            return
        if self.willTurn == 1:
            if self.crossed == 0 or self.x > mid[self.direction]['x']:
                if (self.x >= self.stop or (currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and \
                   (self.index == 0 or self.x > vehicles[self.direction][self.lane][self.index - 1].x +
                    vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().width + gap2 or
                    vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                    self.x -= self.speed
                else:
                    self.waitingTicks += 1
            else:
                if self.turned == 0:
                    self.rotateAngle += rotationAngle
                    self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                    self.x -= 1.8; self.y -= 2.5
                    if self.rotateAngle == 90:
                        self.turned = 1
                else:
                    prev = vehicles[self.direction][self.lane][self.index - 1] if self.index > 0 else None
                    if prev is None or (self.y > prev.y + prev.currentImage.get_rect().height + gap2) or \
                       (self.x > prev.x + gap2):
                        self.y -= self.speed
        else:
            if (self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and \
               (self.index == 0 or self.x > vehicles[self.direction][self.lane][self.index - 1].x +
                vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().width + gap2 or
                vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                self.x -= self.speed
            else:
                self.waitingTicks += 1

    def _has_gap_up(self):
        """Check if there's space ahead in this lane (up direction)."""
        if self.index == 0:
            return True
        prev = vehicles[self.direction][self.lane][self.index - 1]
        if prev.turned == 1:
            return True
        return self.y > prev.y + prev.currentImage.get_rect().height + gap2

    def _move_up(self):
        h = self.currentImage.get_rect().height
        if self.crossed == 0 and self.y < stopLines[self.direction]:
            self.crossed = 1
            vehicles[self.direction]['crossed'] += 1
            if self.isEmergency:
                corridor.clear_emergency()
        # ── Ambulance bypass: skip stop-line but respect gap with vehicles ──
        if self.isEmergency and self.crossed == 0 and cfg.emergencyMode and cfg.emergencyDirection == self.direction_number:
            if self._has_gap_up():
                self.y -= self.speed
            return
        if self.willTurn == 1:
            if self.crossed == 0 or self.y > mid[self.direction]['y']:
                if (self.y >= self.stop or (currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and \
                   (self.index == 0 or self.y > vehicles[self.direction][self.lane][self.index - 1].y +
                    vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().height + gap2 or
                    vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                    self.y -= self.speed
                else:
                    self.waitingTicks += 1
            else:
                if self.turned == 0:
                    self.rotateAngle += rotationAngle
                    self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                    self.x += 1; self.y -= 1
                    if self.rotateAngle == 90:
                        self.turned = 1
                else:
                    prev = vehicles[self.direction][self.lane][self.index - 1] if self.index > 0 else None
                    if prev is None or (self.x < prev.x - prev.currentImage.get_rect().width - gap2) or \
                       (self.y > prev.y + gap2):
                        self.x += self.speed
        else:
            if (self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and \
               (self.index == 0 or self.y > vehicles[self.direction][self.lane][self.index - 1].y +
                vehicles[self.direction][self.lane][self.index - 1].currentImage.get_rect().height + gap2 or
                vehicles[self.direction][self.lane][self.index - 1].turned == 1):
                self.y -= self.speed
            else:
                self.waitingTicks += 1


# ==============================================================================
# INITIALIZATION
# ==============================================================================

def initialize():
    global junction1, junction2

    ts1 = TrafficSignal(0, cfg.defaultYellow, cfg.defaultGreen,
                        cfg.defaultMinimum, cfg.defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, cfg.defaultYellow,
                        cfg.defaultGreen, cfg.defaultMinimum, cfg.defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(cfg.defaultRed, cfg.defaultYellow, cfg.defaultGreen,
                        cfg.defaultMinimum, cfg.defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(cfg.defaultRed, cfg.defaultYellow, cfg.defaultGreen,
                        cfg.defaultMinimum, cfg.defaultMaximum)
    signals.append(ts4)

    # Multi-junction setup
    junction1, junction2 = junction.create_junctions()

    # Generate ambulance sprites (red-tinted bus images)
    corridor.create_ambulance_images()

    repeat()


# ==============================================================================
# SIGNAL CYCLING
# ==============================================================================

def repeat():
    global currentGreen, currentYellow, nextGreen

    while signals[currentGreen].green > 0:
        # ── AI Feature 1: emergency check ────────────────────────────────
        corridor.check_for_emergency(vehicles)
        if cfg.emergencyMode and not cfg.emergencyActive:
            currentGreen = corridor.activate_green_corridor(signals, currentGreen)
            currentYellow = 0
            break  # restart loop with new green

        printStatus()
        updateValues()
        pollution.update_pollution(vehicles, currentGreen)        # Feature 3

        if junction2:                                              # Feature 4
            junction2.update_sync(currentGreen, signals[currentGreen].green)

        # Trigger adaptive detection near end of red on next signal
        if signals[(currentGreen + 1) % cfg.noOfSignals].red == cfg.detectionTime:
            t = threading.Thread(name="detection",
                                 target=adaptive.adaptive_set_time,
                                 args=(signals, vehicles, currentGreen, nextGreen, junction2))
            t.daemon = True
            t.start()

        time.sleep(1)

    # ── Emergency queue loop ───────────────────────────────────────────────
    # Handles single AND multi-ambulance scenarios.
    # When an ambulance crosses, clear_emergency() may chain to the next
    # one in the queue (setting emergencyMode=True, emergencyActive=False
    # with a new direction). We detect that and re-activate signals.
    if cfg.emergencyMode and cfg.emergencyActive:
        prev_direction = cfg.emergencyDirection
        while True:
            # ── Current ambulance still active — tick it ──
            if cfg.emergencyMode and cfg.emergencyActive:
                corridor.tick_emergency()
                corridor.check_for_emergency(vehicles)
                printStatus()
                updateValues()
                pollution.update_pollution(vehicles, currentGreen)
                time.sleep(1)
                continue

            # ── Ambulance crossed (emergencyMode = False) — check queue ──
            if not cfg.emergencyMode:
                # Clean queue of already-crossed ambulances
                cfg.emergencyQueue = [e for e in cfg.emergencyQueue
                                      if e['vehicle'].crossed == 0]

                if not cfg.emergencyQueue:
                    # All done — exit emergency loop
                    break

                # More ambulances waiting — activate next with clearance
                corridor._activate_next_in_queue()
                new_direction = cfg.emergencyDirection

                # ── All-red clearance if direction changes ──
                if new_direction != prev_direction:
                    for i in range(cfg.noOfSignals):
                        signals[i].green = 0
                        signals[i].yellow = 0
                        signals[i].red = 3
                    print("   All-RED clearance (3s)...")
                    for _ in range(3):
                        updateValues()
                        time.sleep(1)

                prev_direction = new_direction
                currentGreen = corridor.activate_green_corridor(signals, currentGreen)
                currentYellow = 0
                continue

            # ── emergencyMode but not Active — needs activation ──
            if cfg.emergencyMode and not cfg.emergencyActive:
                new_direction = cfg.emergencyDirection
                if new_direction != prev_direction:
                    for i in range(cfg.noOfSignals):
                        signals[i].green = 0
                        signals[i].yellow = 0
                        signals[i].red = 3
                    print("   All-RED clearance (3s)...")
                    for _ in range(3):
                        updateValues()
                        time.sleep(1)
                prev_direction = new_direction
                currentGreen = corridor.activate_green_corridor(signals, currentGreen)
                currentYellow = 0

        # Reset signals after ALL emergencies resolved
        for i in range(cfg.noOfSignals):
            signals[i].green  = cfg.defaultGreen
            signals[i].yellow = cfg.defaultYellow
            signals[i].red    = cfg.defaultRed
        signals[currentGreen].red   = 0
        signals[currentGreen].green = cfg.defaultGreen
        nextGreen = (currentGreen + 1) % cfg.noOfSignals
        signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
        repeat()
        return

    # ── Normal yellow phase ──────────────────────────────────────────────
    currentYellow = 1
    vehicleCountTexts[currentGreen] = "0"

    # Record throughput (Feature 2)
    dir_name = cfg.directionNumbers[currentGreen]
    adaptive.record_throughput(dir_name, signals[currentGreen].vehiclesPassedThisCycle)
    signals[currentGreen].vehiclesPassedThisCycle = 0

    # Reset stop coords
    for i in range(3):
        stops[cfg.directionNumbers[currentGreen]][i] = defaultStop[cfg.directionNumbers[currentGreen]]
        for veh in vehicles[cfg.directionNumbers[currentGreen]][i]:
            veh.stop = defaultStop[cfg.directionNumbers[currentGreen]]

    while signals[currentGreen].yellow > 0:
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0

    # Reset current signal to defaults
    signals[currentGreen].green  = cfg.defaultGreen
    signals[currentGreen].yellow = cfg.defaultYellow
    signals[currentGreen].red    = cfg.defaultRed

    # Advance to next signal
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % cfg.noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green
    repeat()


# ==============================================================================
# UTILITIES
# ==============================================================================

def printStatus():
    for i in range(cfg.noOfSignals):
        if i == currentGreen:
            label = " GREEN" if currentYellow == 0 else "YELLOW"
        else:
            label = "   RED"
        print(f"{label} TS{i+1} -> r:{signals[i].red}  y:{signals[i].yellow}  g:{signals[i].green}")
    if cfg.emergencyMode:
        print(f"  EMERGENCY -- {cfg.directionNumbers[cfg.emergencyDirection].upper()}")
    print()


def updateValues():
    # Sync current signal state to cfg for AI modules
    cfg.currentGreen = currentGreen
    cfg.currentYellow = currentYellow
    for i in range(cfg.noOfSignals):
        if i == currentGreen:
            if currentYellow == 0:
                signals[i].green -= 1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1


# ==============================================================================
# VEHICLE GENERATION (with ambulance spawning)
# ==============================================================================

def generateVehicles():
    amb_timer = 0
    while True:
        try:
            amb_timer += 1
            spawn_amb = False
            if amb_timer >= random.randint(40, 80):
                spawn_amb = True
                amb_timer = 0

            if spawn_amb:
                vtype  = 5          # ambulance
                lane   = random.randint(1, 2)
                turn   = 0          # ambulances go straight
                dirnum = random.randint(0, 3)
                Vehicle(lane, cfg.vehicleTypes[vtype], dirnum, cfg.directionNumbers[dirnum], turn)
                print(f"\nAmbulance spawned -> {cfg.directionNumbers[dirnum].upper()}")
            else:
                vtype = random.randint(0, 4)
                lane  = 0 if vtype == 4 else random.randint(1, 2)
                turn  = 0
                if lane == 2:
                    turn = 1 if random.randint(0, 4) <= 2 else 0
                tmp = random.randint(0, 999)
                a = [400, 800, 900, 1000]
                dirnum = 0
                if   tmp < a[0]: dirnum = 0
                elif tmp < a[1]: dirnum = 1
                elif tmp < a[2]: dirnum = 2
                elif tmp < a[3]: dirnum = 3
                Vehicle(lane, cfg.vehicleTypes[vtype], dirnum, cfg.directionNumbers[dirnum], turn)
        except Exception as e:
            print(f"Vehicle generation error (skipping): {e}")

        time.sleep(0.75)


# ==============================================================================
# SIMULATION TIMER
# ==============================================================================

def simulationTime():
    global timeElapsed
    while True:
        timeElapsed += 1
        time.sleep(1)
        if timeElapsed == simTime:
            total = 0
            print('\n─── Simulation Results ───')
            for i in range(cfg.noOfSignals):
                d = cfg.directionNumbers[i]
                print(f"  Lane {i+1} ({d}): {vehicles[d]['crossed']} vehicles")
                total += vehicles[d]['crossed']
            print(f"  Total passed: {total}")
            print(f"  Time: {timeElapsed}s")
            print(f"  Throughput: {total/timeElapsed:.2f} veh/s")
            print('\n─── AI Statistics ───')
            for d in ('right', 'down', 'left', 'up'):
                data = cfg.aiData[d]
                print(f"  {d.upper()}: Score={data['aiScore']}  "
                      f"CO₂={cfg.pollutionLevel[d]:.1f}  "
                      f"Throughput={data['throughputHistory'][-5:]}")
            print(f"  Final AQI: {cfg.totalAQI:.1f}")
            if junction2:
                sync = "SYNCED" if junction2.isSynced else "DESYNCED"
                print(f"  Junction 2: {sync} (Score: {junction2.coordScore:.0f})")
            os._exit(1)


# ==============================================================================
# MAIN
# ==============================================================================

class SimulationApp:
    def __init__(self):
        # ── Colors ───────────────────────────────────────────────────────────
        self.BLACK   = (0, 0, 0)
        self.WHITE   = (255, 255, 255)
        self.DARK_BG = (18, 20, 30)
        self.ACCENT  = (70, 140, 255)
        self.HEADER  = (12, 14, 22)
        self.GREEN_C = (50, 210, 120)
        self.YELLOW_C= (255, 200, 60)
        self.RED_C   = (255, 70, 70)
        self.DIM     = (100, 110, 135)

        # ── Screen ───────────────────────────────────────────────────────────
        self.screenWidth  = 1400
        self.screenHeight = 800
        self.screenSize   = (self.screenWidth, self.screenHeight)
        self.background   = load_image('images/mod_int.png')
        self.screen       = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption("AI-POWERED SMART TRAFFIC MANAGEMENT SYSTEM")
        self.clock = pygame.time.Clock()

        # Signal images
        self.redSignal    = load_image('images/signals/red.png')
        self.yellowSignal = load_image('images/signals/yellow.png')
        self.greenSignal  = load_image('images/signals/green.png')

        # Fonts
        self.f_title   = pygame.font.Font(None, 28)
        self.f_main    = pygame.font.Font(None, 24)
        self.f_signal  = pygame.font.Font(None, 30)
        self.f_small   = pygame.font.Font(None, 20)
        self.f_tiny    = pygame.font.Font(None, 16)

        # Direction info for overlays
        self.dir_info = {
            0: {'name': 'RIGHT', 'color': (255, 130, 90),  'label_pos': (505, 255)},
            1: {'name': 'DOWN',  'color': (90, 180, 255),  'label_pos': (835, 255)},
            2: {'name': 'LEFT',  'color': (90, 230, 160),  'label_pos': (835, 590)},
            3: {'name': 'UP',    'color': (255, 210, 90),  'label_pos': (505, 590)},
        }

    def start_threads(self):
        # Start background threads
        thread4 = threading.Thread(name="simulationTime", target=simulationTime, args=())
        thread4.daemon = True
        thread4.start()

        thread2 = threading.Thread(name="initialization", target=initialize, args=())
        thread2.daemon = True
        thread2.start()

        # Vehicle generation thread
        thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
        thread3.daemon = True
        thread3.start()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                amb_dir = None
                if event.key == pygame.K_1: amb_dir = 0
                elif event.key == pygame.K_2: amb_dir = 1
                elif event.key == pygame.K_3: amb_dir = 2
                elif event.key == pygame.K_4: amb_dir = 3
                if amb_dir is not None:
                    try:
                        lane = random.randint(1, 2)
                        Vehicle(lane, 'ambulance', amb_dir,
                                cfg.directionNumbers[amb_dir], 0)
                        print(f"\nAmbulance spawned (manual) -> "
                              f"{cfg.directionNumbers[amb_dir].upper()}")
                    except Exception as e:
                        print(f"Could not spawn ambulance: {e}")

    def draw_header(self):
        header = pygame.Surface((1400, 42), pygame.SRCALPHA)
        header.fill((*self.HEADER, 235))
        self.screen.blit(header, (0, 0))
        pygame.draw.line(self.screen, self.ACCENT, (0, 42), (1400, 42), 2)
        self.screen.blit(self.f_title.render("AI-POWERED SMART TRAFFIC MANAGEMENT", True, self.WHITE), (15, 10))

        # Header right: time + total count
        total_crossed = sum(vehicles[d]['crossed'] for d in ('right', 'down', 'left', 'up'))
        time_txt = self.f_small.render(f"Time: {timeElapsed}s", True, self.DIM)
        self.screen.blit(time_txt, (850, 14))
        count_txt = self.f_small.render(f"Total Passed: {total_crossed}", True, self.GREEN_C)
        self.screen.blit(count_txt, (950, 14))
        return total_crossed

    def draw_signals(self):
        for i in range(cfg.noOfSignals):
            info = self.dir_info[i]
            # Force green for emergency direction while ambulance is crossing
            is_emergency_green = (cfg.emergencyMode and cfg.emergencyActive and i == cfg.emergencyDirection)
            is_green = is_emergency_green or (i == currentGreen and currentYellow == 0)
            is_yellow = (not is_emergency_green) and (i == currentGreen and currentYellow == 1)

            # Signal image
            if is_green:
                if is_emergency_green:
                    signals[i].signalText = "EMG"
                else:
                    signals[i].signalText = signals[i].green if signals[i].green > 0 else "GO"
                self.screen.blit(self.greenSignal, signalCoods[i])
                sig_color = self.GREEN_C
            elif is_yellow:
                signals[i].signalText = signals[i].yellow if signals[i].yellow > 0 else "!"
                self.screen.blit(self.yellowSignal, signalCoods[i])
                sig_color = self.YELLOW_C
            else:
                if cfg.emergencyMode and i != cfg.emergencyDirection:
                    signals[i].signalText = "WAIT"
                else:
                    signals[i].signalText = signals[i].red if signals[i].red <= 10 else "---"
                self.screen.blit(self.redSignal, signalCoods[i])
                sig_color = self.RED_C

            # Timer box behind countdown
            tx, ty = signalTimerCoods[i]
            timer_bg = pygame.Surface((48, 22), pygame.SRCALPHA)
            timer_bg.fill((0, 0, 0, 180))
            self.screen.blit(timer_bg, (tx - 5, ty - 2))
            timer_txt = self.f_signal.render(str(signals[i].signalText), True, sig_color)
            self.screen.blit(timer_txt, (tx, ty))

            # Direction label near signal
            lx, ly = info['label_pos']
            lbl_bg = pygame.Surface((60, 16), pygame.SRCALPHA)
            lbl_bg.fill((*info['color'], 40))
            self.screen.blit(lbl_bg, (lx, ly))
            self.screen.blit(self.f_tiny.render(info['name'], True, info['color']), (lx + 4, ly + 1))

            # Vehicle count per lane pill
            cx, cy = vehicleCountCoods[i]
            dn = cfg.directionNumbers[i]
            
            l0_count = sum(1 for v in vehicles[dn][0] if v.crossed == 0)
            l1_count = sum(1 for v in vehicles[dn][1] if v.crossed == 0)
            l2_count = sum(1 for v in vehicles[dn][2] if v.crossed == 0)
            lane_txt = f"L1:{l0_count} | L2:{l1_count} | L3:{l2_count}"
            
            pill_bg = pygame.Surface((128, 18), pygame.SRCALPHA)
            pill_bg.fill((0, 0, 0, 160))
            self.screen.blit(pill_bg, (cx - 39, cy))
            self.screen.blit(self.f_small.render(lane_txt, True, self.WHITE), (cx - 35, cy + 2))

    def draw_footer(self, total_crossed):
        bar = pygame.Surface((1050, 30), pygame.SRCALPHA)
        bar.fill((*self.HEADER, 220))
        self.screen.blit(bar, (0, 770))
        pygame.draw.line(self.screen, (40, 50, 75), (0, 770), (1050, 770))

        # Mode indicator
        mode_c = self.GREEN_C if cfg.aiMode == "NORMAL" else self.RED_C if cfg.aiMode == "EMERGENCY" else self.YELLOW_C
        self.screen.blit(self.f_tiny.render(f"MODE: {cfg.aiMode}", True, mode_c), (15, 777))

        # AQI
        aqi_c = self.GREEN_C if cfg.totalAQI < 20 else self.YELLOW_C if cfg.totalAQI < 40 else self.RED_C
        self.screen.blit(self.f_tiny.render(f"AQI: {cfg.totalAQI:.1f}", True, aqi_c), (180, 777))

        # Queue
        q_len = len(cfg.emergencyQueue)
        q_c = self.RED_C if q_len > 0 else self.DIM
        self.screen.blit(self.f_tiny.render(f"Queue: {q_len}", True, q_c), (280, 777))

        # Per-direction waiting
        for di in range(4):
            dn = cfg.directionNumbers[di]
            waiting = 0
            for ln in range(3):
                for v in vehicles[dn][ln]:
                    if v.crossed == 0:
                        waiting += 1
            c = self.dir_info[di]['color']
            self.screen.blit(self.f_tiny.render(f"{self.dir_info[di]['name'][0]}:{waiting}", True, c),
                         (380 + di * 55, 777))

        # Throughput
        if timeElapsed > 0:
            tp = total_crossed / timeElapsed
            self.screen.blit(self.f_tiny.render(f"Throughput: {tp:.2f} v/s", True, self.DIM), (620, 777))

        # Controls hint
        self.screen.blit(self.f_tiny.render("Press 1-4: Spawn Ambulance", True, (80, 85, 110)), (800, 777))

    def run(self):
        self.start_threads()

        while True:
            self.handle_events()
            
            # Background
            self.screen.blit(self.background, (0, 0))

            # UI Header
            total_crossed = self.draw_header()

            # Signals
            self.draw_signals()

            # Vehicles
            for vehicle in simulation:
                self.screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
                vehicle.move()

            # AI overlays
            hud.draw_emergency_overlay(self.screen)
            hud.draw_ai_panel(self.screen, vehicles, currentGreen, currentYellow, junction2)

            # Footer
            self.draw_footer(total_crossed)

            pygame.display.update()
            self.clock.tick(60)


if __name__ == '__main__':
    app = SimulationApp()
    app.run()
