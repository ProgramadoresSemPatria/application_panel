// src/components/PlatformMetrics.tsx
import React from 'react';
import type { PlatformItem } from '../types';


const PlatformMetrics: React.FC<{ platforms: PlatformItem[]; total: number }> = ({ platforms, total }) => (
    <div className="platform-metrics">
        {platforms.map((p) => (
            <div key={p.platform_name} className="platform-metric">
                <span className="platform-name">{p.platform_name}</span>
                <div className="platform-count-container">
                    <span className="platform-count">{p.count}</span>
                    <div className="platform-bar">
                        <div
                            className="platform-bar-fill"
                            style={{ width: `${(p.count / Math.max(1, total)) * 100}%` }}
                        />
                    </div>
                </div>
            </div>
        ))}
    </div>
);


export default PlatformMetrics;