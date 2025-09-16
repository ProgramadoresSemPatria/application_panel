// src/components/StepMetrics.tsx
import React from 'react';
import type { ConversionStep } from '../types';


const StepMetrics: React.FC<{ steps: ConversionStep[] }> = ({ steps }) => (
    <div className="flex flex-col gap-4">
        {steps.map((s) => (
            <div key={s.step_name} className="flex justify-between items-center p-3 bg-white/5 rounded-md transition-all duration-300 hover:bg-white/10">
                <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: s.step_color }} />
                    <div className="flex flex-col">
                        <div className="font-semibold text-white/90 text-[0.95rem]">{s.step_name}</div>
                        <div className="text-white/60 text-[0.8rem]">{s.count ?? '-'} applications</div>
                    </div>
                </div>
                <div className="text-right">
                    <div className="font-bold text-white/90 text-[1.1rem]">{s.conversion_rate}%</div>
                    <div className="block text-white/60 text-[0.75rem]">reach rate</div>
                </div>
            </div>
        ))}
    </div>
);


export default StepMetrics;