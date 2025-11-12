import React from "react";

export const NotificationsBottleneck = ({ handleToggleNotification, isNotificationActive }: { handleToggleNotification: () => void; isNotificationActive: boolean }) => {
  return (
    <button
      onClick={handleToggleNotification}
      title={isNotificationActive ? "Desactivar notificaciones" : "Recibir notificación de esta ubicación y cámara"}
      className={`
        p-2 rounded-full transition-all duration-300 shadow-sm
        flex items-center justify-center
        ${isNotificationActive
          ? 'bg-blue-500 text-white animate-ring shadow-md'
          : 'bg-white text-blue-500 border border-blue-200 hover:bg-blue-50'}
      `}
    >
      {/* Ícono campana */}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className={`h-5 w-5 transition-transform ${isNotificationActive ? 'scale-110' : 'scale-100'}`}
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3c0 .528-.214 1.04-.595 1.405L4 17h5m6 0a3 3 0 11-6 0h6z"
        />
      </svg>
    </button>
  );
};
