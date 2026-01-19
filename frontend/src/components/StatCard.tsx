import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';
import type { StatCardProps } from '@/types';
import { bgColors, textColors, gradients } from '@/utils/colors';

export function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  trend, 
  color,
  delay = 0 
}: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.1, duration: 0.5 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
      className="relative bg-white rounded-2xl p-6 shadow-sm border border-gray-100 overflow-hidden group cursor-pointer"
    >
      {/* Background gradient on hover */}
      <div className={`absolute inset-0 bg-gradient-to-br ${gradients[color]} opacity-0 group-hover:opacity-5 transition-opacity duration-300`} />
      
      {/* Decorative corner */}
      <div className={`absolute -top-10 -right-10 w-24 h-24 bg-gradient-to-br ${gradients[color]} opacity-10 rounded-full blur-2xl group-hover:opacity-20 transition-opacity`} />
      
      <div className="relative flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <motion.p 
            key={value.toString()}
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="text-3xl font-bold text-gray-900 tracking-tight"
          >
            {value}
          </motion.p>
          
          {subtitle && (
            <div className="flex items-center gap-2 mt-2">
              <span className={`text-sm font-medium ${textColors[color]}`}>
                {subtitle}
              </span>
              {trend && (
                <span className={`flex items-center gap-0.5 text-xs font-medium ${
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {trend.isPositive ? (
                    <TrendingUp className="w-3 h-3" />
                  ) : (
                    <TrendingDown className="w-3 h-3" />
                  )}
                  {trend.value}%
                </span>
              )}
            </div>
          )}
        </div>
        
        <motion.div 
          whileHover={{ scale: 1.1, rotate: 5 }}
          className={`p-3 rounded-xl ${bgColors[color]} ${textColors[color]}`}
        >
          {icon}
        </motion.div>
      </div>
    </motion.div>
  );
}

export function StatCardSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="h-4 w-24 shimmer rounded mb-2" />
          <div className="h-9 w-20 shimmer rounded mb-2" />
          <div className="h-4 w-16 shimmer rounded" />
        </div>
        <div className="w-12 h-12 shimmer rounded-xl" />
      </div>
    </div>
  );
}
