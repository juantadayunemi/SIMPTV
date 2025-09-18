import React from 'react';

export const ProfilePage: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile Settings</h1>
        <p className="text-gray-600">Manage your account settings and preferences</p>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-gray-500">Profile management features coming soon...</p>
      </div>
    </div>
  );
};

export default ProfilePage;