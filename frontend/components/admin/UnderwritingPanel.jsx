'use client';
import React from 'react';
import { Shield, TrendingUp, AlertCircle } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';
import { ProgressBar } from '@/components/common/ProgressBar';

const MOCK_WORKERS = [
  { id: 'w-001', name: 'Ravi Kumar', platform: 'Uber', riskScore: 72, premiumFactor: 1.4, recommendation: 'Increase premium by 15%', location: 'Mumbai' },
  { id: 'w-002', name: 'Priya Sharma', platform: 'Zomato', riskScore: 28, premiumFactor: 0.9, recommendation: 'Eligible for loyalty discount', location: 'Delhi' },
  { id: 'w-003', name: 'Amit Patel', platform: 'Swiggy', riskScore: 55, premiumFactor: 1.1, recommendation: 'Standard rate', location: 'Bangalore' },
  { id: 'w-004', name: 'Sunita Devi', platform: 'Ola', riskScore: 85, premiumFactor: 1.8, recommendation: 'High risk — review coverage', location: 'Chennai' },
  { id: 'w-005', name: 'Mohammed Ali', platform: 'Uber', riskScore: 40, premiumFactor: 1.0, recommendation: 'Standard rate', location: 'Hyderabad' },
];

const getRiskVariant = (score) => score >= 70 ? 'danger' : score >= 50 ? 'warning' : 'success';
const getRiskLabel = (score) => score >= 70 ? 'High' : score >= 50 ? 'Medium' : 'Low';

export function UnderwritingPanel() {
  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-blue-600" />
        <h3 className="font-bold text-gray-900 dark:text-white text-lg">Risk Analysis</h3>
      </div>

      <div className="space-y-3">
        {MOCK_WORKERS.map((worker) => (
          <Card key={worker.id} variant="default" className="hover:shadow-md transition-shadow">
            <div className="flex items-start gap-4 flex-wrap">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2 flex-wrap">
                  <p className="font-semibold text-gray-900 dark:text-white">{worker.name}</p>
                  <Badge variant="neutral" size="sm">{worker.platform}</Badge>
                  <span className="text-xs text-gray-400">{worker.location}</span>
                </div>
                <ProgressBar
                  value={worker.riskScore}
                  label="Risk Score"
                  variant={getRiskVariant(worker.riskScore)}
                  className="mb-2"
                />
                <div className="flex items-center gap-2 flex-wrap">
                  <Badge variant={getRiskVariant(worker.riskScore)} size="sm">{getRiskLabel(worker.riskScore)} Risk</Badge>
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <TrendingUp className="w-3.5 h-3.5" />
                    <span>Factor: {worker.premiumFactor}x</span>
                  </div>
                </div>
              </div>
              <div className="shrink-0 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-orange-500 mt-0.5 shrink-0" />
                <p className="text-sm text-gray-600 dark:text-gray-400 max-w-xs">{worker.recommendation}</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
