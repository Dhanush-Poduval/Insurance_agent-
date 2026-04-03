'use client';
import React, { useState } from 'react';
import { CloudRain, Wind, AlertTriangle, FileText } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Tabs } from '@/components/common/Tabs';

const typeIcons = { weather: CloudRain, pollution: Wind, restriction: AlertTriangle };
const statusVariants = { pending: 'warning', approved: 'info', rejected: 'danger', paid: 'success' };

const TABS = [
  { id: 'all', label: 'All' },
  { id: 'pending', label: 'Pending' },
  { id: 'approved', label: 'Approved' },
  { id: 'paid', label: 'Paid' },
];

export function ClaimsHistory({ claims = [] }) {
  const [activeTab, setActiveTab] = useState('all');

  const filtered = activeTab === 'all' ? claims : claims.filter((c) => c.status === activeTab);

  return (
    <Card variant="default">
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-blue-600" />
        <h3 className="font-bold text-gray-900 dark:text-white text-lg">Claims History</h3>
      </div>

      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} className="mb-4" />

      <div className="space-y-3 mt-4">
        {filtered.length === 0 ? (
          <p className="text-center text-gray-400 py-8">No claims found</p>
        ) : (
          filtered.map((claim) => {
            const Icon = typeIcons[claim.disruptionType] || FileText;
            return (
              <div key={claim.id} className="flex items-center gap-3 p-3 rounded-xl border border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <div className="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg shrink-0">
                  <Icon className="w-4 h-4 text-blue-600" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <span className="text-sm font-semibold text-gray-900 dark:text-white truncate">#{claim.id}</span>
                    <Badge variant={statusVariants[claim.status] || 'neutral'} size="sm">{claim.status}</Badge>
                  </div>
                  <p className="text-xs text-gray-500 capitalize">{claim.disruptionType} disruption • {new Date(claim.submittedAt).toLocaleDateString('en-IN')}</p>
                </div>
                <div className="text-right shrink-0">
                  <p className="font-bold text-gray-900 dark:text-white">₹{claim.amount}</p>
                </div>
              </div>
            );
          })
        )}
      </div>
    </Card>
  );
}
