// Color utilities and constants

export const statusColors: Record<string, string> = {
  // Order statuses
  pending: '#f59e0b',
  confirmed: '#3b82f6',
  packing: '#8b5cf6',
  packed: '#6366f1',
  in_transit: '#0891b2',
  delivered: '#10b981',
  partial: '#84cc16',
  cancelled: '#ef4444',
  returned: '#f97316',
  // Route statuses
  draft: '#9ca3af',
  planned: '#3b82f6',
  assigned: '#6366f1',
  in_progress: '#0891b2',
  completed: '#10b981',
};

export const priorityColors: Record<string, string> = {
  CRITICAL: '#ef4444',
  HIGH: '#f97316',
  MEDIUM: '#f59e0b',
  LOW: '#84cc16',
  DEFERRED: '#6b7280',
};

export const chartColors = {
  primary: '#dc2626',
  primaryLight: '#ef4444',
  primaryDark: '#b91c1c',
  success: '#ef4444',
  warning: '#f59e0b',
  danger: '#7f1d1d',
  info: '#3b82f6',
  purple: '#8b5cf6',
  pink: '#ec4899',
  cyan: '#06b6d4',
  gray: '#6b7280',
};

export const gradients = {
  green: 'from-red-500 to-rose-600',
  blue: 'from-blue-500 to-indigo-600',
  purple: 'from-purple-500 to-violet-600',
  orange: 'from-orange-500 to-amber-600',
  pink: 'from-pink-500 to-rose-600',
  cyan: 'from-cyan-500 to-teal-600',
};

export const bgColors = {
  green: 'bg-red-100',
  blue: 'bg-blue-100',
  purple: 'bg-purple-100',
  orange: 'bg-orange-100',
  pink: 'bg-pink-100',
  cyan: 'bg-cyan-100',
};

export const textColors = {
  green: 'text-red-600',
  blue: 'text-blue-600',
  purple: 'text-purple-600',
  orange: 'text-orange-600',
  pink: 'text-pink-600',
  cyan: 'text-cyan-600',
};
