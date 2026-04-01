'use client';
import React from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Users, Shield, FileText, TrendingUp, IndianRupee } from 'lucide-react';
import { Card } from '@/components/common/Card';

const CLAIMS_DATA = [
  { date: 'Mon', claims: 12 }, { date: 'Tue', claims: 19 }, { date: 'Wed', claims: 8 },
  { date: 'Thu', claims: 24 }, { date: 'Fri', claims: 31 }, { date: 'Sat', claims: 15 }, { date: 'Sun', claims: 7 },
];

const PAYOUTS_DATA = [
  { week: 'Wk 1', amount: 84 }, { week: 'Wk 2', amount: 132 },
  { week: 'Wk 3', amount: 97 }, { week: 'Wk 4', amount: 158 },
];

const METRICS = [
  { label: 'Total Workers', value: '1,247', icon: Users, color: 'blue', delta: '+5.2%' },
  { label: 'Active Coverages', value: '983', icon: Shield, color: 'green', delta: '+3.1%' },
  { label: 'Pending Claims', value: '47', icon: FileText, color: 'orange', delta: '-8.4%' },
  { label: 'Payout Rate', value: '94.2%', icon: TrendingUp, color: 'purple', delta: '+1.1%' },
];

const colorMap = { blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30', green: 'bg-green-100 text-green-600 dark:bg-green-900/30', orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900/30', purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900/30' };

export function AnalyticsDashboard() {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {METRICS.map((m) => {
          const Icon = m.icon;
          const positive = m.delta.startsWith('+');
          return (
            <Card key={m.label} variant="default">
              <div className={`inline-flex p-2.5 rounded-xl mb-3 ${colorMap[m.color]}`}>
                <Icon className="w-5 h-5" />
              </div>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{m.value}</p>
              <p className="text-sm text-gray-500 mb-1">{m.label}</p>
              <span className={`text-xs font-medium ${positive ? 'text-green-600' : 'text-red-500'}`}>{m.delta} vs last month</span>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card variant="default">
          <h3 className="font-bold text-gray-900 dark:text-white mb-4">Claims Volume (Last 7 Days)</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={CLAIMS_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip />
                <Bar dataKey="claims" name="Claims" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        <Card variant="default">
          <h3 className="font-bold text-gray-900 dark:text-white mb-4">Payout Trends (₹ thousands)</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={PAYOUTS_DATA}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="week" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `₹${v}k`} />
                <Tooltip formatter={(v) => [`₹${v}k`, 'Payouts']} />
                <Line type="monotone" dataKey="amount" stroke="#10B981" strokeWidth={2} dot={{ fill: '#10B981', r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
        <div className="flex items-center gap-2 text-blue-700 dark:text-blue-300">
          <IndianRupee className="w-5 h-5" />
          <span className="font-bold text-lg">Total Payouts: ₹50,23,400</span>
          <span className="text-sm text-blue-500 ml-2">across 1,247 workers</span>
        </div>
      </div>
    </div>
  );
}
