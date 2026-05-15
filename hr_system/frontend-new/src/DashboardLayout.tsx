import React, { useState } from 'react'
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, Calendar, Wallet, Building2, BarChart3, UserPlus, LogOut, FileText, Settings, TrendingUp, Briefcase, FolderOpen } from 'lucide-react'
import LeaveManagement from './components/LeaveManagement'
import PerformanceManagement from './components/PerformanceManagement'
import Recruitment from './components/Recruitment'
import DocumentManagement from './components/DocumentManagement'
import Payroll from './components/Payroll'

function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()
  const navigate = useNavigate()

  const menuItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/employees', label: 'Employees', icon: Users },
    { path: '/attendance', label: 'Attendance', icon: Calendar },
    { path: '/payroll', label: 'Payroll', icon: Wallet },
    { path: '/leave-management', label: 'Leave Management', icon: BarChart3 },
    { path: '/performance-management', label: 'Performance', icon: TrendingUp },
    { path: '/recruitment', label: 'Recruitment', icon: Briefcase },
    { path: '/document-management', label: 'Documents', icon: FolderOpen },
    { path: '/onboarding', label: 'Onboarding', icon: UserPlus },
    { path: '/exit-management', label: 'Exit Management', icon: LogOut },
    { path: '/reports', label: 'Reports', icon: FileText },
    { path: '/settings', label: 'Settings', icon: Settings },
  ]

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#f9fafb' }}>
      {/* Sidebar */}
      <div style={{ 
        width: sidebarOpen ? '256px' : '80px', 
        backgroundColor: 'white', 
        borderRight: '1px solid #e5e7eb',
        transition: 'width 0.3s ease',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Logo */}
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ 
              width: '40px', 
              height: '40px', 
              backgroundColor: '#3b82f6', 
              borderRadius: '8px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center' 
            }}>
              <Building2 style={{ width: '24px', height: '24px', color: 'white' }} />
            </div>
            {sidebarOpen && (
              <div>
                <div style={{ fontWeight: 'bold', fontSize: '20px', color: '#111827' }}>LOGDAY</div>
                <div style={{ fontSize: '12px', color: '#6b7280' }}>Smart Workforce</div>
              </div>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ padding: '16px', flex: 1 }}>
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                borderRadius: '8px',
                textDecoration: 'none',
                color: location.pathname === item.path ? '#3b82f6' : '#6b7280',
                backgroundColor: location.pathname === item.path ? '#eff6ff' : 'transparent',
                transition: 'all 0.2s ease',
                marginBottom: '4px'
              }}
            >
              <item.icon style={{ width: '20px', height: '20px' }} />
              {sidebarOpen && <span style={{ fontSize: '14px', fontWeight: '500' }}>{item.label}</span>}
            </Link>
          ))}
        </nav>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <header style={{ 
          backgroundColor: 'white', 
          borderBottom: '1px solid #e5e7eb', 
          padding: '16px 24px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              style={{ 
                padding: '8px', 
                borderRadius: '8px', 
                border: '1px solid #e5e7eb',
                backgroundColor: 'white',
                cursor: 'pointer'
              }}
            >
              {sidebarOpen ? '←' : '→'}
            </button>
            <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
              HR Management System
            </h1>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={() => navigate('/login')}
              style={{ 
                padding: '8px 16px', 
                borderRadius: '8px', 
                border: '1px solid #e5e7eb',
                backgroundColor: 'white',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <LogOut style={{ width: '16px', height: '16px' }} />
              Logout
            </button>
          </div>
        </header>

        {/* Page Content */}
        <main style={{ flex: 1, padding: '24px', overflow: 'auto' }}>
          <Routes>
            <Route path="/" element={<DashboardContent />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/attendance" element={<AttendancePage />} />
            <Route path="/payroll" element={<Payroll />} />
            <Route path="/leave-management" element={<LeaveManagement />} />
            <Route path="/performance-management" element={<PerformanceManagement />} />
            <Route path="/recruitment" element={<Recruitment />} />
            <Route path="/document-management" element={<DocumentManagement />} />
            <Route path="/onboarding" element={<OnboardingPage />} />
            <Route path="/exit-management" element={<ExitManagementPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

// Dashboard Content Component
function DashboardContent() {
  const navigate = useNavigate()
  
  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Dashboard</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Welcome to your HR management dashboard</p>

      {/* Quick Actions */}
      <div style={{ 
        backgroundColor: 'white', 
        padding: '24px', 
        borderRadius: '12px', 
        border: '1px solid #e5e7eb',
        marginBottom: '24px' 
      }}>
        <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#111827', marginBottom: '16px' }}>Quick Actions</h3>
        <div style={{ display: 'grid', gap: '8px' }}>
          <button onClick={() => navigate('/employees')} style={{ 
            padding: '10px 16px', 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            width: '100%',
            textAlign: 'left'
          }}>
            + Add New Employee
          </button>
          <button onClick={() => navigate('/reports')} style={{ 
            padding: '10px 16px', 
            backgroundColor: '#10b981', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            width: '100%',
            textAlign: 'left'
          }}>
            📊 Generate Report
          </button>
          <button onClick={() => navigate('/payroll')} style={{ 
            padding: '10px 16px', 
            backgroundColor: '#f59e0b', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            width: '100%',
            textAlign: 'left'
          }}>
            💰 Process Payroll
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Employees</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>1,234</p>
          <p style={{ fontSize: '14px', color: '#10b981', margin: '8px 0 0 0' }}>+12% from last month</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Present Today</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>1,156</p>
          <p style={{ fontSize: '14px', color: '#10b981', margin: '8px 0 0 0' }}>+5% from yesterday</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Monthly Payroll</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>₹2.4M</p>
          <p style={{ fontSize: '14px', color: '#10b981', margin: '8px 0 0 0' }}>+8% from last month</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Open Positions</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>23</p>
          <p style={{ fontSize: '14px', color: '#ef4444', margin: '8px 0 0 0' }}>-3% from last week</p>
        </div>
      </div>
    </div>
  )
}

// Placeholder page components
function EmployeesPage() {
  const [employees, setEmployees] = useState([
    { id: 1, name: 'Rahul Sharma', email: 'rahul.s@logday.com', phone: '+91 98765 43210', department: 'Engineering', position: 'Senior Developer', location: 'Mumbai', salary: '12,00,000', status: 'Active' },
    { id: 2, name: 'Priya Verma', email: 'priya.v@logday.com', phone: '+91 98765 43211', department: 'HR', position: 'HR Manager', location: 'Delhi', salary: '8,50,000', status: 'Active' },
    { id: 3, name: 'Amit Kumar', email: 'amit.k@logday.com', phone: '+91 98765 43212', department: 'Sales', position: 'Sales Executive', location: 'Bangalore', salary: '6,00,000', status: 'Active' },
    { id: 4, name: 'Sneha Patel', email: 'sneha.p@logday.com', phone: '+91 98765 43213', department: 'Marketing', position: 'Marketing Manager', location: 'Pune', salary: '9,00,000', status: 'On Leave' },
    { id: 5, name: 'Vikram Singh', email: 'vikram.s@logday.com', phone: '+91 98765 43214', department: 'Engineering', position: 'DevOps Engineer', location: 'Hyderabad', salary: '10,00,000', status: 'Active' }
  ])
  const [searchTerm, setSearchTerm] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    department: '',
    position: '',
    location: '',
    salary: ''
  })

  const filteredEmployees = employees.filter(emp => 
    emp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    emp.department.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddEmployee = () => {
    console.log('handleAddEmployee called with formData:', formData)
    
    // Validate form
    if (!formData.name || !formData.email || !formData.department || !formData.position) {
      alert('Please fill in all required fields')
      return
    }

    // Create new employee
    const newEmployee = {
      id: employees.length + 1,
      ...formData,
      status: 'Active'
    }

    console.log('Adding new employee:', newEmployee)

    // Add to employees list
    setEmployees(prev => [...prev, newEmployee])
    
    // Reset form
    setFormData({
      name: '',
      email: '',
      phone: '',
      department: '',
      position: '',
      location: '',
      salary: ''
    })
    
    // Hide form
    setShowAddForm(false)
    
    alert('Employee added successfully!')
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Employees</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Manage your employee database</p>
      
      {/* Search and Add */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <input
          type="text"
          placeholder="Search employees..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ 
            flex: 1, 
            padding: '12px 16px', 
            border: '1px solid #e5e7eb', 
            borderRadius: '8px',
            fontSize: '14px'
          }}
        />
        <button
          onClick={() => {
            console.log('Add Employee button clicked, current showAddForm:', showAddForm)
            setShowAddForm(!showAddForm)
          }}
          style={{ 
            padding: '12px 24px', 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => e.target.style.backgroundColor = '#2563eb'}
          onMouseOut={(e) => e.target.style.backgroundColor = '#3b82f6'}
        >
          + Add Employee
        </button>
      </div>

      {/* Add Employee Form */}
      {showAddForm && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px', 
          border: '2px solid #3b82f6',
          marginBottom: '24px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Add New Employee</h3>
            <button
              onClick={() => {
                console.log('Closing form')
                setShowAddForm(false)
                setFormData({
                  name: '',
                  email: '',
                  phone: '',
                  department: '',
                  position: '',
                  location: '',
                  salary: ''
                })
              }}
              style={{ 
                padding: '4px 8px', 
                backgroundColor: '#ef4444', 
                color: 'white', 
                border: 'none', 
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px'
              }}
            >
              ✕ Close
            </button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}>
            <input 
              type="text" 
              name="name"
              placeholder="Full Name *" 
              value={formData.name}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <input 
              type="email" 
              name="email"
              placeholder="Email *" 
              value={formData.email}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <input 
              type="tel" 
              name="phone"
              placeholder="Phone" 
              value={formData.phone}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <input 
              type="text" 
              name="department"
              placeholder="Department *" 
              value={formData.department}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <input 
              type="text" 
              name="position"
              placeholder="Position *" 
              value={formData.position}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <input 
              type="text" 
              name="location"
              placeholder="Location" 
              value={formData.location}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <input 
              type="text" 
              name="salary"
              placeholder="Salary (e.g., 8,00,000)" 
              value={formData.salary}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <button
              onClick={handleAddEmployee}
              style={{ 
                padding: '8px 16px', 
                backgroundColor: '#10b981', 
                color: 'white', 
                border: 'none', 
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Save Employee
            </button>
            <button
              onClick={() => {
                setShowAddForm(false)
                setFormData({
                  name: '',
                  email: '',
                  phone: '',
                  department: '',
                  position: '',
                  location: '',
                  salary: ''
                })
              }}
              style={{ 
                padding: '8px 16px', 
                backgroundColor: '#6b7280', 
                color: 'white', 
                border: 'none', 
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Employees Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead style={{ backgroundColor: '#f9fafb' }}>
            <tr>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280', borderBottom: '1px solid #e5e7eb' }}>Name</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280', borderBottom: '1px solid #e5e7eb' }}>Email</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280', borderBottom: '1px solid #e5e7eb' }}>Department</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280', borderBottom: '1px solid #e5e7eb' }}>Position</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280', borderBottom: '1px solid #e5e7eb' }}>Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280', borderBottom: '1px solid #e5e7eb' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredEmployees.map((employee) => (
              <tr key={employee.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  <div>
                    <div style={{ fontWeight: '500' }}>{employee.name}</div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>{employee.phone}</div>
                  </div>
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>{employee.email}</td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>{employee.department}</td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>{employee.position}</td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: employee.status === 'Active' ? '#d1fae5' : '#fef3c7',
                    color: employee.status === 'Active' ? '#065f46' : '#92400e'
                  }}>
                    {employee.status}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#3b82f6', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      Edit
                    </button>
                    <button
                      style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#ef4444', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function AttendancePage() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [attendanceRecords, setAttendanceRecords] = useState([
    { id: 1, name: 'Rahul Sharma', checkIn: '09:15 AM', checkOut: '06:30 PM', status: 'Present', department: 'Engineering' },
    { id: 2, name: 'Priya Verma', checkIn: '09:00 AM', checkOut: '06:00 PM', status: 'Present', department: 'HR' },
    { id: 3, name: 'Amit Kumar', checkIn: '09:45 AM', checkOut: '06:15 PM', status: 'Late', department: 'Sales' },
    { id: 4, name: 'Sneha Patel', checkIn: '-', checkOut: '-', status: 'Absent', department: 'Marketing' },
    { id: 5, name: 'Vikram Singh', checkIn: '08:45 AM', checkOut: '07:00 PM', status: 'Present', department: 'Engineering' }
  ])

  const stats = {
    present: attendanceRecords.filter(r => r.status === 'Present').length,
    absent: attendanceRecords.filter(r => r.status === 'Absent').length,
    late: attendanceRecords.filter(r => r.status === 'Late').length,
    total: attendanceRecords.length
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Attendance</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Track employee attendance</p>
      
      {/* Date Selection and Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '24px', marginBottom: '24px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Select Date</label>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            style={{ 
              padding: '8px 12px', 
              border: '1px solid #e5e7eb', 
              borderRadius: '6px',
              fontSize: '14px'
            }}
          />
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10b981' }}>{stats.present}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Present</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444' }}>{stats.absent}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Absent</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#f59e0b' }}>{stats.late}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Late</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#6b7280' }}>{stats.total}</div>
            <div style={{ fontSize: '12px', color: '#6b7280' }}>Total</div>
          </div>
        </div>
      </div>

      {/* Attendance Records */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Attendance Records for {selectedDate}</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Employee</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Department</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Check In</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Check Out</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {attendanceRecords.map((record) => (
              <tr key={record.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                  {record.name}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {record.department}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {record.checkIn}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {record.checkOut}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: 
                      record.status === 'Present' ? '#d1fae5' : 
                      record.status === 'Absent' ? '#fee2e2' : '#fef3c7',
                    color: 
                      record.status === 'Present' ? '#065f46' : 
                      record.status === 'Absent' ? '#991b1b' : '#92400e'
                  }}>
                    {record.status}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#3b82f6', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      Edit
                    </button>
                    <button
                      style={{ 
                        padding: '4px 8px', 
                        backgroundColor: record.checkIn === '-' ? '#10b981' : '#ef4444', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      {record.checkIn === '-' ? 'Check In' : 'Check Out'}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function PayrollPage() {
  const [selectedMonth, setSelectedMonth] = useState('April 2026')
  const [payrollRecords, setPayrollRecords] = useState([
    { id: 1, employee: 'Rahul Sharma', basic: '80,000', hra: '20,000', da: '8,000', other: '5,000', gross: '1,13,000', deductions: '15,000', net: '98,000', status: 'Processed' },
    { id: 2, employee: 'Priya Verma', basic: '60,000', hra: '15,000', da: '6,000', other: '3,000', gross: '84,000', deductions: '12,000', net: '72,000', status: 'Processed' },
    { id: 3, employee: 'Amit Kumar', basic: '45,000', hra: '11,250', da: '4,500', other: '2,250', gross: '63,000', deductions: '9,000', net: '54,000', status: 'Pending' },
    { id: 4, employee: 'Sneha Patel', basic: '55,000', hra: '13,750', da: '5,500', other: '2,750', gross: '76,500', deductions: '11,000', net: '65,500', status: 'Processed' },
    { id: 5, employee: 'Vikram Singh', basic: '70,000', hra: '17,500', da: '7,000', other: '3,500', gross: '97,500', deductions: '14,000', net: '83,500', status: 'Pending' }
  ])

  const totalStats = payrollRecords.reduce((acc, record) => ({
    gross: acc.gross + parseInt(record.gross.replace(/,/g, '')),
    net: acc.net + parseInt(record.net.replace(/,/g, '')),
    deductions: acc.deductions + parseInt(record.deductions.replace(/,/g, ''))
  }), { gross: 0, net: 0, deductions: 0 })

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Payroll</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Manage payroll processing</p>
      
      {/* Month Selection and Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Select Month</label>
          <select
            value={selectedMonth}
            onChange={(e) => setSelectedMonth(e.target.value)}
            style={{ 
              padding: '8px 12px', 
              border: '1px solid #e5e7eb', 
              borderRadius: '6px',
              fontSize: '14px',
              minWidth: '150px'
            }}
          >
            <option>April 2026</option>
            <option>May 2026</option>
            <option>June 2026</option>
          </select>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#10b981', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            Process Payroll
          </button>
          <button
            style={{ 
              padding: '10px 20px', 
              backgroundColor: '#3b82f6', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            Export Payslips
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Gross Salary</h4>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827', margin: '0' }}>₹{totalStats.gross.toLocaleString('en-IN')}</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Net Salary</h4>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827', margin: '0' }}>₹{totalStats.net.toLocaleString('en-IN')}</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Deductions</h4>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444', margin: '0' }}>₹{totalStats.deductions.toLocaleString('en-IN')}</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Employees</h4>
          <p style={{ fontSize: '24px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{payrollRecords.length}</p>
        </div>
      </div>

      {/* Payroll Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Payroll Details for {selectedMonth}</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Employee</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Basic</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>HRA</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>DA</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Other</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Gross</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Deductions</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Net</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {payrollRecords.map((record) => (
              <tr key={record.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                  {record.employee}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right' }}>
                  ₹{record.basic}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right' }}>
                  ₹{record.hra}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right' }}>
                  ₹{record.da}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right' }}>
                  ₹{record.other}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right', fontWeight: '600' }}>
                  ₹{record.gross}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#ef4444', textAlign: 'right' }}>
                  ₹{record.deductions}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#10b981', textAlign: 'right', fontWeight: '600' }}>
                  ₹{record.net}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: record.status === 'Processed' ? '#d1fae5' : '#fef3c7',
                    color: record.status === 'Processed' ? '#065f46' : '#92400e'
                  }}>
                    {record.status}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#3b82f6', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      View
                    </button>
                    <button
                      style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#10b981', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}
                    >
                      Payslip
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('6months')
  
  const analyticsData = {
    employeeGrowth: [
      { month: 'Nov', employees: 1180 },
      { month: 'Dec', employees: 1200 },
      { month: 'Jan', employees: 1215 },
      { month: 'Feb', employees: 1230 },
      { month: 'Mar', employees: 1245 },
      { month: 'Apr', employees: 1234 }
    ],
    attendanceTrends: [
      { month: 'Nov', rate: 94.5 },
      { month: 'Dec', rate: 93.2 },
      { month: 'Jan', rate: 95.8 },
      { month: 'Feb', rate: 94.1 },
      { month: 'Mar', rate: 96.2 },
      { month: 'Apr', rate: 93.7 }
    ],
    departmentDistribution: [
      { dept: 'Engineering', count: 450, percentage: 36.5 },
      { dept: 'Sales', count: 280, percentage: 22.7 },
      { dept: 'HR', count: 120, percentage: 9.7 },
      { dept: 'Marketing', count: 180, percentage: 14.6 },
      { dept: 'Operations', count: 150, percentage: 12.2 },
      { dept: 'Finance', count: 54, percentage: 4.3 }
    ]
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Analytics</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>View HR analytics and reports</p>
      
      {/* Time Range Selector */}
      <div style={{ marginBottom: '24px' }}>
        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          style={{ 
            padding: '8px 12px', 
            border: '1px solid #e5e7eb', 
            borderRadius: '6px',
            fontSize: '14px'
          }}
        >
          <option value="1month">Last Month</option>
          <option value="3months">Last 3 Months</option>
          <option value="6months">Last 6 Months</option>
          <option value="1year">Last Year</option>
        </select>
      </div>

      {/* Key Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '32px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Employees</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>1,234</p>
          <p style={{ fontSize: '12px', color: '#10b981', margin: '8px 0 0 0' }}>+2.8% from last month</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Avg Attendance Rate</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>94.7%</p>
          <p style={{ fontSize: '12px', color: '#ef4444', margin: '8px 0 0 0' }}>-1.5% from last month</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Monthly Turnover</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>3.2%</p>
          <p style={{ fontSize: '12px', color: '#10b981', margin: '8px 0 0 0' }}>-0.8% from last month</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h4 style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Open Positions</h4>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>23</p>
          <p style={{ fontSize: '12px', color: '#f59e0b', margin: '8px 0 0 0' }}>5 critical roles</p>
        </div>
      </div>

      {/* Charts Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px', marginBottom: '32px' }}>
        {/* Employee Growth Chart */}
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Employee Growth</h3>
          <div style={{ height: '200px', display: 'flex', alignItems: 'flex-end', gap: '8px' }}>
            {analyticsData.employeeGrowth.map((data, index) => (
              <div key={data.month} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <div style={{ 
                  width: '100%', 
                  backgroundColor: '#3b82f6', 
                  borderRadius: '4px 4px 0 0',
                  height: `${(data.employees - 1170) * 4}px`
                }}></div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>{data.month}</div>
                <div style={{ fontSize: '10px', color: '#111827', fontWeight: '500' }}>{data.employees}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Department Distribution */}
        <div style={{ backgroundColor: 'white', padding: '24px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Department Distribution</h3>
          {analyticsData.departmentDistribution.map((dept) => (
            <div key={dept.dept} style={{ marginBottom: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '14px', color: '#111827' }}>{dept.dept}</span>
                <span style={{ fontSize: '14px', color: '#6b7280' }}>{dept.count} ({dept.percentage}%)</span>
              </div>
              <div style={{ height: '8px', backgroundColor: '#f3f4f6', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ 
                  height: '100%', 
                  backgroundColor: '#3b82f6', 
                  borderRadius: '4px',
                  width: `${dept.percentage * 2}%`
                }}></div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed Analytics Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Department Performance Metrics</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Department</th>
              <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Headcount</th>
              <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Attendance %</th>
              <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Avg Salary</th>
              <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Satisfaction</th>
            </tr>
          </thead>
          <tbody>
            {analyticsData.departmentDistribution.map((dept) => (
              <tr key={dept.dept} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                  {dept.dept}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'center' }}>
                  {dept.count}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'center' }}>
                  {Math.floor(Math.random() * 5 + 93)}%
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'center' }}>
                  ₹{Math.floor(Math.random() * 5 + 8).toLocaleString('en-IN')}L
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'center' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: '#d1fae5',
                    color: '#065f46'
                  }}>
                    {Math.floor(Math.random() * 2 + 4)}/5
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function OnboardingPage() {
  const [candidates, setCandidates] = useState([
    { id: 1, name: 'Anjali Reddy', position: 'Senior Developer', department: 'Engineering', stage: 'Background Check', startDate: '2026-04-15', progress: 75 },
    { id: 2, name: 'Rohit Kumar', position: 'Marketing Manager', department: 'Marketing', stage: 'Document Collection', startDate: '2026-04-20', progress: 40 },
    { id: 3, name: 'Priya Sharma', position: 'HR Executive', department: 'HR', stage: 'Offer Accepted', startDate: '2026-04-25', progress: 25 },
    { id: 4, name: 'Amit Patel', position: 'Sales Executive', department: 'Sales', stage: 'Interview Round 2', startDate: '2026-05-01', progress: 60 }
  ])

  const stageColors = {
    'Offer Accepted': '#fef3c7',
    'Document Collection': '#dbeafe',
    'Background Check': '#e0e7ff',
    'Interview Round 2': '#fce7f3',
    'Ready to Join': '#d1fae5'
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Onboarding</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Manage new employee onboarding</p>
      
      {/* Onboarding Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{candidates.length}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Active Candidates</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: '0' }}>2</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Joining This Week</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: '0' }}>85%</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Avg Completion</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ef4444', margin: '0' }}>3</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Pending Documents</p>
        </div>
      </div>

      {/* Onboarding Pipeline */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Onboarding Pipeline</h3>
        </div>
        <div style={{ padding: '16px' }}>
          {candidates.map((candidate) => (
            <div key={candidate.id} style={{ display: 'flex', alignItems: 'center', padding: '16px 0', borderBottom: '1px solid #f3f4f6' }}>
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                  <div>
                    <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0 0 4px 0' }}>{candidate.name}</h4>
                    <p style={{ fontSize: '14px', color: '#6b7280', margin: '0' }}>{candidate.position} • {candidate.department}</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '0' }}>Start Date</p>
                    <p style={{ fontSize: '14px', fontWeight: '500', color: '#111827', margin: '0' }}>{candidate.startDate}</p>
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: stageColors[candidate.stage] || '#f3f4f6',
                        color: '#374151'
                      }}>
                        {candidate.stage}
                      </span>
                    </div>
                    <div style={{ height: '8px', backgroundColor: '#f3f4f6', borderRadius: '4px', overflow: 'hidden' }}>
                      <div style={{ 
                        height: '100%', 
                        backgroundColor: '#3b82f6', 
                        borderRadius: '4px',
                        width: `${candidate.progress}%`
                      }}></div>
                    </div>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '4px 0 0 0' }}>{candidate.progress}% Complete</p>
                  </div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px', marginLeft: '16px' }}>
                <button style={{ padding: '6px 12px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>View Details</button>
                <button style={{ padding: '6px 12px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>Send Reminder</button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ExitManagementPage() {
  const [exitRequests, setExitRequests] = useState([
    { id: 1, name: 'Sanjay Gupta', position: 'Senior Developer', department: 'Engineering', noticePeriod: '30 days', lastDay: '2026-05-15', reason: 'Better Opportunity', stage: 'Handover in Progress' },
    { id: 2, name: 'Neha Singh', position: 'Marketing Manager', department: 'Marketing', noticePeriod: '60 days', lastDay: '2026-06-10', reason: 'Relocation', stage: 'Document Collection' },
    { id: 3, name: 'Vikram Malhotra', position: 'Sales Executive', department: 'Sales', noticePeriod: '30 days', lastDay: '2026-04-30', reason: 'Career Change', stage: 'Exit Interview' },
    { id: 4, name: 'Anita Desai', position: 'HR Executive', department: 'HR', noticePeriod: '45 days', lastDay: '2026-05-20', reason: 'Further Studies', stage: 'Final Clearance' }
  ])

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Exit Management</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Handle employee exit processes</p>
      
      {/* Exit Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{exitRequests.length}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Active Exits</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: '0' }}>2</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>This Month</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ef4444', margin: '0' }}>3.2%</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Turnover Rate</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: '0' }}>41</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Avg Notice Days</p>
        </div>
      </div>

      {/* Exit Requests Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Exit Requests</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Employee</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Position</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Last Day</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Reason</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Stage</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {exitRequests.map((request) => (
              <tr key={request.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                  {request.name}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {request.position}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {request.lastDay}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {request.reason}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: '#fef3c7',
                    color: '#92400e'
                  }}>
                    {request.stage}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button style={{ padding: '4px 8px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>View</button>
                    <button style={{ padding: '4px 8px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Process</button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ReportsPage() {
  const [selectedReport, setSelectedReport] = useState('attendance')
  const [dateRange, setDateRange] = useState('monthly')

  const reports = [
    { id: 'attendance', name: 'Attendance Report', description: 'Monthly attendance summary', lastGenerated: '2026-04-08' },
    { id: 'payroll', name: 'Payroll Report', description: 'Payroll processing summary', lastGenerated: '2026-04-01' },
    { id: 'performance', name: 'Performance Report', description: 'Employee performance metrics', lastGenerated: '2026-03-31' },
    { id: 'turnover', name: 'Turnover Report', description: 'Employee turnover analysis', lastGenerated: '2026-04-05' },
    { id: 'headcount', name: 'Headcount Report', description: 'Department headcount summary', lastGenerated: '2026-04-08' },
    { id: 'compliance', name: 'Compliance Report', description: 'HR compliance status', lastGenerated: '2026-04-07' }
  ]

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Reports</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Generate and manage HR reports</p>
      
      {/* Report Generation Controls */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'flex-end' }}>
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Report Type</label>
          <select
            value={selectedReport}
            onChange={(e) => setSelectedReport(e.target.value)}
            style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }}
          >
            {reports.map(report => (
              <option key={report.id} value={report.id}>{report.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Date Range</label>
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
            <option value="quarterly">Quarterly</option>
            <option value="yearly">Yearly</option>
          </select>
        </div>
        <button
          style={{ 
            padding: '10px 20px', 
            backgroundColor: '#10b981', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Generate Report
        </button>
      </div>

      {/* Available Reports */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        {reports.map((report) => (
          <div key={report.id} style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: '0' }}>{report.name}</h3>
              <span style={{ 
                padding: '4px 8px', 
                borderRadius: '4px', 
                fontSize: '12px',
                fontWeight: '500',
                backgroundColor: '#dbeafe',
                color: '#1e40af'
              }}>
                {report.id.toUpperCase()}
              </span>
            </div>
            <p style={{ fontSize: '14px', color: '#6b7280', marginBottom: '12px' }}>{report.description}</p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <p style={{ fontSize: '12px', color: '#6b7280', margin: '0' }}>Last: {report.lastGenerated}</p>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button style={{ padding: '4px 8px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>View</button>
                <button style={{ padding: '4px 8px', backgroundColor: '#10b981', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', fontSize: '12px' }}>Download</button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Report Activity */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Recent Report Activity</h3>
        </div>
        <div style={{ padding: '16px' }}>
          {[
            { report: 'Attendance Report', user: 'Admin', date: '2026-04-08 10:30 AM', status: 'Generated' },
            { report: 'Payroll Report', user: 'HR Manager', date: '2026-04-08 09:15 AM', status: 'Generated' },
            { report: 'Performance Report', user: 'Team Lead', date: '2026-04-07 04:45 PM', status: 'Downloaded' },
            { report: 'Headcount Report', user: 'Admin', date: '2026-04-07 02:30 PM', status: 'Generated' }
          ].map((activity, index) => (
            <div key={index} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: index < 3 ? '1px solid #f3f4f6' : 'none' }}>
              <div>
                <p style={{ fontSize: '14px', fontWeight: '500', color: '#111827', margin: '0 0 4px 0' }}>{activity.report}</p>
                <p style={{ fontSize: '12px', color: '#6b7280', margin: '0' }}>{activity.user} • {activity.date}</p>
              </div>
              <span style={{ 
                padding: '4px 8px', 
                borderRadius: '4px', 
                fontSize: '12px',
                fontWeight: '500',
                backgroundColor: activity.status === 'Generated' ? '#d1fae5' : '#dbeafe',
                color: activity.status === 'Generated' ? '#065f46' : '#1e40af'
              }}>
                {activity.status}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function SettingsPage() {
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState({
    companyName: 'LOGDAY Technologies',
    companyEmail: 'hr@logday.com',
    companyPhone: '+91 8080808080',
    workingHours: '9:00 AM - 6:00 PM',
    workingDays: 'Monday - Friday',
    timezone: 'Asia/Kolkata',
    dateFormat: 'DD/MM/YYYY',
    currency: 'INR',
    emailNotifications: true,
    smsNotifications: false,
    backupEnabled: true,
    backupFrequency: 'daily'
  })

  const tabs = [
    { id: 'general', name: 'General', icon: '⚙️' },
    { id: 'company', name: 'Company', icon: '🏢' },
    { id: 'notifications', name: 'Notifications', icon: '🔔' },
    { id: 'security', name: 'Security', icon: '🔒' },
    { id: 'backup', name: 'Backup', icon: '💾' }
  ]

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Settings</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>System settings and configuration</p>
      
      {/* Settings Tabs */}
      <div style={{ display: 'flex', gap: '0', marginBottom: '24px', borderBottom: '1px solid #e5e7eb' }}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{ 
              padding: '12px 24px', 
              border: 'none', 
              borderBottom: activeTab === tab.id ? '2px solid #3b82f6' : '2px solid transparent',
              backgroundColor: 'transparent',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              color: activeTab === tab.id ? '#3b82f6' : '#6b7280',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <span>{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </div>

      {/* Settings Content */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', padding: '24px' }}>
        {activeTab === 'general' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>General Settings</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Date Format</label>
                <select value={settings.dateFormat} onChange={(e) => setSettings({...settings, dateFormat: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }}>
                  <option value="DD/MM/YYYY">DD/MM/YYYY</option>
                  <option value="MM/DD/YYYY">MM/DD/YYYY</option>
                  <option value="YYYY-MM-DD">YYYY-MM-DD</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Timezone</label>
                <select value={settings.timezone} onChange={(e) => setSettings({...settings, timezone: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }}>
                  <option value="Asia/Kolkata">Asia/Kolkata</option>
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">America/New_York</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Currency</label>
                <select value={settings.currency} onChange={(e) => setSettings({...settings, currency: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }}>
                  <option value="INR">INR (₹)</option>
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                </select>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'company' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Company Information</h3>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Company Name</label>
                <input type="text" value={settings.companyName} onChange={(e) => setSettings({...settings, companyName: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Company Email</label>
                <input type="email" value={settings.companyEmail} onChange={(e) => setSettings({...settings, companyEmail: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Company Phone</label>
                <input type="tel" value={settings.companyPhone} onChange={(e) => setSettings({...settings, companyPhone: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Working Hours</label>
                <input type="text" value={settings.workingHours} onChange={(e) => setSettings({...settings, workingHours: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Working Days</label>
                <input type="text" value={settings.workingDays} onChange={(e) => setSettings({...settings, workingDays: e.target.value})} style={{ width: '100%', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }} />
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'notifications' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Notification Settings</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
                <div>
                  <p style={{ fontSize: '16px', fontWeight: '500', color: '#111827', margin: '0 0 4px 0' }}>Email Notifications</p>
                  <p style={{ fontSize: '14px', color: '#6b7280', margin: '0' }}>Receive email notifications for important events</p>
                </div>
                <button
                  onClick={() => setSettings({...settings, emailNotifications: !settings.emailNotifications})}
                  style={{ 
                    padding: '8px 16px', 
                    backgroundColor: settings.emailNotifications ? '#10b981' : '#6b7280', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  {settings.emailNotifications ? 'Enabled' : 'Disabled'}
                </button>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
                <div>
                  <p style={{ fontSize: '16px', fontWeight: '500', color: '#111827', margin: '0 0 4px 0' }}>SMS Notifications</p>
                  <p style={{ fontSize: '14px', color: '#6b7280', margin: '0' }}>Receive SMS notifications for urgent matters</p>
                </div>
                <button
                  onClick={() => setSettings({...settings, smsNotifications: !settings.smsNotifications})}
                  style={{ 
                    padding: '8px 16px', 
                    backgroundColor: settings.smsNotifications ? '#10b981' : '#6b7280', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  {settings.smsNotifications ? 'Enabled' : 'Disabled'}
                </button>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'security' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Security Settings</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ padding: '16px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
                <p style={{ fontSize: '16px', fontWeight: '500', color: '#111827', margin: '0 0 8px 0' }}>Password Policy</p>
                <ul style={{ fontSize: '14px', color: '#6b7280', margin: '0', paddingLeft: '20px' }}>
                  <li>Minimum 8 characters</li>
                  <li>At least one uppercase letter</li>
                  <li>At least one number</li>
                  <li>At least one special character</li>
                </ul>
              </div>
              <div style={{ padding: '16px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
                <p style={{ fontSize: '16px', fontWeight: '500', color: '#111827', margin: '0 0 8px 0' }}>Session Timeout</p>
                <p style={{ fontSize: '14px', color: '#6b7280', margin: '0 0 8px 0' }}>Users will be automatically logged out after 30 minutes of inactivity</p>
                <button style={{ padding: '8px 16px', backgroundColor: '#3b82f6', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' }}>Configure</button>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'backup' && (
          <div>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#111827', marginBottom: '24px' }}>Backup Settings</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
                <div>
                  <p style={{ fontSize: '16px', fontWeight: '500', color: '#111827', margin: '0 0 4px 0' }}>Automatic Backup</p>
                  <p style={{ fontSize: '14px', color: '#6b7280', margin: '0' }}>Enable automatic data backup</p>
                </div>
                <button
                  onClick={() => setSettings({...settings, backupEnabled: !settings.backupEnabled})}
                  style={{ 
                    padding: '8px 16px', 
                    backgroundColor: settings.backupEnabled ? '#10b981' : '#6b7280', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  {settings.backupEnabled ? 'Enabled' : 'Disabled'}
                </button>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '14px', fontWeight: '500', color: '#374151', marginBottom: '8px' }}>Backup Frequency</label>
                <select value={settings.backupFrequency} onChange={(e) => setSettings({...settings, backupFrequency: e.target.value})} style={{ width: '300px', padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', fontSize: '14px' }}>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </select>
              </div>
              <div style={{ padding: '16px', border: '1px solid #dbeafe', borderRadius: '8px', backgroundColor: '#eff6ff' }}>
                <p style={{ fontSize: '14px', color: '#1e40af', margin: '0' }}>Last backup: April 8, 2026 at 2:00 AM</p>
              </div>
            </div>
          </div>
        )}
        
        {/* Save Button */}
        <div style={{ marginTop: '32px', paddingTop: '24px', borderTop: '1px solid #e5e7eb' }}>
          <button
            style={{ 
              padding: '12px 24px', 
              backgroundColor: '#10b981', 
              color: 'white', 
              border: 'none', 
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}

export default DashboardLayout
