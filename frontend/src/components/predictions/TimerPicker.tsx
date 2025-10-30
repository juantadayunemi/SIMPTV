import React, { useState, useRef, useEffect } from "react";
import { Clock } from "lucide-react";

export interface TimePickerProps {
  time: string;
  onTimeChange: (time: string) => void;
}

export default function TimePicker({ time, onTimeChange }: TimePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedHour, setSelectedHour] = useState("00");
  const [selectedMinute, setSelectedMinute] = useState("00");
  const dropdownRef = useRef<HTMLDivElement>(null);

  const hours = Array.from({ length: 24 }, (_, i) =>
    i.toString().padStart(2, "0")
  );
  const minutes = ["00", "10", "20", "30", "40", "50"];

  useEffect(() => {
    if (time) {
      const [hour, minute] = time.split(":");
      setSelectedHour(hour || "00");
      setSelectedMinute(minute || "00");
    }
  }, [time]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleHourClick = (hour: string) => {
    setSelectedHour(hour);
    onTimeChange(`${hour}:${selectedMinute}`);
  };

  const handleMinuteClick = (minute: string) => {
    setSelectedMinute(minute);
    onTimeChange(`${selectedHour}:${minute}`);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="flex items-center gap-2">
        <Clock size={20} className="text-gray-400" />
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white min-w-[120px] text-left"
        >
          {time}
        </button>
      </div>

      {isOpen && (
        <div className="absolute top-full mt-2 bg-white border border-gray-300 rounded-lg shadow-lg z-10 flex">
          <div className="border-r border-gray-200">
            <div
              className="max-h-60 overflow-y-auto scrollbar-hide"
              style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
            >
              {hours.map((hour) => (
                <button
                  key={hour}
                  onClick={() => handleHourClick(hour)}
                  className={`w-full px-5 py-2 text-center hover:bg-blue-50 ${
                    selectedHour === hour
                      ? "bg-blue-100 text-blue-600 font-medium"
                      : ""
                  }`}
                >
                  {hour}
                </button>
              ))}
            </div>
          </div>

          <div>
            <div>
              {minutes.map((minute) => (
                <button
                  key={minute}
                  onClick={() => handleMinuteClick(minute)}
                  className={`w-full px-6 py-2 text-left hover:bg-blue-50 ${
                    selectedMinute === minute
                      ? "bg-blue-100 text-blue-600 font-medium"
                      : ""
                  }`}
                >
                  {minute}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
