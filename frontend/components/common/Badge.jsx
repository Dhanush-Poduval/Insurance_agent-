'use client';
import React from 'react';

export function Badge({ variant = 'neutral', size = 'md', children, className = '' }) {
  const variants = {
    success: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    warning: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400',
    danger: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
    info: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    neutral: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
    primary: 'bg-blue-600 text-white',
  };
  const sizes = { sm: 'px-2 py-0.5 text-xs', md: 'px-2.5 py-1 text-sm', lg: 'px-3 py-1.5 text-base' };

  return (
    <span className={`inline-flex items-center font-medium rounded-full ${variants[variant] || variants.neutral} ${sizes[size]} ${className}`}>
      {children}
    </span>
  );
}
