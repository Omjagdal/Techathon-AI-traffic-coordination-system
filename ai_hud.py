# ==============================================================================
# AI HUD — Professional, clean dashboard overlay
# ==============================================================================

import math
import time
import pygame
import ai_config as cfg


# ── Color palette ────────────────────────────────────────────────────────────
C_BG         = (15, 15, 25)
C_PANEL      = (22, 24, 35)
C_BORDER     = (55, 65, 95)
C_ACCENT     = (70, 140, 255)
C_TEXT       = (210, 215, 230)
C_TEXT_DIM   = (120, 130, 155)
C_GREEN      = (50, 210, 120)
C_YELLOW     = (255, 200, 60)
C_RED        = (255, 70, 70)
C_ORANGE     = (255, 140, 50)
C_WHITE      = (240, 240, 250)


def _get_color_for_level(val, low, high):
    """Return green/yellow/red based on thresholds."""
    if val < low:
        return C_GREEN
    elif val < high:
        return C_YELLOW
    return C_RED


def _draw_bar(screen, x, y, w, h, fill_pct, color, bg=(40, 42, 55)):
    """Draw a rounded progress bar."""
    pygame.draw.rect(screen, bg, (x, y, w, h), border_radius=3)
    fw = max(0, min(w, int(fill_pct * w)))
    if fw > 0:
        pygame.draw.rect(screen, color, (x, y, fw, h), border_radius=3)


def _draw_section_header(screen, font, text, x, y, w):
    """Draw a section divider with label."""
    pygame.draw.line(screen, C_BORDER, (x, y + 8), (x + w, y + 8))
    label = font.render(text, True, C_ACCENT)
    screen.blit(label, (x, y))
    return y + 22


# ==============================================================================
# MAIN AI PANEL
# ==============================================================================

def draw_ai_panel(screen, vehicles, currentGreen, currentYellow, junction2):
    """Render the AI dashboard — clean, professional layout."""

    PX, PY, PW, PH = 1050, 80, 340, 710

    # ── Panel background ─────────────────────────────────────────────────
    panel = pygame.Surface((PW, PH), pygame.SRCALPHA)
    panel.fill((*C_PANEL, 220))
    screen.blit(panel, (PX, PY))
    pygame.draw.rect(screen, C_BORDER, (PX, PY, PW, PH), 1, border_radius=6)

    # ── Fonts ────────────────────────────────────────────────────────────
    f_title = pygame.font.Font(None, 26)
    f_label = pygame.font.Font(None, 21)
    f_small = pygame.font.Font(None, 18)
    f_tiny  = pygame.font.Font(None, 16)

    y = PY + 12

    # ── Title bar ────────────────────────────────────────────────────────
    screen.blit(f_title.render("AI TRAFFIC CONTROL", True, C_WHITE), (PX + 65, y))
    y += 22

    # Mode badge
    mode_colors = {"NORMAL": C_GREEN, "EMERGENCY": C_RED, "POLLUTION_ALERT": C_ORANGE}
    mc = mode_colors.get(cfg.aiMode, C_TEXT_DIM)
    badge = pygame.Surface((70, 16), pygame.SRCALPHA)
    badge.fill((*mc, 60))
    screen.blit(badge, (PX + 135, y))
    screen.blit(f_tiny.render(cfg.aiMode, True, mc), (PX + 140, y + 1))
    y += 24

    # ── Per-direction stats ──────────────────────────────────────────────
    y = _draw_section_header(screen, f_small, "SIGNAL INTELLIGENCE", PX + 10, y, PW - 20)

    dir_labels  = {0: 'RIGHT', 1: 'DOWN', 2: 'LEFT', 3: 'UP'}
    dir_arrows  = {0: '\u2192', 1: '\u2193', 2: '\u2190', 3: '\u2191'}
    dir_colors  = {0: (255, 130, 90), 1: (90, 180, 255), 2: (90, 230, 160), 3: (255, 210, 90)}

    for dn in range(cfg.noOfSignals):
        dname = cfg.directionNumbers[dn]
        data  = cfg.aiData[dname]
        poll  = cfg.pollutionLevel[dname]
        is_green = (dn == currentGreen and currentYellow == 0)

        # Direction row background
        row_bg = pygame.Surface((PW - 20, 62), pygame.SRCALPHA)
        if is_green:
            row_bg.fill((50, 210, 120, 25))
        else:
            row_bg.fill((255, 255, 255, 8))
        screen.blit(row_bg, (PX + 10, y))

        # Direction label
        dc = dir_colors[dn]
        status_dot = "\u25cf" if is_green else "\u25cb"
        screen.blit(f_label.render(
            f"{status_dot} {dir_labels[dn]} {dir_arrows[dn]}", True, dc),
            (PX + 16, y + 3))

        # Stats row 1
        vcount = sum(1 for ln in range(3) for v in vehicles[dname][ln] if v.crossed == 0)
        screen.blit(f_tiny.render(
            f"Veh: {vcount}", True, C_TEXT_DIM), (PX + 160, y + 4))
        screen.blit(f_tiny.render(
            f"Q: {data['queueLength']}", True, C_TEXT_DIM), (PX + 220, y + 4))
        screen.blit(f_tiny.render(
            f"AI: {data['aiScore']}", True, C_ACCENT), (PX + 270, y + 4))

        # Pollution mini-bar
        poll_pct = min(1.0, poll / (cfg.pollutionThreshold * 2))
        poll_color = _get_color_for_level(poll, cfg.pollutionThreshold * 0.5, cfg.pollutionThreshold)
        _draw_bar(screen, PX + 16, y + 22, 180, 5, poll_pct, poll_color)
        screen.blit(f_tiny.render(f"CO\u2082 {poll:.0f}", True, poll_color), (PX + 200, y + 19))

        # Wait time
        screen.blit(f_tiny.render(
            f"Wait: {data['waitTime']}s", True, C_TEXT_DIM), (PX + 260, y + 19))

        # Thin separator
        pygame.draw.line(screen, (40, 45, 65), (PX + 15, y + 35), (PX + PW - 15, y + 35))

        y += 40

    y += 5

    # ── AQI ──────────────────────────────────────────────────────────────
    y = _draw_section_header(screen, f_small, "AIR QUALITY", PX + 10, y, PW - 20)
    aqi_c = _get_color_for_level(cfg.totalAQI, cfg.pollutionThreshold * 0.3, cfg.pollutionThreshold * 0.7)
    aqi_pct = min(1.0, cfg.totalAQI / cfg.pollutionThreshold)
    _draw_bar(screen, PX + 15, y, 220, 8, aqi_pct, aqi_c)
    screen.blit(f_label.render(f"AQI: {cfg.totalAQI:.1f}", True, aqi_c), (PX + 245, y - 2))
    y += 22

    # ── Junction Coordination ────────────────────────────────────────────
    y = _draw_section_header(screen, f_small, "JUNCTION SYNC", PX + 10, y, PW - 20)
    if junction2:
        sc   = C_GREEN if junction2.isSynced else C_RED
        tag  = "SYNCED" if junction2.isSynced else "DESYNCED"
        screen.blit(f_label.render(f"J2: {tag}", True, sc), (PX + 15, y))
        screen.blit(f_tiny.render(
            f"Score: {junction2.coordScore:.0f}/100", True, C_TEXT_DIM), (PX + 140, y + 2))

        coord_pct = junction2.coordScore / 100.0
        _draw_bar(screen, PX + 15, y + 20, 250, 6, coord_pct, sc)
        screen.blit(f_tiny.render(
            f"Offset: {junction2.offset:.1f}s  Phase: {junction2.greenPhase}",
            True, C_TEXT_DIM), (PX + 15, y + 30))
        y += 48
    else:
        y += 15

    # ── Emergency / Queue ─────────────────────────────────────────────────
    queue_len = len(cfg.emergencyQueue)
    if cfg.emergencyMode or queue_len > 0:
        y = _draw_section_header(screen, f_small, "EMERGENCY QUEUE", PX + 10, y, PW - 20)

        if cfg.emergencyMode:
            pulse = int(180 + 75 * math.sin(time.time() * 6))
            alert_bg = pygame.Surface((PW - 20, 24), pygame.SRCALPHA)
            alert_bg.fill((255, 40, 40, pulse))
            screen.blit(alert_bg, (PX + 10, y))
            screen.blit(f_label.render(
                f"ACTIVE: {cfg.directionNumbers[cfg.emergencyDirection].upper()} "
                f"({cfg.emergencyTimer}s)",
                True, C_WHITE), (PX + 15, y + 4))
            y += 28

        # Show queue entries
        for i, entry in enumerate(cfg.emergencyQueue[:4]):
            dname = cfg.directionNumbers[entry['dir']].upper()
            sc = entry['score']
            marker = ">>" if (cfg.emergencyVehicle and id(entry['vehicle']) == id(cfg.emergencyVehicle)) else f"#{i+1}"
            c = C_YELLOW if marker == ">>" else C_TEXT_DIM
            screen.blit(f_tiny.render(
                f"{marker} {dname}  score={sc}", True, c), (PX + 20, y))
            y += 15

        if queue_len > 4:
            screen.blit(f_tiny.render(f"  +{queue_len - 4} more...", True, C_TEXT_DIM), (PX + 20, y))
            y += 15

        # Served counter
        if cfg.emergencyServed > 0:
            screen.blit(f_tiny.render(
                f"Served: {cfg.emergencyServed}", True, C_GREEN), (PX + 220, y - 15))
        y += 5

    # ── Controls ─────────────────────────────────────────────────────────
    y = _draw_section_header(screen, f_small, "CONTROLS", PX + 10, y, PW - 20)

    controls = [
        ("1", "Ambulance RIGHT"),
        ("2", "Ambulance DOWN"),
        ("3", "Ambulance LEFT"),
        ("4", "Ambulance UP"),
    ]
    for key, desc in controls:
        key_bg = pygame.Surface((18, 16), pygame.SRCALPHA)
        key_bg.fill((*C_ACCENT, 80))
        screen.blit(key_bg, (PX + 15, y))
        screen.blit(f_tiny.render(key, True, C_WHITE), (PX + 20, y + 1))
        screen.blit(f_tiny.render(desc, True, C_TEXT_DIM), (PX + 40, y + 1))
        y += 18


# ==============================================================================
# EMERGENCY OVERLAY
# ==============================================================================

def draw_emergency_overlay(screen):
    """Subtle pulsing red border + top banner during emergency."""
    if not cfg.emergencyMode:
        return

    alpha = int(30 + 25 * math.sin(time.time() * 6))
    overlay = pygame.Surface((1400, 800), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (255, 0, 0, alpha), (0, 0, 1400, 800), 6)
    screen.blit(overlay, (0, 0))

    f = pygame.font.Font(None, 32)
    txt = f.render(
        f"EMERGENCY CORRIDOR  --  {cfg.directionNumbers[cfg.emergencyDirection].upper()}",
        True, C_RED)
    r = txt.get_rect(center=(530, 22))
    bg = pygame.Surface((r.width + 24, r.height + 8), pygame.SRCALPHA)
    bg.fill((15, 0, 0, 200))
    screen.blit(bg, (r.x - 12, r.y - 4))
    screen.blit(txt, r)
