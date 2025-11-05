import { ChevronDown } from 'lucide-react';

interface CustomSelectProps {
  value: number | string;
  onChange: (value: string) => void;
  options: Array<{ value: number | string; label: string }>;
  placeholder?: string;
}

export const CustomSelect = ({ value, onChange, options, placeholder }: CustomSelectProps) => {
  return (
    <div className="relative">
      <select
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value)}
        className="appearance-none w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
      >

        <option value={""}>{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-5 h-5 pointer-events-none text-gray-400" />
    </div>
  );
};