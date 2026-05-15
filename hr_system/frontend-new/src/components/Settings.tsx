import React from 'react'
import { motion } from 'framer-motion'
import { Settings as SettingsIcon, Shield, Bell, Database, Users } from 'lucide-react'

const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage system settings and configurations</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">General Settings</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">System Config</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <SettingsIcon className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Users</p>
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
              <p className="text-sm text-gray-600">Storage Used</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">2.4GB</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-100">
              <Database className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Alerts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">3</p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <Bell className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Configuration</h3>
        <p className="text-gray-600">System settings and configuration management will be implemented here.</p>
      </motion.div>
    </div>
  );
}

export default Settings
