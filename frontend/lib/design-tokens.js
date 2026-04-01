export const colors = {
  primary: '#0066FF',
  primaryHover: '#0052CC',
  primaryLight: '#E3F2FD',
  success: '#00C853',
  successLight: '#E8F5E9',
  warning: '#FF9800',
  warningLight: '#FFF3E0',
  danger: '#F44336',
  dangerLight: '#FFEBEE',
  info: '#2196F3',
  infoLight: '#E3F2FD',
  background: '#F9FAFB',
  foreground: '#111827',
  cardBg: '#FFFFFF',
  gray: {
    50: '#F9FAFB',
    100: '#F3F4F6',
    200: '#E5E7EB',
    300: '#D1D5DB',
    400: '#9CA3AF',
    500: '#6B7280',
    600: '#4B5563',
    700: '#374151',
    800: '#1F2937',
    900: '#111827',
  },
};

export const typography = {
  fontSizes: { xs: '0.75rem', sm: '0.875rem', base: '1rem', lg: '1.125rem', xl: '1.25rem', '2xl': '1.5rem', '3xl': '1.875rem', '4xl': '2.25rem' },
  fontWeights: { normal: 400, medium: 500, semibold: 600, bold: 700 },
  lineHeights: { tight: 1.25, snug: 1.375, normal: 1.5, relaxed: 1.625 },
};

export const spacing = {
  0: '0', 1: '0.25rem', 2: '0.5rem', 3: '0.75rem', 4: '1rem', 5: '1.25rem',
  6: '1.5rem', 8: '2rem', 10: '2.5rem', 12: '3rem', 16: '4rem', 20: '5rem', 24: '6rem',
};

export const shadows = {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  base: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
};

export const transitions = {
  fast: '150ms ease-in-out',
  base: '200ms ease-in-out',
  slow: '300ms ease-in-out',
};

export const borderRadius = {
  sm: '0.25rem', base: '0.375rem', md: '0.5rem', lg: '0.75rem', xl: '1rem', full: '9999px',
};
