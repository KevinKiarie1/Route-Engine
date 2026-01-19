import { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Building2, 
  Package, 
  MapPin, 
  Boxes, 
  Truck,
  LayoutDashboard,
  BarChart3,
  Activity
} from 'lucide-react';
import { 
  Header,
  StatCard,
  StatCardSkeleton,
  MetricCard,
  MetricCardSkeleton,
  DeliveryTrendsChart,
  OrderStatusChart,
  RouteStatusChart,
  OutletPriorityChart,
  ChartSkeleton,
  ActivityList,
  ActivityListSkeleton,
  RouteList,
  RouteListSkeleton
} from '@/components';
import { useDashboardOverview, useChartsData, useRecentActivities } from '@/hooks/useApi';
import { formatNumber, formatPercentage, formatWeight, formatDistance, formatDuration } from '@/utils/formatters';
import type { TabType } from '@/types';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  const { overview, isLoading: overviewLoading, refresh: refreshOverview } = useDashboardOverview();
  const { charts, isLoading: chartsLoading, refresh: refreshCharts } = useChartsData();
  const { activities, isLoading: activitiesLoading, refresh: refreshActivities } = useRecentActivities();

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await Promise.all([refreshOverview(), refreshCharts(), refreshActivities()]);
    setTimeout(() => setIsRefreshing(false), 500);
  }, [refreshOverview, refreshCharts, refreshActivities]);

  const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: 'overview', label: 'Overview', icon: <LayoutDashboard className="w-4 h-4" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'activities', label: 'Activities', icon: <Activity className="w-4 h-4" /> },
  ];

  return (
    <div className="min-h-screen">
      <Header 
        lastUpdated={overview?.generated_at ? new Date(overview.generated_at).toLocaleTimeString() : null}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex items-center gap-2 mb-8 p-1 bg-white rounded-xl shadow-sm border border-gray-100 w-fit">
          {tabs.map((tab) => (
            <motion.button
              key={tab.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-red-500 to-rose-600 text-white shadow-lg shadow-red-500/30'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </motion.button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Stats Grid */}
              <section className="mb-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-6 bg-gradient-to-b from-red-500 to-rose-600 rounded-full" />
                  System Overview
                </h2>
                
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {overviewLoading ? (
                    Array.from({ length: 5 }).map((_, i) => (
                      <StatCardSkeleton key={i} />
                    ))
                  ) : overview ? (
                    <>
                      <StatCard
                        title="Total Outlets"
                        value={formatNumber(overview.stats.total_outlets)}
                        subtitle={`${overview.stats.active_outlets} active`}
                        icon={<Building2 className="w-6 h-6" />}
                        color="blue"
                        delay={0}
                      />
                      <StatCard
                        title="Total Orders"
                        value={formatNumber(overview.stats.total_orders)}
                        subtitle={`${overview.stats.pending_orders} pending`}
                        icon={<Package className="w-6 h-6" />}
                        color="purple"
                        delay={1}
                      />
                      <StatCard
                        title="Total Routes"
                        value={formatNumber(overview.stats.total_routes)}
                        subtitle={`${overview.stats.active_routes} active`}
                        icon={<MapPin className="w-6 h-6" />}
                        color="green"
                        delay={2}
                      />
                      <StatCard
                        title="Total Boxes"
                        value={formatNumber(overview.stats.total_boxes)}
                        subtitle={`${overview.box_metrics.boxes_in_transit} in transit`}
                        icon={<Boxes className="w-6 h-6" />}
                        color="orange"
                        delay={3}
                      />
                      <StatCard
                        title="Delivery Rate"
                        value={formatPercentage(overview.delivery_metrics.delivery_success_rate)}
                        subtitle={`${overview.delivery_metrics.on_time_delivery_rate}% on-time`}
                        icon={<Truck className="w-6 h-6" />}
                        color="cyan"
                        delay={4}
                      />
                    </>
                  ) : null}
                </div>
              </section>

              {/* Metrics Cards */}
              <section className="mb-8">
                <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <span className="w-1.5 h-6 bg-gradient-to-b from-blue-500 to-indigo-600 rounded-full" />
                  Performance Metrics
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {overviewLoading ? (
                    Array.from({ length: 3 }).map((_, i) => (
                      <MetricCardSkeleton key={i} />
                    ))
                  ) : overview ? (
                    <>
                      <MetricCard
                        title="Delivery"
                        icon={<Truck className="w-5 h-5" />}
                        delay={5}
                        metrics={[
                          { 
                            label: 'Delivered Today', 
                            value: formatNumber(overview.delivery_metrics.orders_delivered_today),
                            color: 'text-red-600'
                          },
                          { 
                            label: 'Pending Today', 
                            value: formatNumber(overview.delivery_metrics.orders_pending_today),
                            color: 'text-yellow-600'
                          },
                          { 
                            label: 'Avg. Time', 
                            value: formatDuration(overview.delivery_metrics.avg_delivery_time_minutes),
                          },
                          { 
                            label: 'Success Rate', 
                            value: formatPercentage(overview.delivery_metrics.delivery_success_rate),
                            color: 'text-red-600'
                          },
                        ]}
                      />
                      <MetricCard
                        title="Routes"
                        icon={<MapPin className="w-5 h-5" />}
                        delay={6}
                        metrics={[
                          { label: 'Avg. Stops', value: overview.route_metrics.avg_stops_per_route },
                          { label: 'Completion', value: formatPercentage(overview.route_metrics.avg_route_completion) },
                          { label: 'Avg. Distance', value: formatDistance(overview.route_metrics.avg_distance_km) },
                          { 
                            label: 'Fuel Efficiency', 
                            value: overview.route_metrics.avg_fuel_efficiency 
                              ? `${overview.route_metrics.avg_fuel_efficiency} km/L` 
                              : 'N/A' 
                          },
                        ]}
                      />
                      <MetricCard
                        title="Boxes"
                        icon={<Boxes className="w-5 h-5" />}
                        delay={7}
                        metrics={[
                          { label: 'Total Weight', value: formatWeight(overview.box_metrics.total_weight_kg) },
                          { label: 'Avg. Weight', value: `${overview.box_metrics.avg_box_weight_kg}kg` },
                          { label: 'Avg. Fill', value: formatPercentage(overview.box_metrics.avg_fill_percentage) },
                          { 
                            label: 'Special Handling', 
                            value: `${overview.box_metrics.fragile_boxes + overview.box_metrics.refrigerated_boxes}`,
                            color: 'text-orange-600'
                          },
                        ]}
                      />
                    </>
                  ) : null}
                </div>
              </section>

              {/* Quick Charts */}
              <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {chartsLoading ? (
                  <>
                    <ChartSkeleton />
                    <ChartSkeleton />
                  </>
                ) : charts ? (
                  <>
                    <DeliveryTrendsChart data={charts.delivery_trends} delay={8} />
                    <OrderStatusChart data={charts.order_status_distribution} delay={9} />
                  </>
                ) : null}
              </section>
            </motion.div>
          )}

          {activeTab === 'analytics' && (
            <motion.div
              key="analytics"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                {chartsLoading ? (
                  Array.from({ length: 4 }).map((_, i) => (
                    <ChartSkeleton key={i} />
                  ))
                ) : charts ? (
                  <>
                    <DeliveryTrendsChart data={charts.delivery_trends} delay={0} />
                    <OrderStatusChart data={charts.order_status_distribution} delay={1} />
                    <RouteStatusChart data={charts.route_status_distribution} delay={2} />
                    <OutletPriorityChart data={charts.outlet_priority_distribution} delay={3} />
                  </>
                ) : null}
              </section>

              <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {chartsLoading ? (
                  <RouteListSkeleton />
                ) : charts ? (
                  <RouteList routes={charts.top_routes} delay={4} />
                ) : null}
                
                {activitiesLoading ? (
                  <ActivityListSkeleton />
                ) : activities ? (
                  <ActivityList activities={activities.activities} delay={5} />
                ) : null}
              </section>
            </motion.div>
          )}

          {activeTab === 'activities' && (
            <motion.div
              key="activities"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {activitiesLoading ? (
                  <>
                    <ActivityListSkeleton />
                    <RouteListSkeleton />
                  </>
                ) : (
                  <>
                    {activities && <ActivityList activities={activities.activities} delay={0} />}
                    {charts && <RouteList routes={charts.top_routes} delay={1} />}
                  </>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-500">
              © 2026 Route Engine Dashboard · Farmer's Choice Logistics
            </p>
            <div className="flex items-center gap-4">
              <a href="/docs" className="text-sm text-gray-500 hover:text-red-600 transition-colors">
                API Docs
              </a>
              <a href="/health" className="text-sm text-gray-500 hover:text-red-600 transition-colors">
                Health Status
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
