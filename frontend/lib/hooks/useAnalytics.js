'use client';
import { useCallback, useEffect } from 'react';
import { useAdminStore } from '@/lib/store/adminStore';
import { analyticsClient } from '@/lib/api/analyticsClient';

const MOCK_METRICS = { totalWorkers: 1247, activeCoverages: 983, pendingClaims: 47, payoutRate: 94.2, totalPayouts: 5023400 };

const MOCK_CLAIMS_TIMELINE = [
  { date: 'Mon', claims: 12 }, { date: 'Tue', claims: 19 }, { date: 'Wed', claims: 8 },
  { date: 'Thu', claims: 24 }, { date: 'Fri', claims: 31 }, { date: 'Sat', claims: 15 }, { date: 'Sun', claims: 7 },
];

const MOCK_PAYOUTS_TIMELINE = [
  { date: 'Week 1', amount: 84000 }, { date: 'Week 2', amount: 132000 },
  { date: 'Week 3', amount: 97000 }, { date: 'Week 4', amount: 158000 },
];

export function useAnalytics() {
  const { metrics, setMetrics, setLoading, loading } = useAdminStore();

  const loadMetrics = useCallback(async () => {
    setLoading(true);
    try {
      const data = await analyticsClient.getMetrics();
      setMetrics(data);
    } catch {
      setMetrics(MOCK_METRICS);
    } finally {
      setLoading(false);
    }
  }, [setMetrics, setLoading]);

  useEffect(() => {
    if (!metrics) loadMetrics();
  }, [metrics, loadMetrics]);

  return {
    metrics: metrics || MOCK_METRICS,
    claimsTimeline: MOCK_CLAIMS_TIMELINE,
    payoutsTimeline: MOCK_PAYOUTS_TIMELINE,
    loading,
    loadMetrics,
  };
}
