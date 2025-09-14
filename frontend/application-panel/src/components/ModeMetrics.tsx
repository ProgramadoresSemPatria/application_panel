// src/components/ModeMetrics.tsx
import React from 'react';
import type { ModeItem } from '../types';


const ModeMetrics: React.FC<{ modes: ModeItem[]; total: number }> = ({ modes, total }) => (
    <div className="mode-metrics">
        {modes.map((m) => (
            <div key={m.mode} className="mode-metric">
                <div className="mode-info">
                    <span className="mode-name">{m.mode}</span>
                    <span className="mode-count">{m.count} applications</span>
                </div>
                <div className="mode-percentage">{((m.count / Math.max(1, total)) * 100).toFixed(1)}%</div>
            </div>
        ))}
    </div>
);


export default ModeMetrics;