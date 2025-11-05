interface QuickDateButtonsProps {
  onTodayClick: () => void;
  onTomorrowClick: () => void;
  disabled: boolean;
}

export const QuickDateButtons = ({ onTodayClick, onTomorrowClick, disabled }: QuickDateButtonsProps) => {
  if (disabled) {
    return null;
  }

  return (
    <div className="flex gap-3 justify-end">
      <button
        onClick={onTodayClick}
        className="px-6 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm hover:bg-gray-50 transition-colors"
      >
        Hoy
      </button>
      <button
        onClick={onTomorrowClick}
        className="px-6 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 text-sm hover:bg-gray-50 transition-colors"
      >
        Mañana
      </button>
    </div>
  );
};
