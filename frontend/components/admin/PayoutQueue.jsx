'use client';
import React, { useState } from 'react';
import { CheckCircle, XCircle, Users, IndianRupee } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';

const MOCK_PAYOUTS = [
  { id: 'pay-101', disruptionEvent: 'Heavy Rainfall — Mumbai', workersAffected: 234, totalAmount: 81900, status: 'pending', date: '2024-03-20' },
  { id: 'pay-102', disruptionEvent: 'AQI Alert — Andheri', workersAffected: 156, totalAmount: 43680, status: 'pending', date: '2024-03-19' },
  { id: 'pay-103', disruptionEvent: 'Odd-Even Restriction', workersAffected: 412, totalAmount: 172840, status: 'approved', date: '2024-03-18' },
  { id: 'pay-104', disruptionEvent: 'Cyclone Warning', workersAffected: 89, totalAmount: 27590, status: 'paid', date: '2024-03-15' },
  { id: 'pay-105', disruptionEvent: 'Fog Advisory', workersAffected: 67, totalAmount: 20770, status: 'paid', date: '2024-03-12' },
];

const statusVariants = { pending: 'warning', approved: 'info', paid: 'success', rejected: 'danger' };

export function PayoutQueue() {
  const [payouts, setPayouts] = useState(MOCK_PAYOUTS);
  const [filter, setFilter] = useState('all');
  const [processing, setProcessing] = useState(null);

  const filtered = filter === 'all' ? payouts : payouts.filter((p) => p.status === filter);
  const pendingCount = payouts.filter((p) => p.status === 'pending').length;

  const approve = async (id) => {
    setProcessing(id);
    await new Promise((r) => setTimeout(r, 600));
    setPayouts((prev) => prev.map((p) => (p.id === id ? { ...p, status: 'approved' } : p)));
    setProcessing(null);
  };

  const reject = async (id) => {
    setProcessing(id);
    await new Promise((r) => setTimeout(r, 600));
    setPayouts((prev) => prev.map((p) => (p.id === id ? { ...p, status: 'rejected' } : p)));
    setProcessing(null);
  };

  const batchApprove = async () => {
    setProcessing('batch');
    await new Promise((r) => setTimeout(r, 1000));
    setPayouts((prev) => prev.map((p) => (p.status === 'pending' ? { ...p, status: 'approved' } : p)));
    setProcessing(null);
  };

  const FILTERS = ['all', 'pending', 'approved', 'paid', 'rejected'];

  return (
    <div>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((f) => (
            <button key={f} onClick={() => setFilter(f)} className={`px-3 py-1.5 rounded-lg text-sm font-medium capitalize transition-colors ${filter === f ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300'}`}>
              {f}
            </button>
          ))}
        </div>
        {pendingCount > 0 && (
          <Button size="sm" variant="success" isLoading={processing === 'batch'} onClick={batchApprove} icon={<CheckCircle className="w-4 h-4" />}>
            Approve All ({pendingCount})
          </Button>
        )}
      </div>

      <div className="space-y-3">
        {filtered.map((payout) => (
          <Card key={payout.id} variant="default" className="hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4 flex-wrap">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <p className="font-semibold text-gray-900 dark:text-white">{payout.disruptionEvent}</p>
                  <Badge variant={statusVariants[payout.status] || 'neutral'}>{payout.status}</Badge>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-500 flex-wrap">
                  <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {payout.workersAffected} workers</span>
                  <span className="flex items-center gap-1"><IndianRupee className="w-3.5 h-3.5" /> ₹{payout.totalAmount.toLocaleString('en-IN')}</span>
                  <span>{new Date(payout.date).toLocaleDateString('en-IN')}</span>
                </div>
              </div>
              {payout.status === 'pending' && (
                <div className="flex gap-2 shrink-0">
                  <Button size="sm" variant="success" isLoading={processing === payout.id} onClick={() => approve(payout.id)} icon={<CheckCircle className="w-4 h-4" />}>
                    Approve
                  </Button>
                  <Button size="sm" variant="danger" isLoading={processing === payout.id} onClick={() => reject(payout.id)} icon={<XCircle className="w-4 h-4" />}>
                    Reject
                  </Button>
                </div>
              )}
            </div>
          </Card>
        ))}
        {filtered.length === 0 && <div className="text-center py-12 text-gray-400">No payouts in this category</div>}
      </div>
    </div>
  );
}
