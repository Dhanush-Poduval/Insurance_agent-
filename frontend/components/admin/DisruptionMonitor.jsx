'use client';
import React, { useState, useEffect } from 'react';
import { CloudRain, Wind, AlertTriangle, RefreshCw, Users } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';

const typeConfig = {
  weather: { icon: CloudRain, label: 'Weather', variant: 'info' },
  pollution: { icon: Wind, label: 'Pollution', variant: 'warning' },
  restriction: { icon: AlertTriangle, label: 'Restriction', variant: 'danger' },
};

const SEVERITY_VARIANTS = { 1: 'neutral', 2: 'info', 3: 'warning', 4: 'danger', 5: 'danger' };

const MOCK_EVENTS = [
  { id: 'evt-001', type: 'weather', severity: 4, description: 'Heavy rainfall — IMD red alert', affectedAreas: ['Dadar', 'Worli', 'Bandra'], affectedWorkers: 234, startTime: new Date().toISOString(), status: 'active' },
  { id: 'evt-002', type: 'pollution', severity: 3, description: 'AQI 280 — Hazardous conditions', affectedAreas: ['Andheri', 'Kurla'], affectedWorkers: 156, startTime: new Date(Date.now() - 3600000).toISOString(), status: 'active' },
  { id: 'evt-003', type: 'restriction', severity: 2, description: 'Odd-Even vehicle restriction in effect', affectedAreas: ['All of Delhi NCR'], affectedWorkers: 412, startTime: new Date(Date.now() - 7200000).toISOString(), status: 'active' },
  { id: 'evt-004', type: 'weather', severity: 1, description: 'Mild fog advisory', affectedAreas: ['Airport Zone', 'Vile Parle'], affectedWorkers: 67, startTime: new Date(Date.now() - 10800000).toISOString(), status: 'active' },
];

const FILTERS = ['All', 'Weather', 'Pollution', 'Restriction'];

export function DisruptionMonitor() {
  const [filter, setFilter] = useState('All');
  const [events, setEvents] = useState(MOCK_EVENTS);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());

  const refresh = async () => {
    setRefreshing(true);
    await new Promise((r) => setTimeout(r, 800));
    setLastUpdated(new Date());
    setRefreshing(false);
  };

  useEffect(() => {
    const interval = setInterval(refresh, 30000);
    return () => clearInterval(interval);
  }, []);

  const filtered = filter === 'All' ? events : events.filter((e) => e.type === filter.toLowerCase());

  return (
    <div>
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <div className="flex gap-2 flex-wrap">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${filter === f ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300'}`}
            >
              {f}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">Updated {lastUpdated.toLocaleTimeString()}</span>
          <Button size="sm" variant="secondary" icon={<RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin' : ''}`} />} onClick={refresh} isLoading={false}>
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-4">
        {filtered.map((event) => {
          const config = typeConfig[event.type] || typeConfig.weather;
          const Icon = config.icon;
          return (
            <Card key={event.id} variant="default" className="hover:shadow-md transition-shadow">
              <div className="flex items-start gap-4">
                <div className={`p-2.5 rounded-xl ${event.type === 'weather' ? 'bg-blue-100 dark:bg-blue-900/30' : event.type === 'pollution' ? 'bg-orange-100 dark:bg-orange-900/30' : 'bg-red-100 dark:bg-red-900/30'}`}>
                  <Icon className={`w-5 h-5 ${event.type === 'weather' ? 'text-blue-600' : event.type === 'pollution' ? 'text-orange-600' : 'text-red-600'}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap mb-1">
                    <Badge variant={config.variant}>{config.label}</Badge>
                    <Badge variant={SEVERITY_VARIANTS[event.severity] || 'neutral'}>Severity {event.severity}/5</Badge>
                    <Badge variant="success">Active</Badge>
                  </div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white mb-1">{event.description}</p>
                  <p className="text-xs text-gray-500 mb-2">Areas: {event.affectedAreas.join(', ')}</p>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span className="flex items-center gap-1"><Users className="w-3.5 h-3.5" /> {event.affectedWorkers} workers affected</span>
                    <span>Started {new Date(event.startTime).toLocaleTimeString()}</span>
                  </div>
                </div>
              </div>
            </Card>
          );
        })}
        {filtered.length === 0 && (
          <div className="text-center py-12 text-gray-400">No disruptions found for selected filter</div>
        )}
      </div>
    </div>
  );
}
