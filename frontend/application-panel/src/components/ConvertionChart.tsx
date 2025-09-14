// src/components/ConversionChart.tsx
import React from "react";
import { Bar } from "react-chartjs-2";
import type { ConversionStep } from "../types";
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
    data: ConversionStep[];
}

const ConversionChart: React.FC<Props> = ({ data }) => {
    const chartData = {
        labels: data.map((d) => d.step_name),
        datasets: [
            {
                label: "Reach Rate (%)",
                data: data.map((d) => d.conversion_rate),
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
                        return context.dataset.label + ": " + context.parsed.y + "%";
                    },
                },
            },
        },
        scales: {
            y: { beginAtZero: true, max: 100, ticks: { color: "#ddd" } },
            x: { ticks: { color: "#ddd" } },
        },
    };

    return <Bar key={data.length} data={chartData} options={options} />;
};

export default ConversionChart;
