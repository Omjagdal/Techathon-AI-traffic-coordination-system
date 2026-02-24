# ==============================================================================
# AI FEATURE 3: POLLUTION-AWARE SIGNAL OPTIMIZATION
# ==============================================================================

import ai_config as cfg


def update_pollution(vehicles, currentGreen):
    """
    Accumulate CO₂ from idling vehicles (waiting at red) and
    apply natural dissipation each tick.  Updates cfg.totalAQI
    and cfg.aiMode when pollution is critical.
    """
    for dir_num in range(cfg.noOfSignals):
        dir_name = cfg.directionNumbers[dir_num]

        # Vehicles on a red signal are idling → emit CO₂
        if dir_num != currentGreen:
            for lane in range(3):
                for veh in vehicles[dir_name][lane]:
                    if veh.crossed == 0:
                        rate = cfg.emissionRates.get(veh.vehicleClass, 1.0)
                        cfg.pollutionLevel[dir_name] += rate * 0.05

        # Natural dissipation
        cfg.pollutionLevel[dir_name] = max(0.0, cfg.pollutionLevel[dir_name] - 0.3)

    # Aggregate AQI
    cfg.totalAQI = sum(cfg.pollutionLevel.values()) / 4.0

    # Raise / clear pollution alert (don't override EMERGENCY)
    if not cfg.emergencyMode:
        if any(p > cfg.pollutionThreshold * 1.5 for p in cfg.pollutionLevel.values()):
            cfg.aiMode = "POLLUTION_ALERT"
        elif cfg.aiMode == "POLLUTION_ALERT":
            cfg.aiMode = "NORMAL"
