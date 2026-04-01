'use client';
import React from 'react';

export function Input({ label, error, helperText, icon, className = '', id, ...props }) {
  const inputId = id || label?.toLowerCase().replace(/\s+/g, '-');

  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      {label && (
        <label htmlFor={inputId} className="text-sm font-medium text-gray-700 dark:text-gray-300">
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">{icon}</div>
        )}
        <input
          id={inputId}
          className={`w-full rounded-lg border px-3 py-2 text-sm transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white ${icon ? 'pl-9' : ''} ${error ? 'border-red-500 focus:ring-red-500' : 'border-gray-300 dark:border-gray-600'}`}
          {...props}
        />
      </div>
      {error && <p className="text-xs text-red-500">{error}</p>}
      {helperText && !error && <p className="text-xs text-gray-500">{helperText}</p>}
    </div>
  );
}
