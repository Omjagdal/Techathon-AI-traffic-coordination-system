import ChartCard from '../components/ChartCard';
import { motion } from 'framer-motion';
import { MdPlayArrow, MdSpeed, MdLocalHospital, MdAir, MdSyncAlt } from 'react-icons/md';

const aiModules = [
    {
        icon: <MdSpeed />,
        title: 'Adaptive Signal Timing',
        color: '#4A8CFF',
        desc: 'AI dynamically adjusts green light duration based on real-time vehicle count, wait time, and queue length using a weighted scoring algorithm.',
    },
    {
        icon: <MdLocalHospital />,
        title: 'Emergency Green Corridor',
        color: '#F87171',
        desc: 'Automatically detects ambulances via YOLO and gives them priority passage by preempting all traffic signals.',
    },
    {
        icon: <MdAir />,
        title: 'Pollution-Aware Optimization',
        color: '#34D399',
        desc: 'Tracks CO₂ emissions from idling vehicles at each direction and optimizes signal timing to reduce overall pollution.',
    },
    {
        icon: <MdSyncAlt />,
        title: 'Junction Coordination',
        color: '#FBBF24',
        desc: 'Implements green-wave strategy to synchronize adjacent intersections for smoother city-wide traffic flow.',
    },
];

const vehicleTypes = [
    { type: 'Car', speed: 2.25, color: '#4A8CFF' },
    { type: 'Bus', speed: 1.8, color: '#FB923C' },
    { type: 'Truck', speed: 1.8, color: '#F87171' },
    { type: 'Rickshaw', speed: 2.0, color: '#34D399' },
    { type: 'Bike', speed: 2.5, color: '#FBBF24' },
    { type: 'Ambulance', speed: 3.5, color: '#C084FC' },
];

const flowSteps = [
    { step: 1, title: 'Green Phase', desc: 'Vehicles pass through. AI monitors queue length & pollution levels.', color: '#34D399' },
    { step: 2, title: 'Emergency Check', desc: 'YOLO scans for ambulances → activates green corridor if detected.', color: '#F87171' },
    { step: 3, title: 'AI Detection', desc: 'Runs YOLOv3 object detection to count vehicles for next signal decision.', color: '#4A8CFF' },
    { step: 4, title: 'Yellow Phase', desc: 'Transition period. System records throughput and wait-time stats.', color: '#FBBF24' },
    { step: 5, title: 'Signal Advance', desc: 'Advances to next direction based on AI scoring. Cycle repeats.', color: '#C084FC' },
];

export default function Simulation() {
    return (
        <motion.div
            className="page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <div className="page-header">
                <h1 className="page-title">How It Works</h1>
                <p className="page-subtitle">Architecture and AI modules of the Smart Traffic Management System</p>
            </div>

            {/* Launch Command */}
            <motion.div
                className="sim-launch-banner"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <div className="sim-launch-content">
                    <div className="sim-launch-icon"><MdPlayArrow /></div>
                    <div>
                        <h3 className="sim-launch-title">Run the Simulation</h3>
                        <p className="sim-launch-desc">Launch the Pygame window to see AI traffic management in real-time</p>
                    </div>
                </div>
                <code className="sim-launch-cmd">python3 simulation.py</code>
            </motion.div>

            {/* AI Modules */}
            <h2 style={{ color: 'var(--text-primary)', fontSize: '18px', fontWeight: 800, margin: '2rem 0 1rem', letterSpacing: '-0.3px' }}>🧠 AI Modules</h2>
            <div className="sim-modules-simple">
                {aiModules.map((mod, i) => (
                    <motion.div
                        key={i}
                        className="sim-module-simple"
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.08 }}
                        style={{ borderLeft: `3px solid ${mod.color}` }}
                    >
                        <div className="sim-module-simple-icon" style={{ color: mod.color, backgroundColor: `${mod.color}12` }}>
                            {mod.icon}
                        </div>
                        <div>
                            <h4 className="sim-module-simple-title">{mod.title}</h4>
                            <p className="sim-module-simple-desc">{mod.desc}</p>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* Two Column: Vehicle Types + Signal Flow */}
            <div className="chart-grid-2">
                <ChartCard title="Vehicle Types" subtitle="6 vehicle classes with different speeds">
                    <div className="sim-vehicle-list">
                        {vehicleTypes.map((v, i) => (
                            <motion.div
                                key={i}
                                className="sim-vehicle-row"
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.06 }}
                            >
                                <div className="sim-vehicle-dot" style={{ backgroundColor: v.color }} />
                                <span className="sim-vehicle-type">{v.type}</span>
                                <div style={{ flex: 1 }} />
                                <span className="sim-vehicle-stat" style={{ color: v.color, fontWeight: 700 }}>
                                    {v.speed}x
                                </span>
                                <div className="sim-vehicle-bar-bg" style={{ width: '40%' }}>
                                    <motion.div
                                        className="sim-vehicle-bar"
                                        style={{ backgroundColor: v.color }}
                                        initial={{ width: 0 }}
                                        animate={{ width: `${(v.speed / 3.5) * 100}%` }}
                                        transition={{ duration: 0.8, delay: i * 0.08 }}
                                    />
                                </div>
                            </motion.div>
                        ))}
                    </div>
                </ChartCard>

                <ChartCard title="Signal Cycle Flow" subtitle="How one traffic signal cycle works">
                    <div className="sim-flow-steps">
                        {flowSteps.map((s, i) => (
                            <motion.div
                                key={i}
                                className="sim-flow-step"
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.08 }}
                            >
                                <div className="sim-flow-number" style={{ backgroundColor: `${s.color}18`, color: s.color }}>
                                    {s.step}
                                </div>
                                <div className="sim-flow-content">
                                    <h5 className="sim-flow-title" style={{ color: s.color }}>{s.title}</h5>
                                    <p className="sim-flow-desc">{s.desc}</p>
                                </div>
                                {i < 4 && <div className="sim-flow-connector" />}
                            </motion.div>
                        ))}
                    </div>
                </ChartCard>
            </div>

            {/* Keyboard Controls */}
            <ChartCard title="Keyboard Controls" subtitle="Shortcuts during the Pygame simulation">
                <div className="sim-controls-grid">
                    {[
                        { key: '1', action: 'Spawn ambulance → RIGHT' },
                        { key: '2', action: 'Spawn ambulance → DOWN' },
                        { key: '3', action: 'Spawn ambulance → LEFT' },
                        { key: '4', action: 'Spawn ambulance → UP' },
                        { key: 'H', action: 'Toggle AI HUD panel' },
                    ].map(c => (
                        <div key={c.key} className="sim-control-item">
                            <kbd className="sim-key">{c.key}</kbd>
                            <span className="sim-control-desc">{c.action}</span>
                        </div>
                    ))}
                </div>
            </ChartCard>
        </motion.div>
    );
}
