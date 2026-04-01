'use client';
import React from 'react';
import { IndianRupee, CheckCircle, Clock, XCircle } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';

const MOCK_PAYOUTS = [
  { id: 'pay-001', disruptionEvent: 'Heavy Rainfall - Mumbai', amount: 350, date: '2024-03-11', status: 'paid' },
  { id: 'pay-002', disruptionEvent: 'AQI Alert - Andheri', amount: 280, date: '2024-03-16', status: 'approved' },
  { id: 'pay-003', disruptionEvent: 'Odd-Even Restriction', amount: 420, date: '2024-02-29', status: 'pending' },
  { id: 'pay-004', disruptionEvent: 'Cyclone Warning', amount: 310, date: '2024-03-01', status: 'paid' },
];

const statusConfig = {
  paid: { variant: 'success', icon: CheckCircle, label: 'Paid' },
  approved: { variant: 'info', icon: Clock, label: 'Approved' },
  pending: { variant: 'warning', icon: Clock, label: 'Pending' },
  rejected: { variant: 'danger', icon: XCircle, label: 'Rejected' },
};

export function PayoutTracker({ payouts = MOCK_PAYOUTS }) {
  const totalPaid = payouts.filter((p) => p.status === 'paid').reduce((sum, p) => sum + p.amount, 0);

  return (
    <Card variant="default">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <IndianRupee className="w-5 h-5 text-green-600" />
          <h3 className="font-bold text-gray-900 dark:text-white text-lg">Payout Tracker</h3>
        </div>
      </div>

      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-xl mb-4">
        <p className="text-xs text-green-600 font-medium mb-1">Total Received</p>
        <p className="text-2xl font-bold text-green-700 dark:text-green-400">₹{totalPaid.toLocaleString('en-IN')}</p>
      </div>

      <div className="space-y-3">
        {payouts.map((payout) => {
          const config = statusConfig[payout.status] || statusConfig.pending;
          const Icon = config.icon;
          return (
            <div key={payout.id} className="flex items-center justify-between gap-3 p-3 rounded-xl border border-gray-100 dark:border-gray-700">
              <div className="flex items-center gap-3 min-w-0">
                <Icon className={`w-4 h-4 shrink-0 ${payout.status === 'paid' ? 'text-green-500' : payout.status === 'pending' ? 'text-orange-500' : 'text-blue-500'}`} />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">{payout.disruptionEvent}</p>
                  <p className="text-xs text-gray-500">{new Date(payout.date).toLocaleDateString('en-IN')}</p>
                </div>
              </div>
              <div className="text-right shrink-0">
                <p className="font-bold text-gray-900 dark:text-white">₹{payout.amount}</p>
                <Badge variant={config.variant} size="sm">{config.label}</Badge>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
