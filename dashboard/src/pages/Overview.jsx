import KpiCard from '../components/KpiCard';
import ChartCard from '../components/ChartCard';
import { kpis, experimentData, vehicleTimeSeries, aiMetricsPerDirection, directionColors } from '../data/trafficData';
import {
    AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Cell
} from 'recharts';
import { motion } from 'framer-motion';
import { MdSmartToy, MdVisibility, MdSpeed, MdAir, MdSyncAlt, MdLocalHospital } from 'react-icons/md';

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="custom-tooltip">
            <p className="tooltip-label">{label}</p>
            {payload.map((p, i) => (
                <p key={i} style={{ color: p.color }}>
                    {p.name}: <strong>{p.value}</strong>
                </p>
            ))}
        </div>
    );
};

const features = [
    { icon: <MdVisibility />, title: 'YOLO Detection', desc: 'Real-time vehicle counting with YOLOv3', color: '#4A8CFF' },
    { icon: <MdSmartToy />, title: 'AI Signal Control', desc: 'Adaptive green-time optimization', color: '#34D399' },
    { icon: <MdLocalHospital />, title: 'Emergency Corridor', desc: 'Priority passage for ambulances', color: '#F87171' },
    { icon: <MdAir />, title: 'Pollution Tracking', desc: 'CO₂ monitoring & signal adjustment', color: '#FBBF24' },
    { icon: <MdSpeed />, title: 'Throughput Boost', desc: `${kpis.improvement}% faster than manual`, color: '#FB923C' },
    { icon: <MdSyncAlt />, title: 'Junction Sync', desc: 'Green-wave coordination', color: '#C084FC' },
];

export default function Overview() {
    const throughputData = experimentData.map(d => ({
        exp: `E${d.exp}`,
        yolo: d.total,
        manual: d.manual,
    }));

    return (
        <motion.div
            className="page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <div className="page-header">
                <h1 className="page-title">Dashboard Overview</h1>
                <p className="page-subtitle">AI-Powered Smart Traffic Management System — Real-time Analytics</p>
            </div>

            {/* Feature Highlights */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '12px',
                marginBottom: '28px'
            }}>
                {features.map((f, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.06 }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '14px 16px',
                            background: 'rgba(17, 24, 40, 0.6)',
                            backdropFilter: 'blur(12px)',
                            border: '1px solid rgba(255,255,255,0.06)',
                            borderRadius: '12px',
                            cursor: 'default',
                        }}
                    >
                        <div style={{
                            width: '38px',
                            height: '38px',
                            borderRadius: '10px',
                            background: `${f.color}12`,
                            color: f.color,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '18px',
                            flexShrink: 0,
                        }}>
                            {f.icon}
                        </div>
                        <div>
                            <div style={{ fontSize: '13px', fontWeight: 700, color: '#f0f4f8', letterSpacing: '-0.1px' }}>{f.title}</div>
                            <div style={{ fontSize: '11px', color: '#5a6884', marginTop: '1px' }}>{f.desc}</div>
                        </div>
                    </motion.div>
                ))}
            </div>

            {/* KPI Cards */}
            <div className="kpi-grid">
                <KpiCard
                    icon="📊"
                    label="Experiments"
                    value={kpis.totalExperiments}
                    color="#4A8CFF"
                    delay={0}
                />
                <KpiCard
                    icon="🚗"
                    label="Avg YOLO Throughput"
                    value={kpis.avgYoloTotal}
                    suffix=" veh"
                    color="#34D399"
                    delay={100}
                />
                <KpiCard
                    icon="📈"
                    label="AI Improvement"
                    value={kpis.improvement}
                    suffix="%"
                    color="#FBBF24"
                    delay={200}
                />
                <KpiCard
                    icon="⚡"
                    label="Throughput / sec"
                    value={kpis.avgThroughput}
                    suffix=" v/s"
                    color="#C084FC"
                    delay={300}
                />
                <KpiCard
                    icon="🌿"
                    label="Avg AQI"
                    value={kpis.totalAQI}
                    color="#34D399"
                    delay={400}
                />
                <KpiCard
                    icon="🔗"
                    label="Junction Sync"
                    value={kpis.syncScore}
                    suffix="%"
                    color="#4A8CFF"
                    delay={500}
                />
            </div>

            {/* Charts Row */}
            <div className="chart-grid-2">
                <ChartCard title="Throughput Comparison" subtitle="YOLO AI vs Manual control per experiment">
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={throughputData} barGap={2}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="exp" stroke="#5a6884" fontSize={12} />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="yolo" name="YOLO AI" fill="#4A8CFF" radius={[5, 5, 0, 0]} />
                            <Bar dataKey="manual" name="Manual" fill="#F87171" radius={[5, 5, 0, 0]} opacity={0.7} />
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Vehicle Detection Timeline" subtitle="YOLO real-time detection counts">
                    <ResponsiveContainer width="100%" height={280}>
                        <AreaChart data={vehicleTimeSeries.slice(0, 40)}>
                            <defs>
                                <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#4A8CFF" stopOpacity={0.35} />
                                    <stop offset="95%" stopColor="#4A8CFF" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="time" stroke="#5a6884" fontSize={12} unit="s" />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Area
                                type="monotone"
                                dataKey="count"
                                name="Vehicles"
                                stroke="#4A8CFF"
                                fill="url(#colorCount)"
                                strokeWidth={2.5}
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>

            {/* Direction Performance */}
            <div className="chart-grid-1">
                <ChartCard title="Per-Direction AI Performance" subtitle="Current AI scores across all directions">
                    <ResponsiveContainer width="100%" height={260}>
                        <BarChart data={aiMetricsPerDirection} layout="vertical" barSize={20}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                            <XAxis type="number" stroke="#5a6884" fontSize={12} />
                            <YAxis dataKey="direction" type="category" stroke="#5a6884" fontSize={13} width={55} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="aiScore" name="AI Score" radius={[0, 6, 6, 0]}>
                                {aiMetricsPerDirection.map((entry) => (
                                    <Cell key={entry.direction} fill={directionColors[entry.direction]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>
        </motion.div>
    );
}
