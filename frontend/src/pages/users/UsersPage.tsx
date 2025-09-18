import React from 'react';

export const UsersPage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Users Management</h1>
        <p className="text-gray-600">Manage system users and permissions</p>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">User management features coming soon...</p>
      </div>
    </div>
  );
};

export default UsersPage;