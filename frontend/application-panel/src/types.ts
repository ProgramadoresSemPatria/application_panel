// src/types.ts
export interface ConversionStep {
    step_name: string;
    conversion_rate: number; // percent
    step_color: string; // hex, e.g. '#13ECAB'
    count?: number;
}


export interface AverageDaysStep {
    step_name: string;
    avg_days: number;
    step_color: string;
}


export interface PlatformItem {
    platform_name: string;
    count: number;
}


export interface ModeItem {
    mode: string;
    count: number;
}


export interface MonthlyApplication {
    application_date: string; // ISO date or label
    count: number;
}


export interface DashboardData {
    total_applications: number;
    total_offers: number;
    total_denials: number;
    success_rate: number; // percent
    conversion_data: ConversionStep[];
    applications_by_platform: PlatformItem[];
    applications_by_mode: ModeItem[];
    average_days_per_step: AverageDaysStep[];
    monthly_applications: MonthlyApplication[];
}

export interface StepMetrics {
    step_name: string;
    step_color: string;
    count: number;
    conversion_rate: number;
}