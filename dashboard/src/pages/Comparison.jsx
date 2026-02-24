import ChartCard from '../components/ChartCard';
import KpiCard from '../components/KpiCard';
import { experimentData, kpis } from '../data/trafficData';
import {
    BarChart, Bar, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    Legend, Cell, ReferenceLine
} from 'recharts';
import { motion } from 'framer-motion';

const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload?.length) return null;
    return (
        <div className="custom-tooltip">
            <p className="tooltip-label">{label}</p>
            {payload.map((p, i) => (
                <p key={i} style={{ color: p.color || p.stroke || p.fill }}>
                    {p.name}: <strong>{p.value}{p.name === 'Improvement' ? '%' : ''}</strong>
                </p>
            ))}
        </div>
    );
};

export default function Comparison() {
    const comparisonData = experimentData.map(d => ({
        exp: `Exp ${d.exp}`,
        YOLO: d.total,
        Manual: d.manual,
        Improvement: +(((d.total - d.manual) / d.manual) * 100).toFixed(1),
    }));

    let yoloCum = 0, manualCum = 0;
    const cumulativeData = experimentData.map(d => {
        yoloCum += d.total;
        manualCum += d.manual;
        return {
            exp: `E${d.exp}`,
            YOLO: yoloCum,
            Manual: manualCum,
            Gap: yoloCum - manualCum,
        };
    });

    const avgImprovement = +(comparisonData.reduce((s, d) => s + d.Improvement, 0) / comparisonData.length).toFixed(1);
    const maxImprovement = Math.max(...comparisonData.map(d => d.Improvement));
    const totalYolo = experimentData.reduce((s, d) => s + d.total, 0);
    const totalManual = experimentData.reduce((s, d) => s + d.manual, 0);

    return (
        <motion.div
            className="page"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
        >
            <div className="page-header">
                <h1 className="page-title">YOLO vs Manual</h1>
                <p className="page-subtitle">Comprehensive comparison of AI-driven vs manual traffic control</p>
            </div>

            <div className="kpi-grid kpi-grid-4">
                <KpiCard icon="🤖" label="Total YOLO" value={totalYolo} suffix=" veh" color="#4A8CFF" delay={0} />
                <KpiCard icon="👤" label="Total Manual" value={totalManual} suffix=" veh" color="#F87171" delay={100} />
                <KpiCard icon="📈" label="Avg Improvement" value={avgImprovement} suffix="%" color="#34D399" delay={200} />
                <KpiCard icon="🏆" label="Best Improvement" value={maxImprovement} suffix="%" color="#FBBF24" delay={300} />
            </div>

            <div className="chart-grid-2">
                <ChartCard title="Side-by-Side Comparison" subtitle="YOLO AI vs Manual vehicle counts per experiment">
                    <ResponsiveContainer width="100%" height={320}>
                        <BarChart data={comparisonData} barGap={4}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="exp" stroke="#5a6884" fontSize={11} angle={-30} textAnchor="end" height={50} />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ color: '#94a3b8' }} />
                            <Bar dataKey="YOLO" fill="#4A8CFF" radius={[5, 5, 0, 0]} />
                            <Bar dataKey="Manual" fill="#F87171" radius={[5, 5, 0, 0]} opacity={0.7} />
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Improvement %" subtitle="Percentage improvement of YOLO over Manual per experiment">
                    <ResponsiveContainer width="100%" height={320}>
                        <BarChart data={comparisonData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="exp" stroke="#5a6884" fontSize={11} angle={-30} textAnchor="end" height={50} />
                            <YAxis stroke="#5a6884" fontSize={12} unit="%" />
                            <Tooltip content={<CustomTooltip />} />
                            <ReferenceLine y={avgImprovement} stroke="#FBBF24" strokeDasharray="5 5" label={{ value: `Avg: ${avgImprovement}%`, fill: '#FBBF24', fontSize: 11 }} />
                            <Bar dataKey="Improvement" name="Improvement" radius={[5, 5, 0, 0]}>
                                {comparisonData.map((d, i) => (
                                    <Cell key={i} fill={d.Improvement > avgImprovement ? '#34D399' : '#FB923C'} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </ChartCard>
            </div>

            <div className="chart-grid-2">
                <ChartCard title="Cumulative Throughput" subtitle="Running total of vehicles passed over all experiments">
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={cumulativeData}>
                            <defs>
                                <linearGradient id="colorYolo" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#4A8CFF" stopOpacity={0.25} />
                                    <stop offset="95%" stopColor="#4A8CFF" stopOpacity={0} />
                                </linearGradient>
                                <linearGradient id="colorManual" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#F87171" stopOpacity={0.25} />
                                    <stop offset="95%" stopColor="#F87171" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                            <XAxis dataKey="exp" stroke="#5a6884" fontSize={12} />
                            <YAxis stroke="#5a6884" fontSize={12} />
                            <Tooltip content={<CustomTooltip />} />
                            <Legend wrapperStyle={{ color: '#94a3b8' }} />
                            <Area type="monotone" dataKey="YOLO" stroke="#4A8CFF" fill="url(#colorYolo)" strokeWidth={2.5} />
                            <Area type="monotone" dataKey="Manual" stroke="#F87171" fill="url(#colorManual)" strokeWidth={2.5} />
                        </AreaChart>
                    </ResponsiveContainer>
                </ChartCard>

                <ChartCard title="Summary Statistics" subtitle="Key metrics comparison">
                    <div className="stats-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th style={{ color: '#4A8CFF' }}>YOLO AI</th>
                                    <th style={{ color: '#F87171' }}>Manual</th>
                                    <th style={{ color: '#34D399' }}>Diff</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>Total Vehicles</td>
                                    <td className="val-blue">{totalYolo}</td>
                                    <td className="val-red">{totalManual}</td>
                                    <td className="val-green">+{totalYolo - totalManual}</td>
                                </tr>
                                <tr>
                                    <td>Average / Exp</td>
                                    <td className="val-blue">{kpis.avgYoloTotal}</td>
                                    <td className="val-red">{kpis.avgManualTotal}</td>
                                    <td className="val-green">+{kpis.avgYoloTotal - kpis.avgManualTotal}</td>
                                </tr>
                                <tr>
                                    <td>Best Experiment</td>
                                    <td className="val-blue">E{kpis.bestExp} ({kpis.bestExpTotal})</td>
                                    <td className="val-red">-</td>
                                    <td className="val-green">-</td>
                                </tr>
                                <tr>
                                    <td>Throughput / sec</td>
                                    <td className="val-blue">{kpis.avgThroughput}</td>
                                    <td className="val-red">{(kpis.avgManualTotal / 300).toFixed(2)}</td>
                                    <td className="val-green">+{(kpis.avgThroughput - kpis.avgManualTotal / 300).toFixed(2)}</td>
                                </tr>
                                <tr>
                                    <td>Avg Improvement</td>
                                    <td colSpan={2} style={{ textAlign: 'center', color: '#5a6884' }}>-</td>
                                    <td className="val-green">+{avgImprovement}%</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </ChartCard>
            </div>
        </motion.div>
    );
}
