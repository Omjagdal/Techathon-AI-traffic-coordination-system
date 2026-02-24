# ==============================================================================
# AI FEATURE 2: ADAPTIVE SIGNAL TIMING — Weighted multi-factor scoring
# ==============================================================================

import math
import os
import ai_config as cfg


def adaptive_set_time(signals, vehicles, currentGreen, nextGreen, junction2=None):
    """
    Calculate the optimal green time for *nextGreen* direction using
    a weighted combination of vehicle count, average wait, queue length,
    recent throughput, and pollution bonus.
    """
    if cfg.emergencyMode:
        return  # don't touch timers during an emergency

    dir_name = cfg.directionNumbers[nextGreen]

    # macOS TTS announcement (matches original behaviour)
    os.system("say detecting vehicles, " + dir_name)

    # ── Count waiting vehicles ───────────────────────────────────────────
    counts = {'car': 0, 'bus': 0, 'truck': 0, 'rickshaw': 0, 'bike': 0, 'ambulance': 0}
    total_wait_ticks = 0
    queue_count = 0

    for lane in range(3):
        for veh in vehicles[dir_name][lane]:
            if veh.crossed == 0:
                counts[veh.vehicleClass] = counts.get(veh.vehicleClass, 0) + 1
                total_wait_ticks += veh.waitingTicks
                queue_count += 1

    # ── Base green time (original formula) ───────────────────────────────
    base_green = math.ceil(
        (counts['car'] * cfg.carTime +
         counts['rickshaw'] * cfg.rickshawTime +
         counts['bus'] * cfg.busTime +
         counts['truck'] * cfg.truckTime +
         counts['bike'] * cfg.bikeTime +
         counts['ambulance'] * cfg.ambulanceTime)
        / (cfg.noOfLanes + 1)
    )

    # ── AI scoring ───────────────────────────────────────────────────────
    vehicle_count = sum(counts.values())
    avg_wait = (total_wait_ticks / max(1, queue_count)) / 60.0

    hist = cfg.aiData[dir_name]['throughputHistory']
    recent_tp = sum(hist[-5:]) / max(1, len(hist[-5:])) if hist else 0

    pollution_bonus = max(
        0, (cfg.pollutionLevel[dir_name] - cfg.pollutionThreshold) * cfg.AI_WEIGHTS['pollution']
    )

    ai_score = (
        cfg.AI_WEIGHTS['vehicle_count'] * vehicle_count
        + cfg.AI_WEIGHTS['wait_time'] * avg_wait
        + cfg.AI_WEIGHTS['queue_length'] * queue_count
        - cfg.AI_WEIGHTS['throughput'] * recent_tp
        + pollution_bonus
    )

    green_time = math.ceil(base_green + ai_score * 0.8)
    green_time = max(cfg.defaultMinimum, min(cfg.defaultMaximum, green_time))

    # Multi-junction coordination bonus (Feature 4)
    if junction2 and junction2.isSynced:
        green_time = min(green_time + 3, cfg.defaultMaximum)

    # ── Store data for HUD ───────────────────────────────────────────────
    cfg.aiData[dir_name]['aiScore'] = round(ai_score, 1)
    cfg.aiData[dir_name]['waitTime'] = round(avg_wait, 1)
    cfg.aiData[dir_name]['queueLength'] = queue_count

    print(f"🧠 AI Green [{dir_name}]: {green_time}s  "
          f"(score={ai_score:.1f}  veh={vehicle_count}  "
          f"wait={avg_wait:.1f}  q={queue_count}  "
          f"CO₂={cfg.pollutionLevel[dir_name]:.1f})")

    signals[(currentGreen + 1) % cfg.noOfSignals].green = green_time


def record_throughput(direction_name, passed_count):
    """Append this cycle's throughput and keep only the last 20 entries."""
    hist = cfg.aiData[direction_name]['throughputHistory']
    hist.append(passed_count)
    if len(hist) > 20:
        cfg.aiData[direction_name]['throughputHistory'] = hist[-20:]
