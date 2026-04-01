'use client';
import { useCallback, useEffect } from 'react';
import { useInsuranceStore } from '@/lib/store/insuranceStore';
import { insuranceClient } from '@/lib/api/insuranceClient';

const MOCK_COVERAGE = {
  id: 'cov-001',
  workerId: 'worker-001',
  status: 'active',
  weeklyPremium: 149,
  coverageTypes: ['weather', 'pollution', 'restrictions'],
  activeSince: '2024-01-15',
  disruptionLevel: 'low',
};

export function useInsurance(workerId = 'worker-001') {
  const { coverage, setCoverage, setLoading, setError, loading, error } = useInsuranceStore();

  const loadCoverage = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await insuranceClient.getCoverage(workerId);
      setCoverage(data);
    } catch {
      setCoverage(MOCK_COVERAGE);
    } finally {
      setLoading(false);
    }
  }, [workerId, setCoverage, setLoading, setError]);

  const activateCoverage = useCallback(async (data) => {
    setLoading(true);
    try {
      const result = await insuranceClient.activateCoverage(workerId, data);
      setCoverage(result);
      return result;
    } catch {
      setCoverage((prev) => ({ ...prev, status: 'active' }));
    } finally {
      setLoading(false);
    }
  }, [workerId, setCoverage, setLoading]);

  const deactivateCoverage = useCallback(async () => {
    setLoading(true);
    try {
      await insuranceClient.deactivateCoverage(workerId);
      setCoverage((prev) => prev ? { ...prev, status: 'inactive' } : { ...MOCK_COVERAGE, status: 'inactive' });
    } catch {
      setCoverage((prev) => prev ? { ...prev, status: 'inactive' } : { ...MOCK_COVERAGE, status: 'inactive' });
    } finally {
      setLoading(false);
    }
  }, [workerId, setCoverage, setLoading]);

  useEffect(() => {
    if (!coverage) loadCoverage();
  }, [coverage, loadCoverage]);

  return { coverage: coverage || MOCK_COVERAGE, loading, error, loadCoverage, activateCoverage, deactivateCoverage };
}
