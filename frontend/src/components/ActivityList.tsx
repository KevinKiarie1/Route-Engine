import { motion } from 'framer-motion';
import { Package, MapPin, Building2, Clock } from 'lucide-react';
import type { RecentActivity } from '@/types';
import { formatTimeAgo } from '@/utils/formatters';

const iconMap = {
  order: Package,
  route: MapPin,
  outlet: Building2,
};

const actionColors: Record<string, string> = {
  created: 'bg-blue-100 text-blue-700',
  updated: 'bg-yellow-100 text-yellow-700',
  completed: 'bg-red-100 text-red-700',
  delivered: 'bg-rose-100 text-rose-700',
  started: 'bg-cyan-100 text-cyan-700',
};

const typeColors: Record<string, string> = {
  order: 'bg-purple-100 text-purple-600',
  route: 'bg-red-100 text-red-600',
  outlet: 'bg-blue-100 text-blue-600',
};

interface ActivityItemProps {
  activity: RecentActivity;
  index: number;
}

function ActivityItem({ activity, index }: ActivityItemProps) {
  const Icon = iconMap[activity.type] || Package;
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ x: 4, backgroundColor: 'rgba(249, 250, 251, 1)' }}
      className="flex items-center gap-4 p-3 rounded-xl cursor-pointer transition-colors"
    >
      <motion.div 
        whileHover={{ scale: 1.1, rotate: 5 }}
        className={`p-2.5 rounded-xl ${typeColors[activity.type]}`}
      >
        <Icon className="w-5 h-5" />
      </motion.div>
      
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-900 truncate">
          {activity.description}
        </p>
        <div className="flex items-center gap-2 mt-0.5">
          <Clock className="w-3 h-3 text-gray-400" />
          <span className="text-xs text-gray-500">
            {formatTimeAgo(activity.timestamp)}
          </span>
        </div>
      </div>
      
      <span className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${
        actionColors[activity.action] || 'bg-gray-100 text-gray-700'
      }`}>
        {activity.action}
      </span>
    </motion.div>
  );
}

interface ActivityListProps {
  activities: RecentActivity[];
  delay?: number;
}

export function ActivityList({ activities, delay = 0 }: ActivityListProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.1, duration: 0.5 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          Recent Activities
        </h3>
        <span className="text-xs text-gray-400">
          {activities.length} items
        </span>
      </div>
      
      <div className="space-y-1 max-h-[400px] overflow-y-auto">
        {activities.length > 0 ? (
          activities.map((activity, index) => (
            <ActivityItem 
              key={`${activity.type}-${activity.id}`} 
              activity={activity} 
              index={index}
            />
          ))
        ) : (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Clock className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-gray-500">No recent activities</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export function ActivityListSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="h-4 w-32 shimmer rounded mb-4" />
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-center gap-4 p-3">
            <div className="w-10 h-10 shimmer rounded-xl" />
            <div className="flex-1">
              <div className="h-4 w-48 shimmer rounded mb-2" />
              <div className="h-3 w-24 shimmer rounded" />
            </div>
            <div className="h-6 w-16 shimmer rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}
