import ChartCard from '../components/ChartCard';
import KpiCard from '../components/KpiCard';
import { vehicleTimeSeriesWithAvg, countDistribution, vehicleTimeSeries } from '../data/trafficData';
import {
    AreaChart, Area, LineChart, Line, BarChart, Bar,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
    ReferenceLine
} from 'recharts';
import { motion } from 'framer-motion';

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="custom-tooltip">
            <p className="tooltip-label">{typeof label === 'number' ? `${label}s` : label}</p>
            {payload.map((p, i) => (
                <p key={i} style={{ color: p.color || p.stroke }}>
                    {p.name}: <strong>{p.value}</strong>
                </p>
            ))}
        </div>
    );
};

export default function VehicleDetection() {
    const maxCount = Math.max(...vehicleTimeSeries.map(d => d.count));
    const avgCount = +(vehicleTimeSeries.reduce((s, d) => s + d.count, 0) / vehicleTimeSeries.length).toFixed(1);
    const peakTime = vehicleTimeSeries.find(d => d.count === maxCount)?.time || 0;

    const peaks = vehicleTimeSeries.filter((d, i, arr) => {
        if (i === 0 || i === arr.length - 1) return false;
        return d.count > arr[i - 1].count && d.count > arr[i + 1].count && d.count >= 5;
    });

    return (
        <motion.div
            className="page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <div className="page-header">
                <h1 className="page-title">Vehicle Detection</h1>
                <p className="page-subtitle">YOLOv3-based real-time vehicle detection analytics</p>
            </div>

            <div className="kpi-grid kpi-grid-4">
                <KpiCard icon="🔍" label="Total Samples" value={vehicleTimeSeries.length} color="#4A8CFF" delay={0} />
                <KpiCard icon="📊" label="Avg Vehicles" value={avgCount} color="#34D399" delay={100} />
                <KpiCard icon="🔺" label="Peak Count" value={maxCount} color="#F87171" delay={200} />
                <KpiCard icon="⏱️" label="Peak Time" value={peakTime} suffix="s" color="#FBBF24" delay={300} />
            </div>

            <div className="chart-grid-1">
                <ChartCard title="Detection Timeline with Rolling Averages" subtitle="Smoothed vehicle counts with 10s and 20s moving averages">
                    <ResponsiveContainer width="100%" height={350}>
                        <AreaChart data={vehicleTimeSeriesWithAvg}>
                            <defs>
                                <linearGradient id="colorRaw" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#4A8CFF" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#4A8CFF" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="time" stroke="#5a6884" fontSize={12} unit="s" />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ color: '#94a3b8' }} />
                            <ReferenceLine y={avgCount} stroke="#FB923C" strokeDasharray="5 5" label={{ value: `Avg: ${avgCount}`, fill: '#FB923C', fontSize: 11 }} />
                            <Area type="monotone" dataKey="count" name="Raw Count" stroke="#4A8CFF" fill="url(#colorRaw)" strokeWidth={1.5} dot={false} />
                            <Line type="monotone" dataKey="avg10" name="10s Avg" stroke="#34D399" strokeWidth={2} dot={false} />
                            <Line type="monotone" dataKey="avg20" name="20s Avg" stroke="#FBBF24" strokeWidth={2} dot={false} />
                        </AreaChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>

            <div className="chart-grid-2">
                <ChartCard title="Count Distribution" subtitle="Frequency of each vehicle count value">
                    <ResponsiveContainer width="100%" height={280}>
                        <BarChart data={countDistribution}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="count" stroke="#5a6884" fontSize={12} label={{ value: 'Vehicle Count', position: 'insideBottom', offset: -5, fill: '#5a6884' }} />
                            <YAxis stroke="#5a6884" fontSize={12} label={{ value: 'Frequency', angle: -90, position: 'insideLeft', fill: '#5a6884' }} />
                            <Tooltip content={<CustomTooltip />} />
                            <Bar dataKey="frequency" name="Frequency" fill="#C084FC" radius={[5, 5, 0, 0]}>
                                {countDistribution.map((_, i) => {
                                    const colors = ['#4A8CFF', '#34D399', '#FBBF24', '#FB923C', '#C084FC', '#F87171', '#22D3EE'];
                                    return <motion.rect key={i} fill={colors[i % colors.length]} />;
                                })}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Peak Detection" subtitle={`${peaks.length} peaks detected (count ≥ 5)`}>
                    <div className="peaks-list">
                        {peaks.length === 0 ? (
                            <p className="peaks-empty">No significant peaks detected</p>
                        ) : (
                            peaks.map((peak, i) => (
                                <motion.div
                                    key={i}
                                    className="peak-item"
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                >
                                    <div className="peak-badge" style={{ background: peak.count >= 7 ? '#F8717120' : peak.count >= 6 ? '#FBBF2420' : '#4A8CFF20' }}>
                                        <span style={{ color: peak.count >= 7 ? '#F87171' : peak.count >= 6 ? '#FBBF24' : '#4A8CFF' }}>
                                            {peak.count}
                                        </span>
                                    </div>
                                    <div className="peak-info">
                                        <span className="peak-time">{peak.time}s</span>
                                        <span className="peak-label">
                                            {peak.count >= 7 ? 'Critical' : peak.count >= 6 ? 'High' : 'Moderate'} congestion
                                        </span>
                                    </div>
                                </motion.div>
                            ))
                        )}
                    </div>
                </ChartCard>
            </div>
        </motion.div>
    );
}
