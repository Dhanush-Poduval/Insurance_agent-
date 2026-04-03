'use client';
import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp } from 'lucide-react';
import { Card } from '@/components/common/Card';

const MOCK_DATA = [
  { week: 'Week 1', earnings: 3200, disrupted: 2100 },
  { week: 'Week 2', earnings: 3800, disrupted: 3800 },
  { week: 'Week 3', earnings: 2900, disrupted: 1800 },
  { week: 'Week 4', earnings: 4100, disrupted: 4100 },
  { week: 'Week 5', earnings: 3500, disrupted: 2900 },
  { week: 'Week 6', earnings: 4200, disrupted: 4200 },
  { week: 'Week 7', earnings: 3700, disrupted: 2400 },
  { week: 'Week 8', earnings: 4400, disrupted: 4400 },
];

export function EarningsChart() {
  return (
    <Card variant="default">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="w-5 h-5 text-blue-600" />
        <h3 className="font-bold text-gray-900 dark:text-white text-lg">Weekly Earnings Overview</h3>
      </div>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={MOCK_DATA} margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
            <defs>
              <linearGradient id="earningsGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="disruptedGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis dataKey="week" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `₹${(v / 1000).toFixed(1)}k`} />
            <Tooltip formatter={(value) => [`₹${value}`, '']} />
            <Legend />
            <Area type="monotone" dataKey="earnings" name="Gross Earnings" stroke="#3B82F6" fill="url(#earningsGrad)" strokeWidth={2} />
            <Area type="monotone" dataKey="disrupted" name="Insured Earnings" stroke="#10B981" fill="url(#disruptedGrad)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
