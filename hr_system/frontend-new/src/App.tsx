import { Routes, Route, Navigate } from 'react-router-dom'

// Import layout and page components
import DashboardLayout from './DashboardLayout'
import Dashboard from './components/Dashboard'
import Employees from './components/Employees'
import Payroll from './components/Payroll'
import Attendance from './components/Attendance'
import Onboarding from './components/Onboarding'
import ExitManagement from './components/ExitManagement'
import Reports from './components/Reports'
import Settings from './components/Settings'
import Login from './components/Login'
import LeaveManagement from './components/LeaveManagement'
import PerformanceManagement from './components/PerformanceManagement'
import Recruitment from './components/Recruitment'
import DocumentManagement from './components/DocumentManagement'

// Main App component
function App() {
  return (
    <div className="App">
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<DashboardLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="employees" element={<Employees />} />
          <Route path="attendance" element={<Attendance />} />
          <Route path="payroll" element={<Payroll />} />
          <Route path="leave-management" element={<LeaveManagement />} />
          <Route path="performance-management" element={<PerformanceManagement />} />
          <Route path="recruitment" element={<Recruitment />} />
          <Route path="document-management" element={<DocumentManagement />} />
          <Route path="onboarding" element={<Onboarding />} />
          <Route path="exit-management" element={<ExitManagement />} />
          <Route path="reports" element={<Reports />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </div>
  )
}

export default App
