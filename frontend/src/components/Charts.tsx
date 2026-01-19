import { motion } from 'framer-motion';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import { statusColors, priorityColors, chartColors } from '@/utils/colors';
import { formatShortDate } from '@/utils/formatters';
import type { 
  DeliveryTrend, 
  OrderStatusDistribution, 
  RouteStatusDistribution,
  OutletPriorityDistribution 
} from '@/types';

interface ChartCardProps {
  title: string;
  children: React.ReactNode;
  delay?: number;
}

function ChartCard({ title, children, delay = 0 }: ChartCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: delay * 0.1, duration: 0.5 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
        {title}
      </h3>
      <div className="h-72">{children}</div>
    </motion.div>
  );
}

interface DeliveryTrendsChartProps {
  data: DeliveryTrend[];
  delay?: number;
}

export function DeliveryTrendsChart({ data, delay = 0 }: DeliveryTrendsChartProps) {
  const formattedData = data.map((d) => ({
    ...d,
    date: formatShortDate(d.date),
  }));

  return (
    <ChartCard title="Delivery Trends (7 Days)" delay={delay}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={formattedData}>
          <defs>
            <linearGradient id="deliveredGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColors.success} stopOpacity={0.3} />
              <stop offset="95%" stopColor={chartColors.success} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="pendingGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColors.warning} stopOpacity={0.3} />
              <stop offset="95%" stopColor={chartColors.warning} stopOpacity={0} />
            </linearGradient>
            <linearGradient id="cancelledGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={chartColors.danger} stopOpacity={0.3} />
              <stop offset="95%" stopColor={chartColors.danger} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis 
            dataKey="date" 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 12 }}
          />
          <YAxis 
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 12 }}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
            }}
          />
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
            iconType="circle"
          />
          <Area
            type="monotone"
            dataKey="delivered"
            name="Delivered"
            stroke={chartColors.success}
            strokeWidth={2}
            fill="url(#deliveredGradient)"
          />
          <Area
            type="monotone"
            dataKey="pending"
            name="Pending"
            stroke={chartColors.warning}
            strokeWidth={2}
            fill="url(#pendingGradient)"
          />
          <Area
            type="monotone"
            dataKey="cancelled"
            name="Cancelled"
            stroke={chartColors.danger}
            strokeWidth={2}
            fill="url(#cancelledGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

interface OrderStatusChartProps {
  data: OrderStatusDistribution[];
  delay?: number;
}

export function OrderStatusChart({ data, delay = 0 }: OrderStatusChartProps) {
  const RADIAN = Math.PI / 180;
  
  const renderCustomLabel = ({ 
    cx, 
    cy, 
    midAngle, 
    innerRadius, 
    outerRadius, 
    percent 
  }: {
    cx: number;
    cy: number;
    midAngle: number;
    innerRadius: number;
    outerRadius: number;
    percent: number;
  }) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    if (percent < 0.05) return null;

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={12}
        fontWeight={600}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <ChartCard title="Order Status Distribution" delay={delay}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={100}
            innerRadius={60}
            dataKey="count"
            nameKey="status"
            paddingAngle={2}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={statusColors[entry.status] || chartColors.gray}
                stroke="white"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
            }}
            formatter={(value: number, name: string) => [value, name.replace('_', ' ')]}
          />
          <Legend 
            layout="vertical" 
            align="right" 
            verticalAlign="middle"
            iconType="circle"
            formatter={(value) => (
              <span className="text-gray-600 text-sm capitalize">
                {value.replace('_', ' ')}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

interface RouteStatusChartProps {
  data: RouteStatusDistribution[];
  delay?: number;
}

export function RouteStatusChart({ data, delay = 0 }: RouteStatusChartProps) {
  return (
    <ChartCard title="Route Status Distribution" delay={delay}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" horizontal={false} />
          <XAxis 
            type="number"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 12 }}
          />
          <YAxis 
            type="category"
            dataKey="status"
            axisLine={false}
            tickLine={false}
            tick={{ fill: '#64748b', fontSize: 12 }}
            width={100}
            tickFormatter={(value) => value.replace('_', ' ')}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
            }}
            formatter={(value: number) => [value, 'Routes']}
            labelFormatter={(label) => label.replace('_', ' ')}
          />
          <Bar 
            dataKey="count" 
            radius={[0, 8, 8, 0]}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={statusColors[entry.status] || chartColors.gray}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

interface OutletPriorityChartProps {
  data: OutletPriorityDistribution[];
  delay?: number;
}

export function OutletPriorityChart({ data, delay = 0 }: OutletPriorityChartProps) {
  return (
    <ChartCard title="Outlet Priority Distribution" delay={delay}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            outerRadius={100}
            dataKey="count"
            nameKey="priority"
            paddingAngle={2}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={priorityColors[entry.priority] || chartColors.gray}
                stroke="white"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: 'white',
              border: 'none',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0,0,0,0.1)',
            }}
          />
          <Legend 
            layout="vertical" 
            align="right" 
            verticalAlign="middle"
            iconType="circle"
            formatter={(value) => (
              <span className="text-gray-600 text-sm">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </ChartCard>
  );
}

export function ChartSkeleton() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <div className="h-4 w-40 shimmer rounded mb-4" />
      <div className="h-72 shimmer rounded-xl" />
    </div>
  );
}
