# ==============================================================================
# AI FEATURE 4: MULTI-JUNCTION COORDINATION — Green wave strategy
# ==============================================================================

import ai_config as cfg


class Junction:
    """Represents one traffic junction with its own phase and sync state."""

    def __init__(self, name, offset=0):
        self.name = name
        self.offset = offset          # ideal seconds between J1 green end → J2 green start
        self.greenPhase = 0           # which direction is green (0-3)
        self.greenTimer = cfg.defaultGreen
        self.coordScore = 0.0         # 0-100 coordination quality
        self.isSynced = False
        self.distance = 500           # simulated pixel distance between junctions
        self.avgSpeed = 2.0           # average vehicle speed

    def calculate_optimal_offset(self):
        """Offset = travel-time between junctions."""
        self.offset = self.distance / (self.avgSpeed * 60)
        return self.offset

    def update_sync(self, primary_green, primary_timer):
        """
        Score how well junction-2's green aligns with the expected
        arrival of vehicles from junction-1.
        """
        time_diff = abs(self.greenTimer - self.offset) % cfg.defaultGreen
        self.coordScore = max(0.0, 100.0 - time_diff * 10)
        self.isSynced = self.coordScore > 60

        if primary_timer > 0:
            self.greenPhase = (primary_green + 1) % cfg.noOfSignals
            self.greenTimer = max(1, primary_timer - int(self.offset))


def create_junctions():
    """Return (junction1, junction2) ready for use."""
    j1 = Junction("Junction 1 (Primary)", offset=0)
    j2 = Junction("Junction 2 (Downstream)", offset=0)
    j2.calculate_optimal_offset()
    return j1, j2
