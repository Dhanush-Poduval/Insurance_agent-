'use client';
import { useCallback, useEffect } from 'react';
import { useInsuranceStore } from '@/lib/store/insuranceStore';
import { claimsClient } from '@/lib/api/claimsClient';

const MOCK_CLAIMS = [
  { id: 'clm-001', workerId: 'worker-001', disruptionEventId: 'evt-001', disruptionType: 'weather', status: 'paid', amount: 350, submittedAt: '2024-03-10', processedAt: '2024-03-11' },
  { id: 'clm-002', workerId: 'worker-001', disruptionEventId: 'evt-002', disruptionType: 'pollution', status: 'approved', amount: 280, submittedAt: '2024-03-15' },
  { id: 'clm-003', workerId: 'worker-001', disruptionEventId: 'evt-003', disruptionType: 'restriction', status: 'pending', amount: 420, submittedAt: '2024-03-20' },
  { id: 'clm-004', workerId: 'worker-001', disruptionEventId: 'evt-004', disruptionType: 'weather', status: 'paid', amount: 310, submittedAt: '2024-02-28', processedAt: '2024-03-01' },
];

export function useClaims(workerId = 'worker-001') {
  const { claims, setClaims, addClaim, updateClaim, setLoading, setError, loading } = useInsuranceStore();

  const loadClaims = useCallback(async () => {
    setLoading(true);
    try {
      const data = await claimsClient.getWorkerClaims(workerId);
      setClaims(data);
    } catch {
      setClaims(MOCK_CLAIMS);
    } finally {
      setLoading(false);
    }
  }, [workerId, setClaims, setLoading]);

  const submitClaim = useCallback(async (data) => {
    setLoading(true);
    setError(null);
    try {
      const result = await claimsClient.submitClaim({ ...data, workerId });
      addClaim(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [workerId, addClaim, setLoading, setError]);

  useEffect(() => {
    if (claims.length === 0) loadClaims();
  }, [claims.length, loadClaims]);

  return { claims: claims.length > 0 ? claims : MOCK_CLAIMS, loading, loadClaims, submitClaim, updateClaim };
}
