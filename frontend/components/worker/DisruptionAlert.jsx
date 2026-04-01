'use client';
import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CloudRain, Wind, AlertTriangle, X, AlertCircle } from 'lucide-react';

const typeConfig = {
  weather: { icon: CloudRain, bgClass: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800', iconClass: 'text-blue-600', textClass: 'text-blue-800 dark:text-blue-200', label: 'Weather Alert' },
  pollution: { icon: Wind, bgClass: 'bg-orange-50 dark:bg-orange-900/30 border-orange-200 dark:border-orange-800', iconClass: 'text-orange-600', textClass: 'text-orange-800 dark:text-orange-200', label: 'Pollution Alert' },
  restriction: { icon: AlertTriangle, bgClass: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800', iconClass: 'text-red-600', textClass: 'text-red-800 dark:text-red-200', label: 'Restriction Alert' },
};

export function DisruptionAlert({ disruptions = [], onDismiss }) {
  return (
    <AnimatePresence>
      {disruptions.map((disruption) => {
        const config = typeConfig[disruption.type] || typeConfig.weather;
        const Icon = config.icon;
        return (
          <motion.div
            key={disruption.id}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, x: 50 }}
            transition={{ duration: 0.3 }}
            className={`flex items-start gap-3 p-4 rounded-xl border mb-3 ${config.bgClass}`}
          >
            <div className="flex items-center gap-2 shrink-0">
              <AlertCircle className={`w-4 h-4 ${config.iconClass}`} />
              <Icon className={`w-5 h-5 ${config.iconClass}`} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <p className={`font-semibold text-sm ${config.textClass}`}>{config.label} — Severity {disruption.severity}/5</p>
              </div>
              <p className={`text-sm mt-0.5 ${config.textClass} opacity-90`}>{disruption.description}</p>
              {disruption.affectedAreas?.length > 0 && (
                <p className={`text-xs mt-1 ${config.textClass} opacity-70`}>Areas: {disruption.affectedAreas.join(', ')}</p>
              )}
              <p className={`text-xs mt-1 ${config.textClass} opacity-70`}>{disruption.affectedWorkers} workers affected • Coverage auto-activated</p>
            </div>
            {onDismiss && (
              <button onClick={() => onDismiss(disruption.id)} className={`shrink-0 p-1 rounded-lg hover:bg-black/10 transition-colors ${config.textClass}`}>
                <X className="w-4 h-4" />
              </button>
            )}
          </motion.div>
        );
      })}
    </AnimatePresence>
  );
}
