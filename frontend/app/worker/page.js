'use client';
import React, { useState } from 'react';
import { User } from 'lucide-react';
import { InsuranceCard } from '@/components/worker/InsuranceCard';
import { ClaimsHistory } from '@/components/worker/ClaimsHistory';
import { EarningsChart } from '@/components/worker/EarningsChart';
import { PayoutTracker } from '@/components/worker/PayoutTracker';
import { WorkerProfile } from '@/components/worker/WorkerProfile';
import { DisruptionAlert } from '@/components/worker/DisruptionAlert';

const MOCK_WORKER = {
  id: 'worker-001',
  name: 'Ravi Kumar',
  platform: 'Uber',
  location: 'Mumbai, Maharashtra',
  verified: true,
  avgDailyEarnings: 850,
  joinDate: '2023-06-15',
  rating: '4.8',
};

const MOCK_COVERAGE = {
  id: 'cov-001',
  workerId: 'worker-001',
  status: 'active',
  weeklyPremium: 149,
  coverageTypes: ['weather', 'pollution', 'restrictions'],
  activeSince: '2024-01-15',
  disruptionLevel: 'medium',
};

const MOCK_CLAIMS = [
  { id: 'clm-001', disruptionEventId: 'evt-001', disruptionType: 'weather', status: 'paid', amount: 350, submittedAt: '2024-03-10' },
  { id: 'clm-002', disruptionEventId: 'evt-002', disruptionType: 'pollution', status: 'approved', amount: 280, submittedAt: '2024-03-15' },
  { id: 'clm-003', disruptionEventId: 'evt-003', disruptionType: 'restriction', status: 'pending', amount: 420, submittedAt: '2024-03-20' },
  { id: 'clm-004', disruptionEventId: 'evt-004', disruptionType: 'weather', status: 'paid', amount: 310, submittedAt: '2024-02-28' },
];

const MOCK_DISRUPTIONS = [
  { id: 'evt-005', type: 'weather', severity: 4, description: 'Heavy rainfall warning in South Mumbai — IMD Red Alert issued', affectedAreas: ['Dadar', 'Worli', 'Bandra'], affectedWorkers: 234, startTime: new Date().toISOString(), status: 'active' },
];

export default function WorkerDashboard() {
  const [disruptions, setDisruptions] = useState(MOCK_DISRUPTIONS);

  const dismissDisruption = (id) => {
    setDisruptions((prev) => prev.filter((d) => d.id !== id));
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
          <User className="w-6 h-6 text-blue-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Welcome back, {MOCK_WORKER.name} 👋</h1>
          <p className="text-sm text-gray-500">Your coverage is active and protecting your earnings</p>
        </div>
      </div>

      {/* Disruption Alerts */}
      {disruptions.length > 0 && (
        <div className="mb-6">
          <DisruptionAlert disruptions={disruptions} onDismiss={dismissDisruption} />
        </div>
      )}

      {/* Top Row: Insurance Card + Worker Profile */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <InsuranceCard coverage={MOCK_COVERAGE} />
        <WorkerProfile worker={MOCK_WORKER} />
      </div>

      {/* Earnings Chart */}
      <div className="mb-6">
        <EarningsChart />
      </div>

      {/* Bottom Row: Claims History + Payout Tracker */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ClaimsHistory claims={MOCK_CLAIMS} />
        <PayoutTracker />
      </div>
    </div>
  );
}
