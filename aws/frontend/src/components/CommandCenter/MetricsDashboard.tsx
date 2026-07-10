/**
 * Metrics Dashboard - System metrics and analytics
 */

import React from 'react';
import { Card, CardHeader, Badge } from '../common';
import {
  ArrowUpIcon,
  ArrowDownIcon,
  DocumentTextIcon,
  CpuChipIcon,
  ClockIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import clsx from 'clsx';

interface MetricData {
  documentsProcessed: number;
  documentsProcessedChange: number;
  avgProcessingTime: number;
  avgProcessingTimeChange: number;
  successRate: number;
  successRateChange: number;
  activeAgents: number;
  activeAgentsChange: number;
  processingTrend: { date: string; count: number }[];
  documentTypeDistribution: { type: string; count: number }[];
  hourlyProcessing: { hour: string; count: number }[];
  recentActivity: { time: string; action: string; status: string }[];
}

interface MetricsDashboardProps {
  data: MetricData;
  timeRange: '24h' | '7d' | '30d';
  onTimeRangeChange: (range: '24h' | '7d' | '30d') => void;
}

const COLORS = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];

export const MetricsDashboard: React.FC<MetricsDashboardProps> = ({
  data,
  timeRange,
  onTimeRangeChange,
}) => {
  const StatCard = ({
    title,
    value,
    change,
    icon: Icon,
    format = 'number',
  }: {
    title: string;
    value: number;
    change: number;
    icon: any;
    format?: 'number' | 'percent' | 'time';
  }) => {
    const isPositive = change >= 0;
    const formattedValue = format === 'percent'
      ? `${value.toFixed(1)}%`
      : format === 'time'
      ? `${value.toFixed(1)}s`
      : value.toLocaleString();

    return (
      <Card>
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-500">{title}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{formattedValue}</p>
          </div>
          <div className="p-3 bg-apex-50 rounded-xl">
            <Icon className="h-6 w-6 text-apex-600" />
          </div>
        </div>
        <div className="mt-4 flex items-center gap-1">
          {isPositive ? (
            <ArrowUpIcon className="h-4 w-4 text-success-500" />
          ) : (
            <ArrowDownIcon className="h-4 w-4 text-danger-500" />
          )}
          <span className={clsx(
            'text-sm font-medium',
            isPositive ? 'text-success-500' : 'text-danger-500'
          )}>
            {Math.abs(change).toFixed(1)}%
          </span>
          <span className="text-sm text-gray-400">vs last period</span>
        </div>
      </Card>
    );
  };

  return (
    <div className="p-6 space-y-6">
      {/* Time Range Selector */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Command Center</h1>
        <div className="flex bg-gray-100 rounded-lg p-1">
          {(['24h', '7d', '30d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => onTimeRangeChange(range)}
              className={clsx(
                'px-4 py-2 text-sm font-medium rounded-md transition-colors',
                timeRange === range
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              )}
            >
              {range === '24h' ? 'Last 24 Hours' : range === '7d' ? 'Last 7 Days' : 'Last 30 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-4 gap-6">
        <StatCard
          title="Documents Processed"
          value={data.documentsProcessed}
          change={data.documentsProcessedChange}
          icon={DocumentTextIcon}
        />
        <StatCard
          title="Avg Processing Time"
          value={data.avgProcessingTime}
          change={data.avgProcessingTimeChange}
          icon={ClockIcon}
          format="time"
        />
        <StatCard
          title="Success Rate"
          value={data.successRate}
          change={data.successRateChange}
          icon={CheckCircleIcon}
          format="percent"
        />
        <StatCard
          title="Active Agents"
          value={data.activeAgents}
          change={data.activeAgentsChange}
          icon={CpuChipIcon}
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-3 gap-6">
        {/* Processing Trend */}
        <Card className="col-span-2">
          <CardHeader title="Processing Trend" subtitle="Documents processed over time" />
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.processingTrend}>
                <defs>
                  <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} tickLine={false} />
                <YAxis tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="count"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fill="url(#colorCount)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Document Type Distribution */}
        <Card>
          <CardHeader title="Document Types" subtitle="Distribution by type" />
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.documentTypeDistribution}
                  dataKey="count"
                  nameKey="type"
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                >
                  {data.documentTypeDistribution.map((_, index) => (
                    <Cell key={index} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 space-y-2">
            {data.documentTypeDistribution.map((item, index) => (
              <div key={item.type} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: COLORS[index % COLORS.length] }}
                  />
                  <span className="text-gray-600">{item.type}</span>
                </div>
                <span className="font-medium">{item.count}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-2 gap-6">
        {/* Hourly Processing */}
        <Card>
          <CardHeader title="Hourly Activity" subtitle="Processing volume by hour" />
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.hourlyProcessing}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="hour" tick={{ fontSize: 10 }} tickLine={false} />
                <YAxis tick={{ fontSize: 12 }} tickLine={false} axisLine={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader title="Recent Activity" subtitle="Latest system events" />
          <div className="space-y-3 max-h-48 overflow-auto">
            {data.recentActivity.map((activity, index) => (
              <div
                key={index}
                className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
              >
                <div className="flex items-center gap-3">
                  <div className={clsx(
                    'w-2 h-2 rounded-full',
                    activity.status === 'success' && 'bg-success-500',
                    activity.status === 'failed' && 'bg-danger-500',
                    activity.status === 'pending' && 'bg-warning-500'
                  )} />
                  <span className="text-sm text-gray-700">{activity.action}</span>
                </div>
                <span className="text-xs text-gray-400">{activity.time}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default MetricsDashboard;
