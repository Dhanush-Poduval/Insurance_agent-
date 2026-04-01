'use client';
import React from 'react';

export function Button({ variant = 'primary', size = 'md', isLoading = false, icon, fullWidth = false, children, className = '', disabled, ...props }) {
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-900 dark:bg-gray-800 dark:text-gray-100',
    danger: 'bg-red-500 hover:bg-red-600 text-white',
    ghost: 'bg-transparent hover:bg-gray-100 text-blue-600 dark:hover:bg-gray-800',
    success: 'bg-green-600 hover:bg-green-700 text-white',
  };
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2 text-base', lg: 'px-6 py-3 text-lg' };

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed ${variants[variant] || variants.primary} ${sizes[size]} ${fullWidth ? 'w-full' : ''} ${className}`}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? <div className="animate-spin w-4 h-4 border-2 border-current border-t-transparent rounded-full" /> : icon}
      {children}
    </button>
  );
}
