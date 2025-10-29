import React from "react";

interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg" | "df";
  color?: "primary" | "white" | "gray" | "default";
  className?: string;
  borderSize?: string;

}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = "df",
  color = "default",
  className = "",
}) => {
  const sizeClasses = {
    df: "h-20 w-20",
    sm: "h-4 w-4",
    md: "h-8 w-8",
    lg: "h-12 w-12",
  };

  const colorClasses = {
    default: "border-primary-600",
    primary: "text-blue-600",
    white: "text-white",
    gray: "text-gray-600",
  };

  return (
    
      <div className={`animate-spin rounded-full ${sizeClasses[size]} border-b-2 ${colorClasses[color]} mx-auto mb-4 ${className}`}></div>

  );
};

export default LoadingSpinner;
