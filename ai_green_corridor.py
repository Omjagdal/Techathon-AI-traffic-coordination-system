# ==============================================================================
# AI FEATURE 1: GREEN CORRIDOR — Multi-Ambulance Priority Queue
# ==============================================================================
#
# When ambulances appear on multiple lanes simultaneously, this module:
#   1. Detects ALL uncrossed ambulances and adds them to a priority queue
#   2. Scores each by: proximity to intersection + wait time + lane congestion
#   3. Serves the highest-priority ambulance first (shorter 15s green each)
#   4. After one crosses, immediately serves the next in the queue
#   5. Returns to normal only when the queue is fully drained
# ==============================================================================

import os
import time
import pygame
import ai_config as cfg
from image_loader import load_image, save_image

# Maximum seconds per ambulance green (shorter to cycle through queue faster)
EMERGENCY_GREEN = 8
# Absolute timeout per ambulance before auto-skipping
EMERGENCY_TIMEOUT = 12

_tick_counter = 0   # monotonic tick for arrival ordering


def create_ambulance_images():
    """Create red-tinted bus sprites for ambulance in all 4 directions."""
    for direction in ('right', 'down', 'left', 'up'):
        bus_path = os.path.join("images", direction, "bus.png")
        amb_path = os.path.join("images", direction, "ambulance.png")
        if os.path.exists(amb_path):
            continue
        if not os.path.exists(bus_path):
            print(f"  bus.png not found for {direction}, skipping ambulance image")
            continue
        try:
            bus_img = load_image(bus_path)
            amb_img = bus_img.copy()
            red_overlay = pygame.Surface(amb_img.get_size(), pygame.SRCALPHA)
            red_overlay.fill((255, 30, 30, 120))
            amb_img.blit(red_overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            red_boost = pygame.Surface(amb_img.get_size(), pygame.SRCALPHA)
            red_boost.fill((255, 50, 50, 80))
            amb_img.blit(red_boost, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            save_image(amb_img, amb_path)
            print(f"  Created ambulance image: {amb_path}")
        except Exception as exc:
            print(f"  Could not create ambulance image for {direction}: {exc}")


# ==============================================================================
# PRIORITY SCORING
# ==============================================================================

def _score_ambulance(vehicle, dir_num, vehicles_dict):
    """
    Score an ambulance — higher score = higher priority (served first).

    Factors (100 pts total):
      1. Distance to intersection:  closer = higher score       (30 pts max)
      2. Waiting time:              longer wait = higher score   (20 pts max)
      3. Traffic density:           more vehicles = more urgent  (20 pts max)
      4. Arrival order:             first-come = higher score    (15 pts max)
      5. Signal advantage:          already green = lower score  (15 pts max)
    """
    dir_name = cfg.directionNumbers[dir_num]
    score = 0.0

    # 1. Distance to intersection (closer = higher score, 30 pts max)
    stop_line = {'right': 590, 'down': 330, 'left': 800, 'up': 535}[dir_name]
    if dir_name == 'right':
        distance = max(0, stop_line - vehicle.x)
        max_dist = stop_line
    elif dir_name == 'down':
        distance = max(0, stop_line - vehicle.y)
        max_dist = stop_line
    elif dir_name == 'left':
        distance = max(0, vehicle.x - stop_line)
        max_dist = 1400 - stop_line
    else:  # up
        distance = max(0, vehicle.y - stop_line)
        max_dist = 800 - stop_line

    proximity = 1.0 - min(distance / max(1, max_dist), 1.0)
    score += proximity * 30.0

    # 2. Waiting time (longer wait = higher score, 20 pts max)
    score += min(vehicle.waitingTicks / 80.0, 1.0) * 20.0

    # 3. Traffic density — vehicles blocking this direction (20 pts max)
    congestion = 0
    for lane in range(3):
        for v in vehicles_dict[dir_name][lane]:
            if v.crossed == 0:
                congestion += 1
    score += min(congestion / 20.0, 1.0) * 20.0

    # 4. Arrival order — earlier arrival = higher score (15 pts max)
    # _tick_counter increases monotonically; lower tick = arrived first
    tick_age = _tick_counter - getattr(vehicle, '_queue_tick', _tick_counter)
    age_bonus = min(tick_age / 30.0, 1.0) * 15.0
    score += age_bonus

    # 5. Signal advantage — if this direction already has green, lower priority
    #    (ambulance can pass without emergency mode), 15 pts max
    if dir_num == cfg.currentGreen and cfg.currentYellow == 0:
        # Already green — ambulance can pass naturally, low priority
        score += 0.0
    elif dir_num == (cfg.currentGreen + 1) % cfg.noOfSignals:
        # Next to be green — moderate bonus
        score += 8.0
    else:
        # Far from getting green — needs emergency override, high priority
        score += 15.0

    return round(score, 1)


# ==============================================================================
# DETECTION — scan for ALL ambulances, build priority queue
# ==============================================================================

def check_for_emergency(vehicles):
    """
    Scan all lanes for uncrossed ambulances.
    Adds new ones to the priority queue (avoids duplicates).
    """
    global _tick_counter
    _tick_counter += 1

    # Collect ambulance IDs already in queue to avoid duplicates
    queued_ids = {id(entry['vehicle']) for entry in cfg.emergencyQueue}

    for dir_num in range(cfg.noOfSignals):
        dir_name = cfg.directionNumbers[dir_num]
        for lane in range(3):
            for veh in vehicles[dir_name][lane]:
                if veh.isEmergency and veh.crossed == 0 and id(veh) not in queued_ids:
                    score = _score_ambulance(veh, dir_num, vehicles)
                    veh._queue_tick = _tick_counter  # stamp arrival for ordering
                    entry = {
                        'dir': dir_num,
                        'vehicle': veh,
                        'arrivalTick': _tick_counter,
                        'score': score,
                    }
                    cfg.emergencyQueue.append(entry)
                    queued_ids.add(id(veh))
                    print(f"  + Ambulance queued: {dir_name.upper()} "
                          f"(score={score}, queue={len(cfg.emergencyQueue)})")

    # Remove crossed ambulances from queue
    cfg.emergencyQueue = [e for e in cfg.emergencyQueue if e['vehicle'].crossed == 0]

    # Re-sort queue by score (highest first) after every update
    cfg.emergencyQueue.sort(key=lambda e: e['score'], reverse=True)

    # Activate emergency mode if queue has entries and not already active
    if cfg.emergencyQueue and not cfg.emergencyMode:
        _activate_next_in_queue()


# ==============================================================================
# QUEUE PROCESSING
# ==============================================================================

def _activate_next_in_queue():
    """Pick the highest-priority ambulance from the queue and activate green."""
    if not cfg.emergencyQueue:
        _clear_all_emergency()
        return

    # Re-sort (scores may have changed)
    cfg.emergencyQueue.sort(key=lambda e: e['score'], reverse=True)

    entry = cfg.emergencyQueue[0]
    dir_num  = entry['dir']
    dir_name = cfg.directionNumbers[dir_num]

    cfg.emergencyMode = True
    cfg.emergencyDirection = dir_num
    cfg.emergencyVehicle = entry['vehicle']
    cfg.emergencyActive = False   # will be set True by activate_green_corridor
    cfg.emergencyTimer = 0
    cfg.aiMode = "EMERGENCY"

    print(f"\n  >> PRIORITY AMBULANCE: {dir_name.upper()} "
          f"(score={entry['score']}, remaining={len(cfg.emergencyQueue)})")


def activate_green_corridor(signals, currentGreen):
    """
    Force green for the current priority ambulance direction.
    Uses shorter green time (15s) to cycle through queue faster.
    Returns the new currentGreen value.
    """
    if not cfg.emergencyMode or cfg.emergencyActive:
        return currentGreen

    cfg.emergencyActive = True
    new_green = cfg.emergencyDirection
    green_t = EMERGENCY_GREEN if len(cfg.emergencyQueue) > 1 else cfg.defaultMaximum

    for i in range(cfg.noOfSignals):
        if i == cfg.emergencyDirection:
            signals[i].green = green_t
            signals[i].yellow = 0
            signals[i].red = 0
        else:
            signals[i].red = green_t + cfg.defaultYellow
            signals[i].green = 0
            signals[i].yellow = 0

    q_info = f"[{len(cfg.emergencyQueue)} in queue]" if len(cfg.emergencyQueue) > 1 else ""
    print(f"   GREEN CORRIDOR -> {cfg.directionNumbers[cfg.emergencyDirection].upper()} "
          f"({green_t}s) {q_info}")
    return new_green


# ==============================================================================
# CLEANUP / TRANSITIONS
# ==============================================================================

def clear_emergency():
    """Called when the current ambulance crosses — mark current done.
    
    NOTE: Does NOT auto-chain to next ambulance. The emergency loop
    in repeat() handles the transition with all-red clearance to
    prevent cross-traffic collisions between direction switches.
    """
    if not cfg.emergencyMode:
        return

    cfg.emergencyServed += 1
    dir_name = cfg.directionNumbers[cfg.emergencyDirection]

    # Remove crossed ambulances from queue
    cfg.emergencyQueue = [e for e in cfg.emergencyQueue if e['vehicle'].crossed == 0]
    remaining = len(cfg.emergencyQueue)

    print(f"   Ambulance crossed ({dir_name.upper()}) — "
          f"served #{cfg.emergencyServed}, {remaining} remaining")

    # Reset current emergency state — loop will pick up next
    cfg.emergencyMode = False
    cfg.emergencyDirection = -1
    cfg.emergencyActive = False
    cfg.emergencyVehicle = None
    cfg.emergencyTimer = 0

    if not cfg.emergencyQueue:
        cfg.aiMode = "NORMAL"
        cfg.emergencyServed = 0
        print("   All ambulances served - resuming normal operations")


def _clear_all_emergency():
    """Full reset when queue is empty."""
    cfg.emergencyMode = False
    cfg.emergencyDirection = -1
    cfg.emergencyActive = False
    cfg.emergencyVehicle = None
    cfg.emergencyTimer = 0
    cfg.emergencyQueue = []
    cfg.emergencyServed = 0
    cfg.aiMode = "NORMAL"


def tick_emergency():
    """
    Called once per second during emergency.
    Auto-skips current ambulance if it doesn't cross in EMERGENCY_TIMEOUT.
    """
    if not cfg.emergencyMode:
        return

    cfg.emergencyTimer += 1

    # Timeout: skip this ambulance and serve next
    if cfg.emergencyTimer >= EMERGENCY_TIMEOUT:
        dir_name = cfg.directionNumbers[cfg.emergencyDirection]
        print(f"   Timeout ({EMERGENCY_TIMEOUT}s) for {dir_name.upper()} — skipping to next")

        # Remove timed-out entry from queue
        cfg.emergencyQueue = [
            e for e in cfg.emergencyQueue
            if id(e['vehicle']) != id(cfg.emergencyVehicle)
        ]

        cfg.emergencyMode = False
        cfg.emergencyDirection = -1
        cfg.emergencyActive = False
        cfg.emergencyVehicle = None
        cfg.emergencyTimer = 0

        if cfg.emergencyQueue:
            _activate_next_in_queue()
        else:
            _clear_all_emergency()
