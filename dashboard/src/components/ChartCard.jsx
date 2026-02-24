import { motion } from 'framer-motion';

export default function ChartCard({ title, subtitle, children, className = '' }) {
    return (
        <motion.div
            className={`chart-card ${className}`}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
        >
            <div className="chart-card-header">
                <h3 className="chart-card-title">{title}</h3>
                {subtitle && <p className="chart-card-subtitle">{subtitle}</p>}
            </div>
            <div className="chart-card-body">
                {children}
            </div>
        </motion.div>
    );
}
