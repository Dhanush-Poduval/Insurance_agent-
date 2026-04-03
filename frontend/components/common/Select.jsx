'use client';
import React from 'react';

export function Select({ label, error, options = [], className = '', id, ...props }) {
  const selectId = id || label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      {label && (
        <label htmlFor={selectId} className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <select
        id={selectId}
        className={`w-full rounded-lg border px-3 py-2 text-sm bg-white dark:bg-gray-800 dark:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 ${error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 dark:border-gray-600'}`}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
