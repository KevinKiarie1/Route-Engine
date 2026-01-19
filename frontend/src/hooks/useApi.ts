import useSWR from 'swr';
import type { DashboardOverview, ChartsData, RecentActivitiesResponse } from '@/types';

const API_BASE = '/api/v1/dashboard';

const fetcher = async <T>(url: string): Promise<T> => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
};

export function useDashboardOverview() {
  const { data, error, isLoading, mutate } = useSWR<DashboardOverview>(
    `${API_BASE}/overview`,
    fetcher,
    {
      refreshInterval: 30000, // Refresh every 30 seconds
      revalidateOnFocus: true,
      dedupingInterval: 5000,
    }
  );

  return {
    overview: data,
    isLoading,
    isError: error,
    refresh: mutate,
  };
}

export function useChartsData() {
  const { data, error, isLoading, mutate } = useSWR<ChartsData>(
    `${API_BASE}/charts`,
    fetcher,
    {
      refreshInterval: 60000, // Refresh every minute
      revalidateOnFocus: true,
    }
  );

  return {
    charts: data,
    isLoading,
    isError: error,
    refresh: mutate,
  };
}

export function useRecentActivities(limit: number = 20) {
  const { data, error, isLoading, mutate } = useSWR<RecentActivitiesResponse>(
    `${API_BASE}/recent-activities?limit=${limit}`,
    fetcher,
    {
      refreshInterval: 15000, // Refresh every 15 seconds
      revalidateOnFocus: true,
    }
  );

  return {
    activities: data,
    isLoading,
    isError: error,
    refresh: mutate,
  };
}

export async function refreshAllData() {
  const endpoints = ['/overview', '/charts', '/recent-activities'];
  await Promise.all(
    endpoints.map((endpoint) => 
      fetch(`${API_BASE}${endpoint}`).catch(() => null)
    )
  );
}
