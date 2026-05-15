import React from 'react'
import { motion } from 'framer-motion'
import { LogOut, Users, AlertCircle, CheckCircle } from 'lucide-react'

const ExitManagement: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Exit Management</h1>
        <p className="text-gray-600 mt-2">Manage employee offboarding and exit processes</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Resignations</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">5</p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <LogOut className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">In Progress</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">3</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Completed</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">12</p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Pending Tasks</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">8</p>
            </div>
            <div className="p-3 rounded-lg bg-red-100">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Exit Process Pipeline</h3>
        <p className="text-gray-600">Employee exit management workflow will be implemented here.</p>
      </motion.div>
    </div>
  );
}

export default ExitManagement
