// src/components/StatsCards.tsx
import React from 'react';


interface Props {
    total: number;
    offers: number;
    denials: number;
    successRate: number;
}


const StatsCards: React.FC<Props> = ({ total, offers, denials, successRate }) => {
    return (
        <div className="stats-grid">
            <div className="stat-card">
                <div className="stat-number">{total}</div>
                <div className="stat-label">Total Applications</div>
            </div>
            <div className="stat-card">
                <div className="stat-number">{offers}</div>
                <div className="stat-label">Offers Received</div>
            </div>
            <div className="stat-card">
                <div className="stat-number">{successRate}%</div>
                <div className="stat-label">Success Rate</div>
            </div>
            <div className="stat-card">
                <div className="stat-number">{denials}</div>
                <div className="stat-label">Denials</div>
            </div>
        </div>
    );
};


export default StatsCards;