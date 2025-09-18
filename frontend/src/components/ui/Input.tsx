import React from 'react';

interface InputProps {
  type?: 'text' | 'email' | 'password' | 'number' | 'tel' | 'url';
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  id?: string;
  name?: string;
}

export const Input: React.FC<InputProps> = ({
  type = 'text',
  value,
  onChange,
  placeholder,
  label,
  error,
  required = false,
  disabled = false,
  className = '',
  id,
  name,
}) => {
  const inputClasses = `
    w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors
    ${error ? 'border-red-500' : 'border-gray-300'}
    ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
    ${className}
  `.trim();

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        className={inputClasses}
        id={id}
        name={name}
      />
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};

interface SelectProps {
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLSelectElement>) => void;
  options: Array<{ value: string; label: string }>;
  placeholder?: string;
  label?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
  id?: string;
  name?: string;
}

export const Select: React.FC<SelectProps> = ({
  value,
  onChange,
  options,
  placeholder = 'Select an option',
  label,
  error,
  required = false,
  disabled = false,
  className = '',
  id,
  name,
}) => {
  const selectClasses = `
    w-full px-3 py-2 border rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors
    ${error ? 'border-red-500' : 'border-gray-300'}
    ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
    ${className}
  `.trim();

  return (
    <div className="space-y-1">
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      <select
        value={value}
        onChange={onChange}
        required={required}
        disabled={disabled}
        className={selectClasses}
        id={id}
        name={name}
      >
        <option value="">{placeholder}</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="text-sm text-red-600">{error}</p>
      )}
    </div>
  );
};