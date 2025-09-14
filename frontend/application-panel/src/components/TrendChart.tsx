// src/components/TrendChart.tsx
import React from "react";
import { Line } from "react-chartjs-2";
import type { MonthlyApplication } from "../types";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface Props {
    data: MonthlyApplication[];
}

const TrendChart: React.FC<Props> = ({ data }) => {
    const chartData = {
        labels: data.map((d) => d.application_date),
        datasets: [
            {
                label: "Applications",
                data: data.map((d) => d.count),
                borderColor: "rgba(19, 236, 171, 1)",
                backgroundColor: "rgba(19, 236, 171, 0.1)",
                fill: true,
                tension: 0.4,
                borderWidth: 3,
                pointBackgroundColor: "rgba(19, 236, 171, 1)",
                pointBorderColor: "#fff",
                pointBorderWidth: 2,
                pointRadius: 6,
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: { legend: { labels: { color: "#ddd" } } },
        scales: {
            y: { beginAtZero: true, ticks: { color: "#ddd" } },
            x: { ticks: { color: "#ddd" } },
        },
    };

    return <Line key={data.length} data={chartData} options={options} />;
};

export default TrendChart;
