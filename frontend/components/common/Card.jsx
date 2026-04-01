'use client';
import React from 'react';

export function Card({ variant = 'default', className = '', children, ...props }) {
  const variants = {
    default: 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700',
    elevated: 'bg-white dark:bg-gray-800 shadow-lg',
    outlined: 'bg-transparent border-2 border-gray-300 dark:border-gray-600',
  };

  return (
    <div
      className={`rounded-xl p-5 ${variants[variant] || variants.default} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
