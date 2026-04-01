'use client';
import React from 'react';
import { User, MapPin, CheckCircle, Calendar, TrendingUp, Star } from 'lucide-react';
import { Card } from '@/components/common/Card';
import { Badge } from '@/components/common/Badge';

const PLATFORMS = { Uber: 'bg-black text-white', Zomato: 'bg-red-500 text-white', Swiggy: 'bg-orange-500 text-white', Ola: 'bg-green-600 text-white' };

export function WorkerProfile({ worker }) {
  if (!worker) return null;

  const platformClass = PLATFORMS[worker.platform] || 'bg-gray-600 text-white';

  return (
    <Card variant="elevated">
      <div className="flex items-start gap-4 mb-5">
        <div className="w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shrink-0">
          <User className="w-7 h-7 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-bold text-gray-900 dark:text-white text-lg">{worker.name}</h3>
            {worker.verified && (
              <CheckCircle className="w-4 h-4 text-blue-500 shrink-0" title="Verified" />
            )}
          </div>
          <div className="flex items-center gap-2 mt-1 flex-wrap">
            <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${platformClass}`}>{worker.platform}</span>
            <div className="flex items-center gap-1 text-sm text-gray-500">
              <MapPin className="w-3.5 h-3.5" />
              <span>{worker.location}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-4">
        <div className="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
          <div className="flex items-center gap-1.5 text-blue-600 mb-1">
            <TrendingUp className="w-4 h-4" />
            <span className="text-xs font-medium">Avg Daily</span>
          </div>
          <p className="font-bold text-gray-900 dark:text-white">₹{worker.avgDailyEarnings}</p>
        </div>
        <div className="p-3 bg-purple-50 dark:bg-purple-900/20 rounded-xl">
          <div className="flex items-center gap-1.5 text-purple-600 mb-1">
            <Star className="w-4 h-4" />
            <span className="text-xs font-medium">Rating</span>
          </div>
          <p className="font-bold text-gray-900 dark:text-white">{worker.rating || '4.8'} ⭐</p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-sm text-gray-500">
        <Calendar className="w-4 h-4" />
        <span>Member since {new Date(worker.joinDate).toLocaleDateString('en-IN', { month: 'long', year: 'numeric' })}</span>
      </div>

      {worker.verified && (
        <div className="mt-3 flex items-center gap-2">
          <Badge variant="success">Verified Worker</Badge>
          <Badge variant="info">KYC Complete</Badge>
        </div>
      )}
    </Card>
  );
}
