// API Response Types

export interface OverviewStats {
  total_outlets: number;
  active_outlets: number;
  total_orders: number;
  pending_orders: number;
  orders_in_transit: number;
  delivered_orders: number;
  total_routes: number;
  active_routes: number;
  completed_routes: number;
  total_boxes: number;
}

export interface DeliveryMetrics {
  delivery_success_rate: number;
  avg_delivery_time_minutes: number | null;
  on_time_delivery_rate: number;
  orders_delivered_today: number;
  orders_pending_today: number;
}

export interface RouteMetrics {
  avg_stops_per_route: number;
  avg_route_completion: number;
  avg_distance_km: number | null;
  avg_fuel_efficiency: number | null;
  routes_in_progress: number;
  routes_completed_today: number;
}

export interface BoxMetrics {
  total_weight_kg: number;
  avg_box_weight_kg: number;
  avg_fill_percentage: number;
  boxes_in_transit: number;
  fragile_boxes: number;
  refrigerated_boxes: number;
}

export interface DashboardOverview {
  stats: OverviewStats;
  delivery_metrics: DeliveryMetrics;
  route_metrics: RouteMetrics;
  box_metrics: BoxMetrics;
  generated_at: string;
}

export interface OrderStatusDistribution {
  status: string;
  count: number;
  percentage: number;
}

export interface RouteStatusDistribution {
  status: string;
  count: number;
  percentage: number;
}

export interface OutletPriorityDistribution {
  priority: string;
  count: number;
  percentage: number;
}

export interface VehicleTypeDistribution {
  vehicle_type: string;
  count: number;
  total_capacity_kg: number;
}

export interface DeliveryTrend {
  date: string;
  delivered: number;
  pending: number;
  cancelled: number;
}

export interface RouteEfficiency {
  route_code: string;
  planned_stops: number;
  completed_stops: number;
  completion_rate: number;
  distance_km: number | null;
}

export interface ChartsData {
  order_status_distribution: OrderStatusDistribution[];
  route_status_distribution: RouteStatusDistribution[];
  outlet_priority_distribution: OutletPriorityDistribution[];
  vehicle_type_distribution: VehicleTypeDistribution[];
  delivery_trends: DeliveryTrend[];
  top_routes: RouteEfficiency[];
  generated_at: string;
}

export interface RecentActivity {
  id: number;
  type: 'order' | 'route' | 'outlet';
  action: string;
  description: string;
  timestamp: string;
}

export interface RecentActivitiesResponse {
  activities: RecentActivity[];
  total: number;
}

// UI Types

export interface StatCardProps {
  title: string;
  value: number | string;
  subtitle?: string;
  icon: React.ReactNode;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: 'green' | 'blue' | 'purple' | 'orange' | 'pink' | 'cyan';
  delay?: number;
}

export interface MetricItemProps {
  label: string;
  value: string | number;
  color?: string;
}

export type TabType = 'overview' | 'analytics' | 'activities';
