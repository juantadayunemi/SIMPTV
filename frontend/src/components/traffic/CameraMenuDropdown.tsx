import React, { useState, useRef, useEffect } from 'react';
import { Video, Link, Camera, Settings } from 'lucide-react';

interface CameraMenuDropdownProps {
  onConnectPath: () => void;
  onConnectUrl: () => void;
  onConnectCamera: () => void;
  onConfigure: () => void;
}

export const CameraMenuDropdown: React.FC<CameraMenuDropdownProps> = ({
  onConnectPath,
  onConnectUrl,
  onConnectCamera,
  onConfigure,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleMenuClick = (action: () => void) => {
    action();
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={(e) => {
          e.stopPropagation();
          setIsOpen(!isOpen);
        }}
        className="p-1 hover:bg-gray-100 rounded transition-colors"
      >
        <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 bottom-full mb-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleMenuClick(onConnectPath);
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-3"
          >
            <Video className="w-4 h-4 text-blue-500" />
            <span>Conectar (Path)</span>
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              handleMenuClick(onConnectUrl);
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-3"
          >
            <Link className="w-4 h-4 text-green-500" />
            <span>Conectar (URL)</span>
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              handleMenuClick(onConnectCamera);
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-3"
          >
            <Camera className="w-4 h-4 text-purple-500" />
            <span>Conectar (Cámara)</span>
          </button>

          <div className="border-t border-gray-100 my-1"></div>

          <button
            onClick={(e) => {
              e.stopPropagation();
              handleMenuClick(onConfigure);
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-50 flex items-center space-x-3"
          >
            <Settings className="w-4 h-4 text-gray-500" />
            <span>Configurar</span>
          </button>
        </div>
      )}
    </div>
  );
};

export default CameraMenuDropdown;
