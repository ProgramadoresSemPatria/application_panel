// src/components/AverageDaysChart.tsx
import React from "react";
import { Bar } from "react-chartjs-2";
import type { AverageDaysStep } from "../types";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface Props {
    data: AverageDaysStep[];
}

const AverageDaysChart: React.FC<Props> = ({ data }) => {
    const chartData = {
        labels: data.map((d) => d.step_name),
        datasets: [
            {
                label: "Average Days",
                data: data.map((d) => d.avg_days),
                backgroundColor: data.map((d) => d.step_color + "80"),
                borderColor: data.map((d) => d.step_color),
                borderWidth: 2,
                borderRadius: 4,
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: { labels: { color: "#ddd" } },
            tooltip: {
                callbacks: {
                    label: function (context: any) {
                        return context.dataset.label + ": " + Math.round(context.parsed.y) + " days";
                    },
                },
            },
        },
        scales: {
            y: { beginAtZero: true, ticks: { color: "#ddd" } },
            x: { ticks: { color: "#ddd" } },
        },
    };

    return <Bar key={data.length} data={chartData} options={options} />;
};

export default AverageDaysChart;
