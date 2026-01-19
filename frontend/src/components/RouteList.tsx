import { motion } from 'framer-motion';
import { TrendingUp, MapPin, Target } from 'lucide-react';
import type { RouteEfficiency } from '@/types';
import { formatDistance } from '@/utils/formatters';

interface RouteItemProps {
  route: RouteEfficiency;
  index: number;
}

function RouteItem({ route, index }: RouteItemProps) {
  const getCompletionColor = (rate: number) => {
    if (rate >= 80) return 'text-red-600 bg-red-100';
    if (rate >= 50) return 'text-yellow-600 bg-yellow-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getProgressColor = (rate: number) => {
    if (rate >= 80) return 'bg-gradient-to-r from-red-500 to-rose-500';
    if (rate >= 50) return 'bg-gradient-to-r from-yellow-500 to-amber-500';
    return 'bg-gradient-to-r from-gray-500 to-gray-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ x: -4, backgroundColor: 'rgba(249, 250, 251, 1)' }}
      className="p-4 rounded-xl cursor-pointer transition-colors"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-red-100 text-red-600 rounded-lg">
            <MapPin className="w-4 h-4" />
          </div>
          <div>
            <p className="font-semibold text-gray-900">{route.route_code}</p>
            <p className="text-xs text-gray-500">
              {route.completed_stops}/{route.planned_stops} stops
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <span className={`inline-flex items-center px-2.5 py-1 rounded-lg text-sm font-semibold ${
            getCompletionColor(route.completion_rate)
          }`}>
            {route.completion_rate}%
          </span>
          {route.distance_km && (
            <p className="text-xs text-gray-500 mt-1">
              {formatDistance(route.distance_km)}
            </p>
          )}
        </div>
      </div>
      
      {/* Progress bar */}
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${route.completion_rate}%` }}
          transition={{ delay: index * 0.05 + 0.2, duration: 0.8, ease: 'easeOut' }}
          className={`h-full rounded-full ${getProgressColor(route.completion_rate)}`}
        />
      </div>
    </motion.div>
  );
}

interface RouteListProps {
  routes: RouteEfficiency[];
  delay?: number;
}

export function RouteList({ routes, delay = 0 }: RouteListProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.1, duration: 0.5 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          Recent Routes Performance
        </h3>
        <div className="flex items-center gap-1 text-red-600">
          <TrendingUp className="w-4 h-4" />
          <span className="text-xs font-medium">Live</span>
        </div>
      </div>
      
      <div className="space-y-2 max-h-[400px] overflow-y-auto">
        {routes.length > 0 ? (
          routes.map((route, index) => (
            <RouteItem key={route.route_code} route={route} index={index} />
          ))
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Target className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-500">No routes available</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export function RouteListSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="h-4 w-40 shimmer rounded mb-4" />
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 shimmer rounded-lg" />
                <div>
                  <div className="h-4 w-24 shimmer rounded mb-1" />
                  <div className="h-3 w-16 shimmer rounded" />
                </div>
              </div>
              <div className="h-6 w-14 shimmer rounded-lg" />
            </div>
            <div className="h-2 shimmer rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}
