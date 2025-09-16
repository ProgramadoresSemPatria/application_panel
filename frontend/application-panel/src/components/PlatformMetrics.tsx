// src/components/PlatformMetrics.tsx
import React from 'react';
import type { PlatformItem } from '../types';


const PlatformMetrics: React.FC<{ platforms: PlatformItem[]; total: number }> = ({ platforms, total }) => (
    <div className="flex flex-col gap-3">
        {platforms.map((p) => (
            <div key={p.platform_name} className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-white/80 font-medium">{p.platform_name}</span>
                <div className="flex items-center gap-3">
                    <span className="font-bold text-white/90 min-w-[30px] text-right">{p.count}</span>
                    <div className="w-[60px] h-1.5 bg-white/10 rounded overflow-hidden">
                        <div
                            className="h-full rounded bg-gradient-to-r from-[#13ecab]/80 to-[#13ecab]/100 transition-[width] duration-500 ease-in-out"
                            style={{ width: `${(p.count / Math.max(1, total)) * 100}%` }}
                        />
                    </div>
                </div>
            </div>
        ))}
    </div>
);


export default PlatformMetrics;