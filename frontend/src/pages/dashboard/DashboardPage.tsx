import React from 'react';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of traffic analysis system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total Analyses */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Analyses
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    142
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Plates Detected */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">🔍</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Plates Detected
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    1,247
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Active Users */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">👥</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Active Users
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    12
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">✅</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    System Status
                  </dt>
                  <dd className="text-lg font-medium text-green-600">
                    Healthy
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Recent Activity
          </h3>
          <div className="space-y-3">
            {[
              { action: 'New traffic analysis completed', location: 'Main Street', time: '2 minutes ago' },
              { action: 'Plate detection alert', location: 'Highway 101', time: '15 minutes ago' },
              { action: 'User login', location: 'System', time: '32 minutes ago' },
              { action: 'Analysis started', location: 'Downtown Ave', time: '1 hour ago' },
            ].map((activity, index) => (
              <div key={index} className="flex items-center space-x-3 text-sm">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <div className="flex-1">
                  <span className="text-gray-900">{activity.action}</span>
                  <span className="text-gray-500"> at {activity.location}</span>
                </div>
                <span className="text-gray-400">{activity.time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <button className="bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg p-4 text-center transition-colors">
              <span className="text-2xl mb-2 block">🚗</span>
              <span className="text-sm font-medium text-blue-900">New Analysis</span>
            </button>
            <button className="bg-green-50 hover:bg-green-100 border border-green-200 rounded-lg p-4 text-center transition-colors">
              <span className="text-2xl mb-2 block">📊</span>
              <span className="text-sm font-medium text-green-900">View Reports</span>
            </button>
            <Link 
              to="/settings"
              className="bg-purple-50 hover:bg-purple-100 border border-purple-200 rounded-lg p-4 text-center transition-colors block"
            >
              <span className="text-2xl mb-2 block">⚙️</span>
              <span className="text-sm font-medium text-purple-900">Settings</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;