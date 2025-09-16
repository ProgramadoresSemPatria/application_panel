// src/components/ModeMetrics.tsx
import React from 'react';
import type { ModeItem } from '../types';


const ModeMetrics: React.FC<{ modes: ModeItem[]; total: number }> = ({ modes, total }) => (
    <div className="flex flex-col gap-4">
        {modes.map((m) => (
            <div key={m.mode} className="flex justify-between items-center p-3 bg-white/5 rounded-md">
                <div className="flex flex-col">
                    <span className="font-semibold text-white/90 text-[0.95rem]">{m.mode}</span>
                    <span className="text-white/60 text-[0.8rem]">{m.count} applications</span>
                </div>
                <div className="font-bold text-white/90 text-[1.1rem]">{((m.count / Math.max(1, total)) * 100).toFixed(1)}%</div>
            </div>
        ))}
    </div>
);


export default ModeMetrics;