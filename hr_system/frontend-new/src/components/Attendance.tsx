import React from 'react'
import { motion } from 'framer-motion'
import { Calendar, Users, Clock, CheckCircle } from 'lucide-react'

const Attendance: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Attendance Management</h1>
        <p className="text-gray-600 mt-2">Track and manage employee attendance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Present Today</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">1,189</p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Absent Today</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">23</p>
            </div>
            <div className="p-3 rounded-lg bg-red-100">
              <Users className="w-6 h-6 text-red-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Late Arrivals</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">15</p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <Clock className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">This Month</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">94.2%</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Attendance Records</h3>
        <p className="text-gray-600">Attendance tracking functionality will be implemented here.</p>
      </motion.div>
    </div>
  );
}

export default Attendance
