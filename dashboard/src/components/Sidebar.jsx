import { NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
    MdDashboard,
    MdTraffic,
    MdDirectionsCar,
    MdPsychology,
    MdCompareArrows,
    MdVideogameAsset,
    MdSensors,
} from 'react-icons/md';

const navItems = [
    { to: '/', icon: MdDashboard, label: 'Overview' },
    { to: '/live', icon: MdSensors, label: 'Live Simulation' },
    { to: '/simulation', icon: MdVideogameAsset, label: 'How It Works' },
    { to: '/signals', icon: MdTraffic, label: 'Signal Analysis' },
    { to: '/detection', icon: MdDirectionsCar, label: 'Vehicle Detection' },
    { to: '/ai', icon: MdPsychology, label: 'AI Performance' },
    { to: '/comparison', icon: MdCompareArrows, label: 'YOLO vs Manual' },
];

export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <div className="sidebar-logo">🚦</div>
                <div>
                    <h1 className="sidebar-title">Smart Traffic AI</h1>
                    <p className="sidebar-subtitle">Intelligent Management System</p>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        className={({ isActive }) =>
                            `sidebar-link ${isActive ? 'active' : ''}`
                        }
                    >
                        {({ isActive }) => (
                            <motion.div
                                className="sidebar-link-inner"
                                whileHover={{ x: 4 }}
                                transition={{ type: 'spring', stiffness: 300 }}
                            >
                                {isActive && (
                                    <motion.div
                                        className="sidebar-active-indicator"
                                        layoutId="activeIndicator"
                                        transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                                    />
                                )}
                                <item.icon className="sidebar-icon" />
                                <span>{item.label}</span>
                            </motion.div>
                        )}
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-footer">
                <p className="sidebar-footer-text">AI-Powered System</p>
                <p className="sidebar-footer-version">v2.0 — React + YOLO Dashboard</p>
            </div>
        </aside>
    );
}
