import React from "react";
import ChartCard from "../components/ChartCard";
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
        <article className="grid grid-cols-1 md:grid-cols-4 gap-6 bg-black p-6 space-y-6 min-h-screen text-white">

            <h3 className="text-2xl col-span-4 text-center font-bold">Application Analytics Dashboard</h3>
            <section className="col-span-full">
                <StatsCards
                    total={mockData.total_applications}
                    offers={mockData.total_offers}
                    successRate={mockData.success_rate}
                    denials={mockData.total_denials}
                />
            </section>

            <section className="md:col-span-2">
                <ChartCard title="Applications by Step">
                    <StepMetrics steps={mockData.conversion_data} />
                </ChartCard>
            </section>

            <section className="md:col-span-2">
                <ChartCard title="Average Days Between Steps">
                    <AverageDaysChart data={mockData.average_days_per_step} />
                </ChartCard>
            </section>

            <section className="col-span-full p-4 bg-white/10 rounded-xl">
                <ChartCard title="Conversion Funnel">
                    <ConversionChart data={mockData.conversion_data} />
                </ChartCard>
            </section>

            <section className="md:col-span-2">
                <ChartCard title="Applications by Platform">
                    <PlatformMetrics
                        platforms={mockData.applications_by_platform}
                        total={mockData.total_applications}
                    />
                </ChartCard>
            </section>

            <section className="md:col-span-2">
                <ChartCard title="Application Mode">
                    <ModeMetrics
                        modes={mockData.applications_by_mode}
                        total={mockData.total_applications}
                    />
                </ChartCard>
            </section>

            <section className="col-span-full">
            <ChartCard title="Application Trend (Last 30 Days)">
                <TrendChart data={mockData.monthly_applications} />
            </ChartCard>
            </section>
        </article>
    );
};

export default Dashboard;
