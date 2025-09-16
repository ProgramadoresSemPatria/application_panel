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
        <div className="grid grid-cols-[repeat(auto-fit,minmax(200px,1fr))] gap-4 mb-4">
            <div className="bg-white/10 p-6 rounded-xl text-center backdrop-blur-md border border-white/20 transition-all duration-300 ease-in-out hover:bg-white/15 hover:-translate-y-0.5">
                <div className="text-2xl font-bold text-white/95 mb-2">{total}</div>
                <div className="text-sm text-white/70">Total Applications</div>
            </div>
            <div className="bg-white/10 p-6 rounded-xl text-center backdrop-blur-md border border-white/20 transition-all duration-300 ease-in-out hover:bg-white/15 hover:-translate-y-0.5">
                <div className="text-2xl font-bold text-white/95 mb-2">{offers}</div>
                <div className="text-sm text-white/70">Offers Received</div>
            </div>
            <div className="bg-white/10 p-6 rounded-xl text-center backdrop-blur-md border border-white/20 transition-all duration-300 ease-in-out hover:bg-white/15 hover:-translate-y-0.5">
                <div className="text-2xl font-bold text-white/95 mb-2">{successRate}%</div>
                <div className="text-sm text-white/70">Success Rate</div>
            </div>
            <div className="bg-white/10 p-6 rounded-xl text-center backdrop-blur-md border border-white/20 transition-all duration-300 ease-in-out hover:bg-white/15 hover:-translate-y-0.5">
                <div className="text-2xl font-bold text-white/95 mb-2">{denials}</div>
                <div className="text-sm text-white/70">Denials</div>
            </div>
        </div>
    );
};


export default StatsCards;