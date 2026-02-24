import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function KpiCard({ icon, label, value, suffix = '', color = '#4A8CFF', delay = 0 }) {
    const [displayValue, setDisplayValue] = useState(0);
    const numericValue = typeof value === 'number' ? value : parseFloat(value) || 0;
    const isDecimal = String(value).includes('.');

    useEffect(() => {
        let start = 0;
        const duration = 1200;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            start = numericValue * eased;
            setDisplayValue(start);
            if (progress < 1) requestAnimationFrame(animate);
        };

        const timer = setTimeout(() => requestAnimationFrame(animate), delay);
        return () => clearTimeout(timer);
    }, [numericValue, delay]);

    return (
        <motion.div
            className="kpi-card"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: delay / 1000 }}
            whileHover={{ y: -4, transition: { duration: 0.2 } }}
            style={{ '--kpi-color': color }}
        >
            <div className="kpi-icon-wrapper" style={{ background: `${color}18` }}>
                <span className="kpi-icon" style={{ color }}>{icon}</span>
            </div>
            <div className="kpi-content">
                <p className="kpi-label">{label}</p>
                <h2 className="kpi-value" style={{ color }}>
                    {isDecimal ? displayValue.toFixed(1) : Math.round(displayValue)}
                    <span className="kpi-suffix">{suffix}</span>
                </h2>
            </div>
            <div className="kpi-glow" style={{ background: color }} />
        </motion.div>
    );
}
