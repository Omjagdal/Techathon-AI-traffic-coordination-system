import ChartCard from '../components/ChartCard';
import KpiCard from '../components/KpiCard';
import {
    aiMetricsPerDirection, aiScoreTrends, co2Trends, aiWeights,
    emissionRates, directionColors, signalConfig
} from '../data/trafficData';
import {
    LineChart, Line, BarChart, Bar, RadarChart, Radar, PolarGrid,
    PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid,
    Tooltip, ResponsiveContainer, Legend, Cell
} from 'recharts';
import { motion } from 'framer-motion';

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="custom-tooltip">
            <p className="tooltip-label">{label}</p>
            {payload.map((p, i) => (
                <p key={i} style={{ color: p.color || p.stroke }}>
                    {p.name}: <strong>{p.value}</strong>
                </p>
            ))}
        </div>
    );
};

export default function AiPerformance() {
    const totalCO2 = aiMetricsPerDirection.reduce((s, d) => s + d.co2, 0);
    const avgScore = +(aiMetricsPerDirection.reduce((s, d) => s + d.aiScore, 0) / 4).toFixed(1);
    const maxWait = Math.max(...aiMetricsPerDirection.map(d => d.waitTime));

    return (
        <motion.div
            className="page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <div className="page-header">
                <h1 className="page-title">AI Performance</h1>
                <p className="page-subtitle">Adaptive timing, pollution tracking, and scoring analytics</p>
            </div>

            <div className="kpi-grid kpi-grid-4">
                <KpiCard icon="🧠" label="Avg AI Score" value={avgScore} color="#4A8CFF" delay={0} />
                <KpiCard icon="💨" label="Total CO₂" value={totalCO2} suffix=" units" color="#FB923C" delay={100} />
                <KpiCard icon="⏳" label="Max Wait" value={maxWait} suffix="s" color="#F87171" delay={200} />
                <KpiCard icon="🎯" label="Pollution Threshold" value={signalConfig.pollutionThreshold} color="#34D399" delay={300} />
            </div>

            <div className="chart-grid-2">
                <ChartCard title="AI Score Trends" subtitle="Per-direction AI decision scores over 20 cycles">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={aiScoreTrends}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="cycle" stroke="#5a6884" fontSize={12} label={{ value: 'Cycle', position: 'insideBottom', offset: -5, fill: '#5a6884' }} />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ color: '#94a3b8' }} />
                            {Object.entries(directionColors).map(([dir, color]) => (
                                <Line key={dir} type="monotone" dataKey={dir} stroke={color} strokeWidth={2.5} dot={{ r: 2, fill: color }} />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="CO₂ Emission Trends" subtitle="Per-direction pollution levels over cycles">
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={co2Trends}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="cycle" stroke="#5a6884" fontSize={12} />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ color: '#94a3b8' }} />
                            {Object.entries(directionColors).map(([dir, color]) => (
                                <Line key={dir} type="monotone" dataKey={dir} stroke={color} strokeWidth={2.5} dot={{ r: 2, fill: color }} strokeDasharray={dir === 'Right' ? '' : '5 5'} />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>

            <div className="chart-grid-2">
                <ChartCard title="AI Weights Radar" subtitle="Decision factor importance from ai_config.py">
                    <ResponsiveContainer width="100%" height={300}>
                        <RadarChart data={aiWeights} cx="50%" cy="50%" outerRadius="70%">
                            <PolarGrid stroke="rgba(255,255,255,0.06)" />
                            <PolarAngleAxis dataKey="factor" stroke="#94a3b8" fontSize={11} />
                            <PolarRadiusAxis angle={18} domain={[0, 0.5]} stroke="#5a6884" fontSize={10} />
                            <Radar name="Weight" dataKey="weight" stroke="#4A8CFF" fill="#4A8CFF" fillOpacity={0.25} strokeWidth={2.5} />
                        </RadarChart>
                    </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Emission Rates by Vehicle" subtitle="CO₂ units per vehicle type">
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={emissionRates} layout="vertical" barSize={22}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" horizontal={false} />
                            <XAxis type="number" stroke="#5a6884" fontSize={12} />
                            <YAxis dataKey="type" type="category" stroke="#5a6884" fontSize={12} width={70} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="rate" name="CO₂ Rate" radius={[0, 6, 6, 0]}>
                                {emissionRates.map((entry, i) => (
                                    <Cell key={i} fill={entry.color} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>

            <div className="chart-grid-1">
                <ChartCard title="Signal Configuration" subtitle="Current AI system parameters">
                    <div className="config-grid">
                        {Object.entries(signalConfig).map(([key, val]) => (
                            <motion.div
                                key={key}
                                className="config-item"
                                whileHover={{ scale: 1.02 }}
                            >
                                <span className="config-label">{key.replace(/([A-Z])/g, ' $1').replace('default ', '').trim()}</span>
                                <span className="config-value">{val}{key.includes('Threshold') ? ' units' : key.includes('Time') ? 's' : 's'}</span>
                            </motion.div>
                        ))}
                    </div>
                </ChartCard>
            </div>
        </motion.div>
    );
}
