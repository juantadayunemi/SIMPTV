import { X, AlertCircle } from "lucide-react";
import { createPortal } from "react-dom";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onApply?: () => void;
  closeText?: string;
  applyText?: string;
  buttonClose?: boolean;
  buttonApply?: boolean;    
  placeholder?: string;
  type?: "warning" | "info";
}

export default function Modal({ isOpen, onClose, onApply, closeText, applyText, buttonClose, buttonApply, placeholder, type = "info" }: ModalProps) {
  if (!isOpen) return null;

  const handleClose = () => {
    onClose();
  };

  const handleApply = () => {
    if (onApply) onApply();
  };

  const ButtonsClass = {
    "warning": {"apply": "bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors", "close": "border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 hover:text-white transition-colors", "title": "text-red-700"},
    "info": {"apply": "bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors", "close": "border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 hover:text-white transition-colors", "title": "text-blue-700"},
  }


  return createPortal(
    <div className="fixed inset-0 flex flex-col items-center justify-center bg-black/85 backdrop-blur-sm z-[9999]">
      <div className="bg-white rounded-xl shadow-xl p-6 w-full max-w-md mx-4">

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <AlertCircle className={`w-5 h-5 ${ButtonsClass[type].title}`} />
            <h2 className={`text-lg font-semibold ${ButtonsClass[type].title}`}>{type === "warning" ? "Advertencia" : "Información"} </h2>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {placeholder && (
          <p className="text-gray-600 mb-6 text-sm sm:text-base text-center">
            {placeholder}
          </p>
        )}

        <div className="flex gap-3 mt-4">
          {buttonClose && (
             <button
            onClick={handleClose}
            className={`flex-1 px-4 py-2 ${ButtonsClass[type].close}`}
          >
            {closeText || "Cerrar"}
          </button>
          )}

          {buttonApply && (
          <button
            onClick={handleApply}
            className={`flex-1 px-4 py-2 ${ButtonsClass[type].apply}`}
          >
            {applyText || "Continuar"}
          </button>
          )}
        </div>
      </div>
    </div>,
    document.body
  );
}
