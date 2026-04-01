'use client';
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, CloudRain, Wind, AlertTriangle, CheckCircle, Calendar } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { Button } from '@/components/common/Button';

const typeIcons = { weather: CloudRain, pollution: Wind, restrictions: AlertTriangle };

const disruptionLevelColor = { low: 'bg-green-500', medium: 'bg-orange-500', high: 'bg-red-500' };

export function InsuranceCard({ coverage }) {
  const [loading, setLoading] = useState(false);

  if (!coverage) return null;

  const isActive = coverage.status === 'active';
  const statusVariant = isActive ? 'success' : 'neutral';

  const handleToggle = async () => {
    setLoading(true);
    await new Promise((r) => setTimeout(r, 800));
    setLoading(false);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card variant="elevated" className="h-full">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
              <Shield className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-bold text-gray-900 dark:text-white text-lg">My Coverage</h3>
          </div>
          <Badge variant={statusVariant}>{isActive ? 'Active' : 'Inactive'}</Badge>
        </div>

        <div className="mb-5">
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-gray-900 dark:text-white">₹{coverage.weeklyPremium}</span>
            <span className="text-gray-500 text-sm">/week</span>
          </div>
          <div className="flex items-center gap-1.5 mt-1">
            <div className={`w-2 h-2 rounded-full ${disruptionLevelColor[coverage.disruptionLevel] || 'bg-gray-400'}`} />
            <span className="text-sm text-gray-500 capitalize">{coverage.disruptionLevel} disruption risk</span>
          </div>
        </div>

        {coverage.activeSince && (
          <div className="flex items-center gap-2 text-sm text-gray-500 mb-4">
            <Calendar className="w-4 h-4" />
            <span>Active since {new Date(coverage.activeSince).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</span>
          </div>
        )}

        <div className="mb-5">
          <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-2">Coverage Types</p>
          <div className="flex flex-wrap gap-2">
            {(coverage.coverageTypes || []).map((type) => {
              const Icon = typeIcons[type] || Shield;
              return (
                <div key={type} className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                  <Icon className="w-3.5 h-3.5 text-blue-600" />
                  <span className="text-xs font-medium text-blue-700 dark:text-blue-400 capitalize">{type}</span>
                </div>
              );
            })}
          </div>
        </div>

        {isActive && (
          <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg mb-4">
            <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
            <p className="text-xs text-green-700 dark:text-green-400">You are protected. Claims are processed automatically on qualifying disruptions.</p>
          </div>
        )}

        <Button
          variant={isActive ? 'secondary' : 'primary'}
          fullWidth
          isLoading={loading}
          onClick={handleToggle}
        >
          {isActive ? 'Deactivate Coverage' : 'Activate Coverage'}
        </Button>
      </Card>
    </motion.div>
  );
}
