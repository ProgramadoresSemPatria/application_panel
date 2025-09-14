// src/data/mockData.ts
import type { DashboardData } from '../types';


export const mockData: DashboardData = {
    total_applications: 120,
    total_offers: 8,
    total_denials: 60,
    success_rate: 6.7,
    conversion_data: [
        { step_name: 'Applied', conversion_rate: 100, step_color: '#4f46e5', count: 120 },
        { step_name: 'Phone Screen', conversion_rate: 50, step_color: '#06b6d4', count: 60 },
        { step_name: 'Interview', conversion_rate: 25, step_color: '#f59e0b', count: 30 },
        { step_name: 'Offer', conversion_rate: 6.7, step_color: '#10b981', count: 8 },
    ],
    applications_by_platform: [
        { platform_name: 'LinkedIn', count: 50 },
        { platform_name: 'Indeed', count: 30 },
        { platform_name: 'Company site', count: 20 },
        { platform_name: 'Referral', count: 20 },
    ],
    applications_by_mode: [
        { mode: 'remote', count: 70 },
        { mode: 'hybrid', count: 30 },
        { mode: 'on-site', count: 20 },
    ],
    average_days_per_step: [
        { step_name: 'Applied → Screen', avg_days: 5, step_color: '#4f46e5' },
        { step_name: 'Screen → Interview', avg_days: 7, step_color: '#06b6d4' },
        { step_name: 'Interview → Offer', avg_days: 12, step_color: '#f59e0b' },
    ],
    monthly_applications: Array.from({ length: 30 }).map((_, i) => ({
        application_date: new Date(Date.now() - (29 - i) * 24 * 3600 * 1000).toLocaleDateString(),
        count: Math.floor(1 + Math.random() * 8),
    })),
};