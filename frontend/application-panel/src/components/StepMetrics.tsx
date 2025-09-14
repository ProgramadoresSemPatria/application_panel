// src/components/StepMetrics.tsx
import React from 'react';
import type { ConversionStep } from '../types';


const StepMetrics: React.FC<{ steps: ConversionStep[] }> = ({ steps }) => (
    <div className="step-metrics">
        {steps.map((s) => (
            <div key={s.step_name} className="step-metric">
                <div className="step-info-dashboard">
                    <div className="step-indicator" style={{ backgroundColor: s.step_color }} />
                    <div className="step-details">
                        <div className="step-name">{s.step_name}</div>
                        <div className="step-stats">{s.count ?? '-'} applications</div>
                    </div>
                </div>
                <div className="step-conversion">
                    <div className="conversion-rate">{s.conversion_rate}%</div>
                    <div className="conversion-label">reach rate</div>
                </div>
            </div>
        ))}
    </div>
);


export default StepMetrics;