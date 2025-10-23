import { useEffect } from "react";
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react";

export type ToastType = "success" | "error" | "warning" | "info";

export interface ToastProps {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
  onClose: (id: string) => void;
}

const Toast = ({ id, type, message, duration = 5000, onClose }: ToastProps) => {
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose(id);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [id, duration, onClose]);

  const configs = {
    success: {
      icon: CheckCircle,
      bgColor: "bg-green-50",
      borderColor: "border-green-500",
      iconColor: "text-green-600",
      textColor: "text-green-800",
    },
    error: {
      icon: AlertCircle,
      bgColor: "bg-red-50",
      borderColor: "border-red-500",
      iconColor: "text-red-600",
      textColor: "text-red-800",
    },
    warning: {
      icon: AlertTriangle,
      bgColor: "bg-orange-50",
      borderColor: "border-orange-500",
      iconColor: "text-orange-600",
      textColor: "text-orange-800",
    },
    info: {
      icon: Info,
      bgColor: "bg-blue-50",
      borderColor: "border-blue-500",
      iconColor: "text-blue-600",
      textColor: "text-blue-800",
    },
  };

  const config = configs[type];
  const Icon = config.icon;

  return (
    <div
      className={`${config.bgColor} ${config.borderColor} border-l-4 rounded-lg shadow-lg p-4 flex items-start gap-3 min-w-[320px] max-w-md animate-slide-in`}
      role="alert"
    >
      <Icon className={`${config.iconColor} flex-shrink-0 mt-0.5`} size={20} />
      <p className={`${config.textColor} text-sm flex-1 font-medium`}>
        {message}
      </p>
      <button
        onClick={() => onClose(id)}
        className={`${config.iconColor} hover:opacity-70 transition-opacity flex-shrink-0`}
        aria-label="Cerrar notificación"
      >
        <X size={18} />
      </button>
    </div>
  );
};

export default Toast;
