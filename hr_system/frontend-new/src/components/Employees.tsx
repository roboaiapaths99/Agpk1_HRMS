import React, { useState } from 'react';
import {
  Users,
  Plus,
  Search,
  Filter,
  Edit,
  Trash2,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Briefcase,
  Download,
  Upload
} from 'lucide-react';

interface Employee {
  id: string;
  name: string;
  email: string;
  phone: string;
  department: string;
  position: string;
  location: string;
  salary: number;
  joiningDate: string;
  status: string;
}

interface Department {
  value: string;
  label: string;
}

const Employees: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDepartment, setSelectedDepartment] = useState('all');

  // Mock employee data with Indian names
  const employees: Employee[] = [
    {
      id: 'EMP001',
      name: 'Rahul Sharma',
      email: 'rahul.sharma@logday.com',
      phone: '+91 98765 43210',
      department: 'Engineering',
      position: 'Senior Developer',
      location: 'Bangalore',
      salary: 850000,
      joiningDate: '2022-03-15',
      status: 'active'
    },
    {
      id: 'EMP002',
      name: 'Priya Verma',
      email: 'priya.verma@logday.com',
      phone: '+91 98765 43211',
      department: 'HR',
      position: 'HR Manager',
      location: 'Delhi',
      salary: 600000,
      joiningDate: '2021-07-20',
      status: 'active'
    },
    {
      id: 'EMP003',
      name: 'Amit Kumar',
      email: 'amit.kumar@logday.com',
      phone: '+91 98765 43212',
      department: 'Sales',
      position: 'Sales Executive',
      location: 'Mumbai',
      salary: 450000,
      joiningDate: '2023-01-10',
      status: 'active'
    },
    {
      id: 'EMP004',
      name: 'Sneha Patel',
      email: 'sneha.patel@logday.com',
      phone: '+91 98765 43213',
      department: 'Marketing',
      position: 'Marketing Manager',
      location: 'Pune',
      salary: 720000,
      joiningDate: '2021-11-05',
      status: 'active'
    },
    {
      id: 'EMP005',
      name: 'Vikram Singh',
      email: 'vikram.singh@logday.com',
      phone: '+91 98765 43214',
      department: 'Engineering',
      position: 'DevOps Engineer',
      location: 'Bangalore',
      salary: 780000,
      joiningDate: '2022-08-22',
      status: 'active'
    },
    {
      id: 'EMP006',
      name: 'Anjali Nair',
      email: 'anjali.nair@logday.com',
      phone: '+91 98765 43215',
      department: 'Finance',
      position: 'Finance Analyst',
      location: 'Chennai',
      salary: 550000,
      joiningDate: '2023-02-14',
      status: 'active'
    }
  ];

  const departments = [
    { value: 'all', label: 'All Departments' },
    { value: 'Engineering', label: 'Engineering' },
    { value: 'HR', label: 'HR' },
    { value: 'Sales', label: 'Sales' },
    { value: 'Marketing', label: 'Marketing' },
    { value: 'Finance', label: 'Finance' },
    { value: 'Operations', label: 'Operations' }
  ];

  const filteredEmployees = employees.filter(employee => {
    const matchesSearch = employee.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         employee.id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDepartment = selectedDepartment === 'all' || employee.department === selectedDepartment;
    return matchesSearch && matchesDepartment;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'inactive':
        return 'bg-red-100 text-red-800';
      case 'on-leave':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Employees</h1>
          <p className="text-gray-600 mt-2">Manage your workforce and employee information</p>
        </div>
        <div className="flex gap-3">
          <button className="btn-secondary flex items-center gap-2">
            <Upload className="w-4 h-4" />
            Import
          </button>
          <button className="btn-secondary flex items-center gap-2">
            <Download className="w-4 h-4" />
            Export
          </button>
          <button className="btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add Employee
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Employees</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{employees.length}</p>
            </div>
            <div className="p-3 rounded-lg bg-blue-100">
              <Users className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Now</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{employees.filter(e => e.status === 'active').length}</p>
            </div>
            <div className="p-3 rounded-lg bg-green-100">
              <Users className="w-6 h-6 text-green-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Departments</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{departments.length - 1}</p>
            </div>
            <div className="p-3 rounded-lg bg-purple-100">
              <Briefcase className="w-6 h-6 text-purple-600" />
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">New This Month</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">12</p>
            </div>
            <div className="p-3 rounded-lg bg-orange-100">
              <Calendar className="w-6 h-6 text-orange-600" />
            </div>
          </div>
        </motion.div>
      </div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.5 }}
        className="card"
      >
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search employees by name, email, or ID..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              {departments.map(dept => (
                <option key={dept.value} value={dept.value}>{dept.label}</option>
              ))}
            </select>
            <button className="btn-secondary flex items-center gap-2">
              <Filter className="w-4 h-4" />
              More Filters
            </button>
          </div>
        </div>
      </motion.div>

      {/* Employee Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.6 }}
        className="card"
      >
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Employee</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Contact</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Department</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Position</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Location</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Salary</th>
                <th className="text-left py-3 px-4 text-sm font-medium text-gray-700">Status</th>
                <th className="text-center py-3 px-4 text-sm font-medium text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredEmployees.map((employee, index) => (
                <motion.tr
                  key={employee.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.7 + index * 0.05 }}
                  className="border-b border-gray-100 hover:bg-gray-50"
                >
                  <td className="py-3 px-4">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{employee.name}</p>
                      <p className="text-xs text-gray-500">{employee.id}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-1">
                        <Mail className="w-3 h-3 text-gray-400" />
                        <p className="text-sm text-gray-600">{employee.email}</p>
                      </div>
                      <div className="flex items-center gap-1">
                        <Phone className="w-3 h-3 text-gray-400" />
                        <p className="text-sm text-gray-600">{employee.phone}</p>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900">{employee.department}</td>
                  <td className="py-3 px-4 text-sm text-gray-900">{employee.position}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-gray-400" />
                      <p className="text-sm text-gray-900">{employee.location}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-900">₹{employee.salary.toLocaleString()}</td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(employee.status)}`}>
                      {employee.status.charAt(0).toUpperCase() + employee.status.slice(1)}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-center gap-2">
                      <button className="p-1 hover:bg-gray-100 rounded">
                        <Edit className="w-4 h-4 text-gray-600" />
                      </button>
                      <button className="p-1 hover:bg-gray-100 rounded">
                        <Trash2 className="w-4 h-4 text-gray-600" />
                      </button>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Table Footer */}
        <div className="mt-4 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Showing {filteredEmployees.length} of {employees.length} employees
          </div>
          <div className="flex gap-2">
            <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">Previous</button>
            <button className="px-3 py-1 bg-primary-600 text-white rounded-lg text-sm">1</button>
            <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">2</button>
            <button className="px-3 py-1 border border-gray-300 rounded-lg text-sm hover:bg-gray-50">Next</button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Employees
