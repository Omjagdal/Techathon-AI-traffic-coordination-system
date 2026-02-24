import ChartCard from '../components/ChartCard';
import { experimentData } from '../data/trafficData';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Cell, LineChart, Line, Legend
} from 'recharts';
import { motion } from 'framer-motion';
import { useState } from 'react';

const laneColors = ['#4A8CFF', '#34D399', '#FBBF24', '#FB923C'];

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="custom-tooltip">
            <p className="tooltip-label">{label}</p>
            {payload.map((p, i) => (
                <p key={i} style={{ color: p.color || p.fill }}>
                    {p.name}: <strong>{p.value}</strong>
                </p>
            ))}
        </div>
    );
};

export default function SignalAnalysis() {
    const [selectedExp, setSelectedExp] = useState(null);

    const stackedData = experimentData.map(d => ({
        exp: `Exp ${d.exp}`,
        'Lane 1': d.lane1,
        'Lane 2': d.lane2,
        'Lane 3': d.lane3,
        'Lane 4': d.lane4,
    }));

    const trendData = experimentData.map(d => ({
        exp: `E${d.exp}`,
        'Lane 1': d.lane1,
        'Lane 2': d.lane2,
        'Lane 3': d.lane3,
        'Lane 4': d.lane4,
    }));

    const lanes = ['Lane 1', 'Lane 2', 'Lane 3', 'Lane 4'];
    const heatmapMax = Math.max(...experimentData.flatMap(d => [d.lane1, d.lane2, d.lane3, d.lane4]));

    const getHeatColor = (val) => {
        const pct = val / heatmapMax;
        if (pct > 0.75) return '#34D399';
        if (pct > 0.5) return '#4A8CFF';
        if (pct > 0.25) return '#FBBF24';
        return '#F87171';
    };

    return (
        <motion.div
            className="page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <div className="page-header">
                <h1 className="page-title">Signal Analysis</h1>
                <p className="page-subtitle">Per-lane vehicle distribution and signal performance across experiments</p>
            </div>

            <div className="chart-grid-2">
                <ChartCard title="Lane Distribution" subtitle="Stacked vehicle counts per lane per experiment">
                    <ResponsiveContainer width="100%" height={320}>
                        <BarChart data={stackedData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="exp" stroke="#5a6884" fontSize={11} angle={-30} textAnchor="end" height={50} />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ color: '#94a3b8' }} />
                            {lanes.map((lane, i) => (
                                <Bar key={lane} dataKey={lane} stackId="a" fill={laneColors[i]} radius={i === 3 ? [5, 5, 0, 0] : [0, 0, 0, 0]} />
                            ))}
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Lane Trends" subtitle="Per-lane vehicle counts across experiments">
                    <ResponsiveContainer width="100%" height={320}>
                        <LineChart data={trendData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="exp" stroke="#5a6884" fontSize={12} />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ color: '#94a3b8' }} />
                            {lanes.map((lane, i) => (
                                <Line key={lane} type="monotone" dataKey={lane} stroke={laneColors[i]} strokeWidth={2.5} dot={{ r: 3, fill: laneColors[i] }} />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>

            {/* Heatmap */}
            <div className="chart-grid-1">
                <ChartCard title="Performance Heatmap" subtitle="Click a cell to view experiment details">
                    <div className="heatmap-container">
                        <div className="heatmap-header">
                            <div className="heatmap-label-spacer"></div>
                            {experimentData.map(d => (
                                <div key={d.exp} className="heatmap-col-label">E{d.exp}</div>
                            ))}
                        </div>
                        {lanes.map((lane, li) => (
                            <div key={lane} className="heatmap-row">
                                <div className="heatmap-row-label">{lane}</div>
                                {experimentData.map(d => {
                                    const val = [d.lane1, d.lane2, d.lane3, d.lane4][li];
                                    return (
                                        <motion.div
                                            key={`${d.exp}-${li}`}
                                            className={`heatmap-cell ${selectedExp === d.exp ? 'selected' : ''}`}
                                            style={{ backgroundColor: getHeatColor(val) + '30', color: getHeatColor(val) }}
                                            whileHover={{ scale: 1.1 }}
                                            onClick={() => setSelectedExp(d.exp === selectedExp ? null : d.exp)}
                                        >
                                            {val}
                                        </motion.div>
                                    );
                                })}
                            </div>
                        ))}
                    </div>

                    {selectedExp && (
                        <motion.div
                            className="experiment-detail"
                            initial={{ opacity: 0, height: 0 }}
                            animate={{ opacity: 1, height: 'auto' }}
                        >
                            {(() => {
                                const d = experimentData.find(e => e.exp === selectedExp);
                                const improvement = (((d.total - d.manual) / d.manual) * 100).toFixed(1);
                                return (
                                    <div className="experiment-detail-content">
                                        <h4>Experiment {d.exp} Details</h4>
                                        <div className="detail-grid">
                                            <div className="detail-item">
                                                <span className="detail-label">Lane 1</span>
                                                <span className="detail-value" style={{ color: laneColors[0] }}>{d.lane1}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">Lane 2</span>
                                                <span className="detail-value" style={{ color: laneColors[1] }}>{d.lane2}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">Lane 3</span>
                                                <span className="detail-value" style={{ color: laneColors[2] }}>{d.lane3}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">Lane 4</span>
                                                <span className="detail-value" style={{ color: laneColors[3] }}>{d.lane4}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">YOLO Total</span>
                                                <span className="detail-value" style={{ color: '#4A8CFF' }}>{d.total}</span>
                                            </div>
                                            <div className="detail-item">
                                                <span className="detail-label">Manual</span>
                                                <span className="detail-value" style={{ color: '#F87171' }}>{d.manual}</span>
                                            </div>
                                            <div className="detail-item span-2">
                                                <span className="detail-label">Improvement</span>
                                                <span className="detail-value" style={{ color: '#34D399' }}>+{improvement}%</span>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })()}
                        </motion.div>
                    )}
                </ChartCard>
            </div>
        </motion.div>
    );
}
