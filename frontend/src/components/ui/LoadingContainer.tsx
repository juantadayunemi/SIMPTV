import React from "react";
import { LoadingSpinner } from "../ui/LoadingSpinner";
import { create } from "domain";
import { createPortal } from "react-dom";

interface LoadingContainerProps {
  loading: boolean;
  message?: string;
  type?: "global" | "section" | "button";
  children?: React.ReactNode;
}

export const LoadingContainer: React.FC<LoadingContainerProps> = ({
  loading,
  message = "Cargando...",
  type = "section",
  children,
}) => {
  if (!loading) return <>{children}</>;

  switch (type) {
    case "global":
      return createPortal(
        <div className="fixed inset-0 flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm z-[9999]">
          <LoadingSpinner size="df" />
          <p className="mt-4 text-gray-600 text-lg">{message}</p>
        </div>,
        document.body
      );

    case "button":
      return (
        <div className="flex items-center justify-center">
          <LoadingSpinner size="sm" color="white" />
        </div>
      );

    case "section":
    default:
      return (
        <div className="flex flex-col items-center justify-center h-64 space-y-3">
          <LoadingSpinner size="df" />
          <p className="text-gray-400">{message}</p>
        </div>
      );
  }
};
