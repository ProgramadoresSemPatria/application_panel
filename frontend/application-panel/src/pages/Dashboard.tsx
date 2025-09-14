import React from "react";
import StatsCards from "../components/StatsCards";
import StepMetrics from "../components/StepMetrics";
import ConversionChart from "../components/ConvertionChart";
import AverageDaysChart from "../components/AverageDaysChart";
import PlatformMetrics from "../components/PlatformMetrics";
import ModeMetrics from "../components/ModeMetrics";
import TrendChart from "../components/TrendChart";
import { mockData } from "../data/mockData";

const Dashboard: React.FC = () => {
    return (
        <div className="p-6 space-y-6 bg-gray-900 min-h-screen text-white">
            <h1 className="text-2xl font-bold">Application Analytics Dashboard</h1>

            {/* Summary Stats */}
            <StatsCards
                total={mockData.total_applications}
                offers={mockData.total_offers}
                successRate={mockData.success_rate}
                denials={mockData.total_denials}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="p-4 bg-white/10 rounded-xl">
                    <h2 className="mb-2 font-semibold">Applications by Step</h2>
                    <StepMetrics steps={mockData.conversion_data} />
                </div>

                <div className="p-4 bg-white/10 rounded-xl">
                    <h2 className="mb-2 font-semibold">Conversion Funnel</h2>
                    <ConversionChart data={mockData.conversion_data} />
                </div>

                <div className="p-4 bg-white/10 rounded-xl">
                    <h2 className="mb-2 font-semibold">Average Days Between Steps</h2>
                    <AverageDaysChart data={mockData.average_days_per_step} />
                </div>

                <div className="p-4 bg-white/10 rounded-xl">
                    <h2 className="mb-2 font-semibold">Applications by Platform</h2>
                    <PlatformMetrics 
                        platforms={mockData.applications_by_platform} 
                        total={mockData.total_applications} 
                    />
                </div>

                <div className="p-4 bg-white/10 rounded-xl">
                    <h2 className="mb-2 font-semibold">Application Mode</h2>
                    <ModeMetrics 
                        modes={mockData.applications_by_mode} 
                        total={mockData.total_applications} 
                    />
                </div>


            </div>

            <div className="p-4 bg-white/10 rounded-xl">
                <h2 className="mb-2 font-semibold">Application Trend (Last 30 Days)</h2>
                <TrendChart data={mockData.monthly_applications} />
            </div>
        </div>
    );
};

export default Dashboard;
