'use client';
import React, { useState } from 'react';
import { BarChart2 } from 'lucide-react';
import { Tabs } from '@/components/common/Tabs';
import { AnalyticsDashboard } from '@/components/admin/AnalyticsDashboard';
import { DisruptionMonitor } from '@/components/admin/DisruptionMonitor';
import { PayoutQueue } from '@/components/admin/PayoutQueue';
import { UnderwritingPanel } from '@/components/admin/UnderwritingPanel';
import { EventManager } from '@/components/admin/EventManager';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'disruptions', label: 'Disruptions' },
  { id: 'payouts', label: 'Payouts' },
  { id: 'underwriting', label: 'Underwriting' },
  { id: 'events', label: 'Events' },
];

const TAB_COMPONENTS = {
  overview: AnalyticsDashboard,
  disruptions: DisruptionMonitor,
  payouts: PayoutQueue,
  underwriting: UnderwritingPanel,
  events: EventManager,
};

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview');

  const ActiveComponent = TAB_COMPONENTS[activeTab] || AnalyticsDashboard;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
          <BarChart2 className="w-6 h-6 text-purple-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Admin Dashboard</h1>
          <p className="text-sm text-gray-500">Monitor disruptions, manage payouts, and oversee coverage</p>
        </div>
      </div>

      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} className="mb-6" />

      <div><ActiveComponent /></div>
    </div>
  );
}
