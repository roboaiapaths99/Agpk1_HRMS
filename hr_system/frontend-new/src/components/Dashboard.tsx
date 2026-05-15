import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Users, TrendingUp, Calendar, DollarSign, UserPlus, UserMinus, Clock, AlertCircle, Building2, BarChart3 } from 'lucide-react'

const Dashboard: React.FC = () => {
  const navigate = useNavigate()

  const stats = [
    {
      title: 'Total Employees',
      value: '1,234',
      change: '+12%',
      icon: Users,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      title: 'Present Today',
      value: '1,156',
      change: '+5%',
      icon: Calendar,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      title: 'Monthly Payroll',
      value: '₹2.4M',
      change: '+8%',
      icon: DollarSign,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      title: 'Open Positions',
      value: '23',
      change: '-3%',
      icon: UserPlus,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ]

  const recentActivities = [
    { id: 1, type: 'hire', name: 'Arjun Mehta', position: 'Senior Developer', time: '2 hours ago', icon: '👨‍💻' },
    { id: 2, type: 'leave', name: 'Priya Patel', position: 'UI Designer', time: '3 hours ago', icon: '🏖️' },
    { id: 3, type: 'payroll', name: 'Monthly Payroll', position: 'All Employees', time: '1 day ago', icon: '💰' },
    { id: 4, type: 'exit', name: 'Rohit Verma', position: 'Sales Executive', time: '2 days ago', icon: '👋' }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome to your HR management dashboard</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <div key={index} className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                <p className="text-sm text-green-600 mt-2">{stat.change}</p>
              </div>
              <div className={`w-12 h-12 ${stat.bgColor} rounded-lg flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => navigate('/employees')}
            className="flex items-center space-x-3 p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
          >
            <UserPlus className="w-5 h-5 text-blue-600" />
            <span className="text-blue-900 font-medium">Add New Employee</span>
          </button>
          <button
            onClick={() => navigate('/reports')}
            className="flex items-center space-x-3 p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors"
          >
            <BarChart3 className="w-5 h-5 text-green-600" />
            <span className="text-green-900 font-medium">Generate Report</span>
          </button>
          <button
            onClick={() => navigate('/payroll')}
            className="flex items-center space-x-3 p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors"
          >
            <DollarSign className="w-5 h-5 text-purple-600" />
            <span className="text-purple-900 font-medium">Process Payroll</span>
          </button>
        </div>
      </div>

      {/* Recent Activities */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activities</h2>
        <div className="space-y-4">
          {recentActivities.map((activity) => (
            <div key={activity.id} className="flex items-center space-x-4 p-4 hover:bg-gray-50 rounded-lg">
              <div className="text-2xl">{activity.icon}</div>
              <div className="flex-1">
                <p className="font-medium text-gray-900">{activity.name}</p>
                <p className="text-sm text-gray-600">{activity.position}</p>
              </div>
              <p className="text-sm text-gray-500">{activity.time}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Dashboard
