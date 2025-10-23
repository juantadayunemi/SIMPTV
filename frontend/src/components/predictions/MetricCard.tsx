interface MetricCardProps {
  value: string | number;
  label: string;
  color?: 'blue' | 'orange' | 'green';
}

export default function MetricCard({ value, label, color = 'blue' }: MetricCardProps) {
  const bgColors = {
    blue: 'bg-blue-50',
    orange: 'bg-orange-50',
    green: 'bg-green-50'
  };

  const textColors = {
    blue: 'text-blue-600',
    orange: 'text-orange-600',
    green: 'text-green-600'
  };

  return (
    <div className={`${bgColors[color]} rounded-lg p-6 flex flex-col items-center justify-center`}>
      <div className={`text-4xl font-bold ${textColors[color]}`}>
        {value}
      </div>
      <div className="text-sm text-gray-600 mt-2">{label}</div>
    </div>
  );
}
