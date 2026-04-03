'use client';
import { useCallback, useEffect } from 'react';
import { useDisruptionStore } from '@/lib/store/disruptionStore';
import { disruptionClient } from '@/lib/api/disruptionClient';

const MOCK_DISRUPTIONS = [
  { id: 'evt-005', type: 'weather', severity: 4, description: 'Heavy rainfall warning in South Mumbai', affectedAreas: ['Dadar', 'Worli', 'Bandra'], affectedWorkers: 234, startTime: new Date().toISOString(), status: 'active' },
  { id: 'evt-006', type: 'pollution', severity: 3, description: 'AQI above 250 - Hazardous conditions', affectedAreas: ['Andheri', 'Kurla'], affectedWorkers: 156, startTime: new Date().toISOString(), status: 'active' },
];

export function useDisruptions() {
  const { events, activeDisruptions, setEvents, setActiveDisruptions, dismissDisruption, setLoading, loading } = useDisruptionStore();

  const loadDisruptions = useCallback(async () => {
    setLoading(true);
    try {
      const data = await disruptionClient.getActiveDisruptions();
      setActiveDisruptions(data);
    } catch {
      setActiveDisruptions(MOCK_DISRUPTIONS);
    } finally {
      setLoading(false);
    }
  }, [setActiveDisruptions, setLoading]);

  const loadHistory = useCallback(async (params) => {
    setLoading(true);
    try {
      const data = await disruptionClient.getHistory(params);
      setEvents(data);
    } catch {
      setEvents([]);
    } finally {
      setLoading(false);
    }
  }, [setEvents, setLoading]);

  useEffect(() => {
    if (activeDisruptions.length === 0) loadDisruptions();
  }, [activeDisruptions.length, loadDisruptions]);

  return {
    events,
    activeDisruptions: activeDisruptions.length > 0 ? activeDisruptions : MOCK_DISRUPTIONS,
    loading,
    loadDisruptions,
    loadHistory,
    dismissDisruption,
  };
}
