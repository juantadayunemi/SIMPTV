import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { FCMInitializer } from '../notifications/FCMInitializer';

export const Layout: React.FC = () => {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Initialize FCM when user is logged in */}
      <FCMInitializer />

      {/* Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header />

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;