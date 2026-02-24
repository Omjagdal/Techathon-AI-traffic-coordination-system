import { useRef, useEffect, useState } from 'react';

// ── Sprite paths ─────────────────────────────────────────────────────────────
const SPRITE_PATHS = {
    intersection: '/sprites/intersection.png',
    car: '/sprites/car.png',
    bus: '/sprites/bus.png',
    truck: '/sprites/truck.png',
    rickshaw: '/sprites/rickshaw.png',
    bike: '/sprites/bike.png',
    ambulance: '/sprites/ambulance.png',
};

// ── Vehicle sprite target sizes (width × height facing right) ────────────────
const VEHICLE_SPRITES = {
    car: { w: 90, h: 44 },
    bus: { w: 130, h: 44 },
    truck: { w: 120, h: 48 },
    rickshaw: { w: 72, h: 38 },
    bike: { w: 60, h: 28 },
    ambulance: { w: 120, h: 48 },
};

// ── Direction → rotation angle (degrees, clockwise) ──────────────────────────
const DIR_ROTATION = {
    right: 0,
    down: 90,
    left: 180,
    up: 270,
};

const SIGNAL_POSITIONS = [
    { x: 540, y: 240, labelX: 505, labelY: 210, label: 'E' },
    { x: 810, y: 240, labelX: 835, labelY: 210, label: 'S' },
    { x: 810, y: 540, labelX: 835, labelY: 570, label: 'W' },
    { x: 540, y: 540, labelX: 505, labelY: 570, label: 'N' },
];

const COLORS = {
    signalGreen: '#32D27A',
    signalYellow: '#FFC83D',
    signalRed: '#FF4646',
    text: '#e2e8f0',
    dim: '#64748b',
    ambulanceGlow: '#E040FB',
};

// ── Preload helper ───────────────────────────────────────────────────────────
function loadImage(src) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = () => resolve(null);
        img.src = src;
    });
}

export default function IntersectionCanvas({ state }) {
    const canvasRef = useRef(null);
    const spritesRef = useRef({});
    const [loaded, setLoaded] = useState(false);

    // Preload all sprites once
    useEffect(() => {
        (async () => {
            const entries = Object.entries(SPRITE_PATHS);
            const results = await Promise.all(entries.map(([, src]) => loadImage(src)));
            const sprites = {};
            entries.forEach(([key], i) => {
                sprites[key] = results[i];
            });
            spritesRef.current = sprites;
            setLoaded(true);
        })();
    }, []);

    // Canvas sizing
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const dpr = window.devicePixelRatio || 1;

        const resize = () => {
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = rect.width * dpr;
            canvas.height = (rect.width * 800 / 1400) * dpr;
            canvas.style.width = `${rect.width}px`;
            canvas.style.height = `${rect.width * 800 / 1400}px`;
        };
        resize();
        window.addEventListener('resize', resize);
        return () => window.removeEventListener('resize', resize);
    }, []);

    // Render loop
    useEffect(() => {
        if (!state || !loaded) return;
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        const W = 1400, H = 800;
        const scaleX = canvas.width / W;
        const scaleY = canvas.height / H;
        const sprites = spritesRef.current;

        ctx.save();
        ctx.scale(scaleX, scaleY);

        // ── Background ──────────────────────────────────────────────────────
        if (sprites.intersection) {
            ctx.drawImage(sprites.intersection, 0, 0, W, H);

            // Dim overlay for contrast
            ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
            ctx.fillRect(0, 0, W, H);
        } else {
            // Fallback: dark background
            ctx.fillStyle = '#1a1a2e';
            ctx.fillRect(0, 0, W, H);
            ctx.fillStyle = '#23233a';
            ctx.fillRect(0, 320, W, 200);
            ctx.fillRect(580, 0, 240, H);
        }

        // ── Vehicles ────────────────────────────────────────────────────────
        const vehicles = state.vehicles || [];
        for (const veh of vehicles) {
            const spriteImg = sprites[veh.type];
            const info = VEHICLE_SPRITES[veh.type] || { w: 48, h: 24 };
            const rotation = DIR_ROTATION[veh.dir] || 0;

            ctx.save();

            // Ambulance glow
            if (veh.isEmergency && !veh.crossed) {
                const pulse = 0.5 + 0.5 * Math.sin(Date.now() / 200);
                ctx.shadowColor = COLORS.ambulanceGlow;
                ctx.shadowBlur = 18 + pulse * 12;
            }

            const cx = veh.x + veh.w / 2;
            const cy = veh.y + veh.h / 2;

            if (spriteImg) {
                ctx.translate(cx, cy);
                ctx.rotate((rotation * Math.PI) / 180);

                // Draw the sprite image scaled to target size
                const drawW = info.w;
                const drawH = info.h;
                ctx.drawImage(spriteImg, -drawW / 2, -drawH / 2, drawW, drawH);
            } else {
                // Fallback: colored rectangle
                const typeColors = {
                    car: '#4A8CFF', bus: '#FF825A', truck: '#FF4646',
                    rickshaw: '#32D27A', bike: '#FFC83D', ambulance: '#E040FB',
                };
                ctx.translate(cx, cy);
                ctx.rotate((rotation * Math.PI) / 180);
                ctx.fillStyle = typeColors[veh.type] || '#4A8CFF';
                ctx.beginPath();
                ctx.roundRect(-info.w / 2, -info.h / 2, info.w, info.h, 3);
                ctx.fill();
            }

            ctx.restore();
        }

        // ── Traffic Signals ─────────────────────────────────────────────────
        const signals = state.signals || [];
        for (let i = 0; i < signals.length; i++) {
            const sig = signals[i];
            const pos = SIGNAL_POSITIONS[i];

            // Signal housing — tall dark rectangle
            ctx.fillStyle = 'rgba(10, 10, 20, 0.85)';
            ctx.beginPath();
            ctx.roundRect(pos.x - 18, pos.y - 50, 36, 100, 8);
            ctx.fill();
            ctx.strokeStyle = 'rgba(255,255,255,0.08)';
            ctx.lineWidth = 1.5;
            ctx.stroke();

            // Inner border
            ctx.strokeStyle = 'rgba(255,255,255,0.04)';
            ctx.lineWidth = 0.5;
            ctx.beginPath();
            ctx.roundRect(pos.x - 15, pos.y - 47, 30, 94, 6);
            ctx.stroke();

            // Three lights with realistic rendering
            const lights = [
                { color: COLORS.signalRed, active: sig.state === 'red', cy: pos.y - 28 },
                { color: COLORS.signalYellow, active: sig.state === 'yellow', cy: pos.y },
                { color: COLORS.signalGreen, active: sig.state === 'green', cy: pos.y + 28 },
            ];

            for (const light of lights) {
                // Light housing (dark circle)
                ctx.beginPath();
                ctx.arc(pos.x, light.cy, 11, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(20, 20, 30, 0.9)';
                ctx.fill();

                // Light
                ctx.beginPath();
                ctx.arc(pos.x, light.cy, 9, 0, Math.PI * 2);
                if (light.active) {
                    // Radial gradient for realistic light
                    const grad = ctx.createRadialGradient(pos.x - 2, light.cy - 2, 0, pos.x, light.cy, 10);
                    grad.addColorStop(0, '#fff');
                    grad.addColorStop(0.3, light.color);
                    grad.addColorStop(1, light.color);
                    ctx.fillStyle = grad;
                    ctx.shadowColor = light.color;
                    ctx.shadowBlur = 20;
                } else {
                    ctx.fillStyle = 'rgba(40, 40, 50, 0.7)';
                    ctx.shadowBlur = 0;
                }
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            // Timer text below signal
            ctx.font = 'bold 18px "Inter", "SF Mono", monospace';
            ctx.textAlign = 'center';
            const timerColor = sig.state === 'green' ? COLORS.signalGreen :
                sig.state === 'yellow' ? COLORS.signalYellow :
                    COLORS.signalRed;
            // Timer background pill
            ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
            ctx.beginPath();
            ctx.roundRect(pos.x - 24, pos.y + 55, 48, 22, 4);
            ctx.fill();
            ctx.fillStyle = timerColor;
            // Show EMG/WAIT during emergency like simulation.py
            let timerLabel = `${sig.timer}`;
            if (state.emergency?.active) {
                const emDir = state.emergency.direction;
                const dirs = ['right', 'down', 'left', 'up'];
                if (dirs[i] === emDir) {
                    timerLabel = 'EMG';
                    ctx.fillStyle = COLORS.signalGreen;
                } else if (sig.state === 'red') {
                    timerLabel = 'WAIT';
                }
            }
            ctx.fillText(timerLabel, pos.x, pos.y + 72);

            // Direction label
            ctx.font = 'bold 11px Inter, sans-serif';
            ctx.fillStyle = 'rgba(255,255,255,0.5)';
            ctx.fillText(pos.label, pos.x, pos.y - 58);
            ctx.textAlign = 'start';
        }

        // ── Emergency overlay ───────────────────────────────────────────────
        if (state.emergency?.active) {
            const pulse = 0.4 + 0.6 * Math.sin(Date.now() / 300);
            // Red vignette
            const vignette = ctx.createRadialGradient(W / 2, H / 2, 200, W / 2, H / 2, 700);
            vignette.addColorStop(0, 'rgba(255,0,0,0)');
            vignette.addColorStop(1, `rgba(255,0,0,${0.08 * pulse})`);
            ctx.fillStyle = vignette;
            ctx.fillRect(0, 0, W, H);

            // Emergency banner
            ctx.fillStyle = `rgba(255,20,20,${0.8 * pulse})`;
            ctx.beginPath();
            ctx.roundRect(W / 2 - 200, 8, 400, 36, 8);
            ctx.fill();
            ctx.strokeStyle = `rgba(255,100,100,${0.5 * pulse})`;
            ctx.lineWidth = 1;
            ctx.stroke();
            ctx.font = 'bold 14px Inter, sans-serif';
            ctx.fillStyle = '#fff';
            ctx.textAlign = 'center';
            ctx.fillText(`🚨 EMERGENCY — ${state.emergency.direction?.toUpperCase()}`, W / 2, 32);
            ctx.textAlign = 'start';
        }

        // ── Vehicle count badges on approaches ──────────────────────────────
        const waiting = state.waiting || {};
        const badgePositions = {
            right: [470, 395], down: [730, 275], left: [830, 460], up: [615, 560],
        };
        ctx.font = 'bold 13px Inter, sans-serif';
        for (const d of ['right', 'down', 'left', 'up']) {
            const [bx, by] = badgePositions[d];
            const count = waiting[d] || 0;
            // Badge background
            ctx.fillStyle = count > 10 ? 'rgba(255,70,70,0.8)' :
                count > 5 ? 'rgba(255,200,60,0.8)' :
                    'rgba(50,210,122,0.8)';
            ctx.beginPath();
            ctx.arc(bx, by, 14, 0, Math.PI * 2);
            ctx.fill();
            // Badge text
            ctx.fillStyle = count > 5 ? '#000' : '#fff';
            ctx.textAlign = 'center';
            ctx.fillText(count, bx, by + 5);
            ctx.textAlign = 'start';
        }

        // ── Timestamp watermark ─────────────────────────────────────────────
        ctx.font = '11px "SF Mono", monospace';
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.fillText(`SIM T+${state.time || 0}s`, 12, H - 10);

        ctx.restore();
    }, [state, loaded]);

    return (
        <div className="intersection-canvas-wrapper">
            {!loaded && (
                <div style={{
                    position: 'absolute', inset: 0, display: 'flex',
                    alignItems: 'center', justifyContent: 'center',
                    color: 'var(--text-dim)', fontSize: 13,
                }}>
                    Loading simulation assets...
                </div>
            )}
            <canvas ref={canvasRef} />
        </div>
    );
}
