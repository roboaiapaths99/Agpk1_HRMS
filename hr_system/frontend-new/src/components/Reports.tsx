import React from 'react'
import { motion } from 'framer-motion'
import { FileText, Download, Filter, Calendar } from 'lucide-react'

const Reports: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
        <p className="text-gray-600 mt-2">Generate and manage HR reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Monthly Reports</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">12</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Generated Today</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">5</p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <Download className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Scheduled</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">8</p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <Calendar className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>

        <motion.div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Templates</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">15</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-100">
              <Filter className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </motion.div>
      </div>

      <motion.div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Report Library</h3>
        <p className="text-gray-600">HR reports generation and management will be implemented here.</p>
      </motion.div>
    </div>
  );
}

export default Reports
