import { format, formatDistanceToNow, parseISO } from 'date-fns';

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US').format(value);
}

export function formatPercentage(value: number): string {
  return `${value.toFixed(1)}%`;
}

export function formatWeight(kg: number): string {
  if (kg >= 1000) {
    return `${(kg / 1000).toFixed(1)}t`;
  }
  return `${kg.toFixed(1)}kg`;
}

export function formatDistance(km: number | null): string {
  if (km === null) return 'N/A';
  return `${km.toFixed(1)}km`;
}

export function formatDuration(minutes: number | null): string {
  if (minutes === null) return 'N/A';
  if (minutes < 60) return `${Math.round(minutes)}min`;
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  return `${hours}h ${mins}m`;
}

export function formatDate(isoString: string): string {
  try {
    return format(parseISO(isoString), 'MMM d, yyyy');
  } catch {
    return isoString;
  }
}

export function formatDateTime(isoString: string): string {
  try {
    return format(parseISO(isoString), 'MMM d, yyyy HH:mm');
  } catch {
    return isoString;
  }
}

export function formatTimeAgo(isoString: string): string {
  try {
    return formatDistanceToNow(parseISO(isoString), { addSuffix: true });
  } catch {
    return isoString;
  }
}

export function formatShortDate(isoString: string): string {
  try {
    return format(parseISO(isoString), 'MMM d');
  } catch {
    return isoString;
  }
}
