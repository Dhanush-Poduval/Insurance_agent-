'use client';
import React from 'react';

export function ProgressBar({ value = 0, label, variant = 'info', showLabel = true, className = '' }) {
  const variants = {
    success: 'bg-green-500',
    warning: 'bg-orange-500',
    danger: 'bg-red-500',
    info: 'bg-blue-500',
    primary: 'bg-blue-600',
  };

  const clamped = Math.min(100, Math.max(0, value));

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      {(label || showLabel) && (
        <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400">
          {label && <span>{label}</span>}
          {showLabel && <span className="font-medium">{clamped}%</span>}
        </div>
      )}
      <div className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${variants[variant] || variants.info}`}
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
