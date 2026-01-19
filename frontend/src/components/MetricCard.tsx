import { motion } from 'framer-motion';
import type { MetricItemProps } from '@/types';

interface MetricCardProps {
  title: string;
  icon: React.ReactNode;
  metrics: MetricItemProps[];
  delay?: number;
}

export function MetricCard({ title, icon, metrics, delay = 0 }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.1, duration: 0.5 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100 card-hover"
    >
      <div className="flex items-center gap-3 mb-5">
        <div className="p-2 bg-gray-100 rounded-lg text-gray-600">
          {icon}
        </div>
        <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider">
          {title}
        </h3>
      </div>
      
      <div className="space-y-4">
        {metrics.map((metric, index) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: (delay + index * 0.5) * 0.1 }}
            className="flex justify-between items-center group"
          >
            <span className="text-gray-600 group-hover:text-gray-900 transition-colors">
              {metric.label}
            </span>
            <span className={`font-semibold ${metric.color || 'text-gray-900'}`}>
              {metric.value}
            </span>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

export function MetricCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 shimmer rounded-lg" />
        <div className="h-4 w-20 shimmer rounded" />
      </div>
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="flex justify-between">
            <div className="h-4 w-24 shimmer rounded" />
            <div className="h-4 w-16 shimmer rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
