'use client';
import React, { useState } from 'react';
import { Plus, Save, X } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Input } from '@/components/common/Input';
import { Select } from '@/components/common/Select';
import { Button } from '@/components/common/Button';
import { Badge } from '@/components/common/Badge';

const TYPE_OPTIONS = [
  { value: 'weather', label: 'Weather' },
  { value: 'pollution', label: 'Pollution' },
  { value: 'restriction', label: 'Restriction' },
];

const SEVERITY_OPTIONS = [
  { value: '1', label: '1 — Minor' },
  { value: '2', label: '2 — Moderate' },
  { value: '3', label: '3 — Significant' },
  { value: '4', label: '4 — Severe' },
  { value: '5', label: '5 — Extreme' },
];

const SEVERITY_VARIANTS = { '1': 'neutral', '2': 'info', '3': 'warning', '4': 'danger', '5': 'danger' };

const INITIAL = { type: 'weather', severity: '3', description: '', affectedAreas: '', threshold: '250' };

export function EventManager() {
  const [form, setForm] = useState(INITIAL);
  const [saving, setSaving] = useState(false);
  const [events, setEvents] = useState([]);
  const [saved, setSaved] = useState(false);

  const handleChange = (field) => (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.description.trim()) return;
    setSaving(true);
    await new Promise((r) => setTimeout(r, 800));
    const newEvent = {
      id: `evt-${Date.now()}`,
      ...form,
      severity: parseInt(form.severity),
      affectedAreas: form.affectedAreas.split(',').map((a) => a.trim()).filter(Boolean),
      createdAt: new Date().toISOString(),
      status: 'active',
    };
    setEvents((prev) => [newEvent, ...prev]);
    setForm(INITIAL);
    setSaving(false);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="space-y-6">
      <Card variant="default">
        <div className="flex items-center gap-2 mb-4">
          <Plus className="w-5 h-5 text-blue-600" />
          <h3 className="font-bold text-gray-900 dark:text-white text-lg">Create Disruption Event</h3>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Select label="Event Type" options={TYPE_OPTIONS} value={form.type} onChange={handleChange('type')} />
            <Select label="Severity" options={SEVERITY_OPTIONS} value={form.severity} onChange={handleChange('severity')} />
          </div>

          <Input
            label="Description"
            placeholder="Describe the disruption event..."
            value={form.description}
            onChange={handleChange('description')}
            required
          />

          <Input
            label="Affected Areas"
            placeholder="Dadar, Worli, Bandra (comma-separated)"
            value={form.affectedAreas}
            onChange={handleChange('affectedAreas')}
            helperText="Enter areas separated by commas"
          />

          <Input
            label="Threshold Value"
            type="number"
            placeholder="e.g. 250 for AQI, 100 for rainfall mm"
            value={form.threshold}
            onChange={handleChange('threshold')}
            helperText="Numeric threshold for automatic claim triggering"
          />

          <div className="flex items-center gap-3">
            <Button type="submit" isLoading={saving} icon={<Save className="w-4 h-4" />}>
              Create Event
            </Button>
            <Button type="button" variant="secondary" icon={<X className="w-4 h-4" />} onClick={() => setForm(INITIAL)}>
              Reset
            </Button>
            {saved && <span className="text-sm text-green-600 font-medium">✓ Event created!</span>}
          </div>
        </form>
      </Card>

      {events.length > 0 && (
        <div>
          <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Recently Created Events</h4>
          <div className="space-y-3">
            {events.map((event) => (
              <Card key={event.id} variant="outlined">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Badge variant={SEVERITY_VARIANTS[String(event.severity)] || 'neutral'}>Severity {event.severity}</Badge>
                      <Badge variant="info" size="sm">{event.type}</Badge>
                    </div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">{event.description}</p>
                    {event.affectedAreas.length > 0 && (
                      <p className="text-xs text-gray-500 mt-1">Areas: {event.affectedAreas.join(', ')}</p>
                    )}
                  </div>
                  <Badge variant="success" size="sm">Active</Badge>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
