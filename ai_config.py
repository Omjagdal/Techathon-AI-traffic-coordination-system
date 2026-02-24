# ==============================================================================
# AI CONFIGURATION — All constants, weights, and shared state for AI features
# ==============================================================================

# ── Signal defaults ──────────────────────────────────────────────────────────
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

# ── Current signal state (updated by simulation loop) ───────────────────────
currentGreen = 0
currentYellow = 0

# ── Vehicle timing (seconds to pass intersection) ───────────────────────────
carTime = 2
bikeTime = 1
rickshawTime = 2.25
busTime = 2.5
truckTime = 2.5
ambulanceTime = 1.5

# ── Vehicle speeds ───────────────────────────────────────────────────────────
speeds = {
    'car': 2.25, 'bus': 1.8, 'truck': 1.8,
    'rickshaw': 2, 'bike': 2.5, 'ambulance': 3.0
}

# ── Vehicle & direction maps ────────────────────────────────────────────────
vehicleTypes = {0: 'car', 1: 'bus', 2: 'truck', 3: 'rickshaw', 4: 'bike', 5: 'ambulance'}
directionNumbers = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}
noOfSignals = 4
noOfLanes = 2

# ── Adaptive Signal Timing weights ──────────────────────────────────────────
AI_WEIGHTS = {
    'vehicle_count': 0.4,
    'wait_time': 0.3,
    'queue_length': 0.2,
    'throughput': 0.1,
    'pollution': 0.15
}

# ── Emission rates per vehicle type (relative CO₂ units) ────────────────────
emissionRates = {
    'car': 2.3, 'bus': 5.0, 'truck': 6.0,
    'rickshaw': 1.0, 'bike': 0.5, 'ambulance': 4.0
}

# ── Pollution thresholds ────────────────────────────────────────────────────
pollutionThreshold = 50.0

# ── Detection timing ────────────────────────────────────────────────────────
detectionTime = 5

# ==============================================================================
# SHARED MUTABLE STATE  (imported by all AI modules)
# ==============================================================================

# Per-direction AI tracking
aiData = {
    d: {'waitTime': 0, 'queueLength': 0, 'throughputHistory': [], 'aiScore': 0}
    for d in ('right', 'down', 'left', 'up')
}

# Pollution levels per direction
pollutionLevel = {'right': 0.0, 'down': 0.0, 'left': 0.0, 'up': 0.0}
totalAQI = 0.0

# Emergency state — priority queue for multi-ambulance handling
emergencyMode = False
emergencyDirection = -1
emergencyActive = False
emergencyVehicle = None
emergencyTimer = 0
emergencyQueue = []        # list of dicts: {dir, vehicle, arrivalTick, score}
emergencyGreenTime = 15    # shorter green per ambulance when queued (cycles faster)
emergencyServed = 0        # count of ambulances served this burst

# AI mode label for HUD
aiMode = "NORMAL"
