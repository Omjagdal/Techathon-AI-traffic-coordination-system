import { motion, AnimatePresence } from 'framer-motion';
import IntersectionCanvas from '../components/IntersectionCanvas';
import useSimulation from '../hooks/useSimulation';
import {
    MdCircle, MdLocalHospital, MdAir, MdSpeed, MdTimeline,
    MdRefresh, MdWifi, MdWifiOff, MdArrowForward, MdArrowDownward,
    MdArrowBack, MdArrowUpward, MdWarning, MdAccessTime,
} from 'react-icons/md';

const DIR_ARROWS = {
    right: { icon: MdArrowForward, label: 'EAST', color: '#FB923C' },
    down: { icon: MdArrowDownward, label: 'SOUTH', color: '#4A8CFF' },
    left: { icon: MdArrowBack, label: 'WEST', color: '#34D399' },
    up: { icon: MdArrowUpward, label: 'NORTH', color: '#FBBF24' },
};

const SIGNAL_COLORS = { green: '#34D399', yellow: '#FBBF24', red: '#F87171' };
const MODE_COLORS = { NORMAL: '#34D399', EMERGENCY: '#F87171', POLLUTION_ALERT: '#FBBF24' };

function SignalIndicator({ signal, direction, index, currentGreen }) {
    const info = DIR_ARROWS[direction];
    const color = SIGNAL_COLORS[signal.state];
    const isActive = index === currentGreen;

    return (
        <div className={`ldb-signal ${isActive ? 'active' : ''}`}>
            <div className="ldb-signal-light" style={{ backgroundColor: color, boxShadow: `0 0 12px ${color}` }} />
            <div className="ldb-signal-info">
                <span className="ldb-signal-dir" style={{ color: info.color }}>{info.label}</span>
                <span className="ldb-signal-timer" style={{ color }}>{signal.timer}s</span>
            </div>
        </div>
    );
}

function AiDirectionCard({ direction, ai, waiting, crossed }) {
    const info = DIR_ARROWS[direction];
    const Icon = info.icon;
    const score = ai?.scores?.[direction] || 0;
    const wait = ai?.waitTimes?.[direction] || 0;
    const pollution = ai?.pollution?.[direction] || 0;

    return (
        <motion.div
            className="ldb-ai-card"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ '--dir-color': info.color }}
        >
            <div className="ldb-ai-card-header">
                <Icon style={{ color: info.color, fontSize: 18 }} />
                <span className="ldb-ai-card-label" style={{ color: info.color }}>{info.label}</span>
                <span className="ldb-ai-card-score">{score}</span>
            </div>
            <div className="ldb-ai-card-metrics">
                <div className="ldb-ai-metric">
                    <span className="ldb-ai-metric-label">Waiting</span>
                    <span className="ldb-ai-metric-value" style={{ color: (waiting || 0) > 10 ? '#F87171' : '#f0f4f8' }}>
                        {waiting || 0}
                    </span>
                </div>
                <div className="ldb-ai-metric">
                    <span className="ldb-ai-metric-label">Crossed</span>
                    <span className="ldb-ai-metric-value">{crossed || 0}</span>
                </div>
                <div className="ldb-ai-metric">
                    <span className="ldb-ai-metric-label">Wait</span>
                    <span className="ldb-ai-metric-value">{wait}s</span>
                </div>
                <div className="ldb-ai-metric">
                    <span className="ldb-ai-metric-label">CO₂</span>
                    <span className="ldb-ai-metric-value" style={{ color: pollution > 30 ? '#F87171' : pollution > 15 ? '#FBBF24' : '#34D399' }}>
                        {pollution}
                    </span>
                </div>
            </div>
        </motion.div>
    );
}

export default function LiveDashboard() {
    const { state, connected, spawnAmbulance, resetSimulation } = useSimulation();
    const ai = state?.ai;
    const emergency = state?.emergency;

    return (
        <motion.div
            className="page ldb-page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            {/* ── Top status bar ────────────────────────────────────────── */}
            <div className="ldb-topbar">
                <div className="ldb-topbar-left">
                    <h1 className="ldb-title">🏙️ Smart City Control Room</h1>
                    <div className={`ldb-connection ${connected ? 'on' : 'off'}`}>
                        {connected ? <MdWifi /> : <MdWifiOff />}
                        <span>{connected ? 'LIVE' : 'OFFLINE'}</span>
                    </div>
                </div>
                <div className="ldb-topbar-right">
                    <div className="ldb-stat">
                        <MdAccessTime />
                        <span>{state?.time || 0}s</span>
                    </div>
                    <div className="ldb-stat">
                        <span className="ldb-stat-label">MODE</span>
                        <span className="ldb-stat-value" style={{ color: MODE_COLORS[ai?.mode] || '#34D399' }}>
                            {ai?.mode || 'NORMAL'}
                        </span>
                    </div>
                    <div className="ldb-stat">
                        <MdAir />
                        <span style={{ color: (ai?.aqi || 0) > 30 ? '#F87171' : (ai?.aqi || 0) > 15 ? '#FBBF24' : '#34D399' }}>
                            AQI {ai?.aqi || 0}
                        </span>
                    </div>
                    <div className="ldb-stat">
                        <MdSpeed />
                        <span>{state?.throughput || 0} v/s</span>
                    </div>
                    <div className="ldb-stat highlight">
                        <span>{state?.totalCrossed || 0}</span>
                        <span className="ldb-stat-label">passed</span>
                    </div>
                </div>
            </div>

            {/* ── Emergency alert ───────────────────────────────────────── */}
            <AnimatePresence>
                {emergency?.active && (
                    <motion.div
                        className="ldb-emergency-bar"
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                    >
                        <MdWarning className="ldb-emergency-icon" />
                        <span>EMERGENCY GREEN CORRIDOR — {emergency.direction?.toUpperCase()}</span>
                        <span className="ldb-emergency-queue">Queue: {emergency.queueLength} | Served: {emergency.served}</span>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* ── BIG Canvas — Full Width ──────────────────────────────── */}
            <div className="ldb-canvas-panel ldb-canvas-fullwidth">
                <div className="ldb-canvas-header">
                    <span>Live Intersection Feed</span>
                    <div className="ldb-canvas-header-right">
                        <span className="ldb-canvas-label">Real-time • 30 FPS</span>
                        <div className="ldb-live-dot" />
                    </div>
                </div>
                <IntersectionCanvas state={state} />
            </div>

            {/* ── Dashboard panels below ──────────────────────────────── */}
            <div className="ldb-bottom-panels">
                {/* Signals row */}
                <div className="ldb-section">
                    <h3 className="ldb-section-title"><MdTimeline /> Signal Status</h3>
                    <div className="ldb-signals-grid">
                        {state?.signals?.map((sig, i) => (
                            <SignalIndicator
                                key={i}
                                signal={sig}
                                direction={['right', 'down', 'left', 'up'][i]}
                                index={i}
                                currentGreen={state.currentGreen}
                            />
                        ))}
                    </div>
                </div>

                {/* AI + Junction + Controls row */}
                <div className="ldb-section">
                    <h3 className="ldb-section-title"><MdSpeed /> AI Decisions</h3>
                    <div className="ldb-ai-grid">
                        {['right', 'down', 'left', 'up'].map(d => (
                            <AiDirectionCard
                                key={d}
                                direction={d}
                                ai={ai}
                                waiting={state?.waiting?.[d]}
                                crossed={state?.crossed?.[d]}
                            />
                        ))}
                    </div>
                </div>

                {/* Controls + Junction + Events */}
                <div className="ldb-bottom-row">
                    <div className="ldb-section ldb-section-compact">
                        <div className="ldb-junction-card">
                            <span className="ldb-junction-label">Junction Sync</span>
                            <span className={`ldb-junction-status ${state?.junction?.synced ? 'synced' : 'desynced'}`}>
                                {state?.junction?.synced ? 'SYNCED' : 'DESYNCED'}
                            </span>
                            <span className="ldb-junction-score">{state?.junction?.score || 0}/100</span>
                        </div>
                    </div>

                    <div className="ldb-section ldb-section-compact">
                        <h3 className="ldb-section-title"><MdLocalHospital /> Spawn Ambulance</h3>
                        <div className="ldb-controls">
                            {[0, 1, 2, 3].map(i => {
                                const d = ['right', 'down', 'left', 'up'][i];
                                const info = DIR_ARROWS[d];
                                const Icon = info.icon;
                                return (
                                    <button
                                        key={i}
                                        className="ldb-spawn-btn"
                                        onClick={() => spawnAmbulance(i)}
                                        style={{ '--btn-color': info.color }}
                                    >
                                        <Icon />
                                        <span>{info.label}</span>
                                    </button>
                                );
                            })}
                            <button className="ldb-reset-btn" onClick={resetSimulation}>
                                <MdRefresh /> Reset
                            </button>
                        </div>
                    </div>

                    <div className="ldb-section ldb-section-compact">
                        <h3 className="ldb-section-title">📋 Event Log</h3>
                        <div className="ldb-events">
                            {(state?.events || []).slice().reverse().map((evt, i) => (
                                <div key={i} className={`ldb-event ldb-event-${evt.type}`}>
                                    <span className="ldb-event-time">{evt.time}s</span>
                                    <span className="ldb-event-msg">{evt.message}</span>
                                </div>
                            ))}
                            {(!state?.events || state.events.length === 0) && (
                                <div className="ldb-event ldb-event-system">
                                    <span className="ldb-event-msg">Waiting for events...</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
}
