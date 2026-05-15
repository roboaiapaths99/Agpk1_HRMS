import React from 'react';
import { Users, UserPlus, Shield, Settings } from 'lucide-react';

const UserManagement: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">User Management</h1>
        <p className="text-gray-600 mt-2">Manage system users and permissions</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Users</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">24</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Users</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">18</p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <Shield className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Admin Users</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">5</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-100">
              <Settings className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">New This Month</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">3</p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <UserPlus className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">User Accounts</h3>
        <p className="text-gray-600">User management functionality will be implemented here.</p>
      </motion.div>
    </div>
  );
};

export default UserManagement;
