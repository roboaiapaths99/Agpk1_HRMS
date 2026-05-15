import React, { useState } from 'react'

const LeaveManagement: React.FC = () => {
  const [leaveRequests, setLeaveRequests] = useState([
    { id: 1, employee: 'Rahul Sharma', type: 'Annual Leave', startDate: '2026-04-15', endDate: '2026-04-20', days: 5, status: 'Approved', reason: 'Family vacation' },
    { id: 2, employee: 'Priya Verma', type: 'Sick Leave', startDate: '2026-04-10', endDate: '2026-04-12', days: 3, status: 'Pending', reason: 'Medical appointment' },
    { id: 3, employee: 'Amit Kumar', type: 'Casual Leave', startDate: '2026-04-08', endDate: '2026-04-08', days: 1, status: 'Rejected', reason: 'Personal work' },
    { id: 4, employee: 'Sneha Patel', type: 'Maternity Leave', startDate: '2026-05-01', endDate: '2026-08-31', days: 90, status: 'Pending', reason: 'Maternity' },
    { id: 5, employee: 'Vikram Singh', type: 'Annual Leave', startDate: '2026-04-25', endDate: '2026-04-30', days: 5, status: 'Approved', reason: 'Vacation' }
  ])

  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    employee: '',
    type: 'Annual Leave',
    startDate: '',
    endDate: '',
    reason: ''
  })

  const leaveTypes = ['Annual Leave', 'Sick Leave', 'Casual Leave', 'Maternity Leave', 'Paternity Leave', 'Unpaid Leave']
  const statusColors = {
    'Approved': '#d1fae5',
    'Pending': '#fef3c7',
    'Rejected': '#fee2e2'
  }
  const statusTextColors = {
    'Approved': '#065f46',
    'Pending': '#92400e',
    'Rejected': '#991b1b'
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddLeaveRequest = () => {
    if (!formData.employee || !formData.startDate || !formData.endDate || !formData.reason) {
      alert('Please fill in all required fields')
      return
    }

    const start = new Date(formData.startDate)
    const end = new Date(formData.endDate)
    const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1

    const newRequest = {
      id: leaveRequests.length + 1,
      ...formData,
      days,
      status: 'Pending'
    }

    setLeaveRequests(prev => [...prev, newRequest])
    setFormData({
      employee: '',
      type: 'Annual Leave',
      startDate: '',
      endDate: '',
      reason: ''
    })
    setShowAddForm(false)
    alert('Leave request submitted successfully!')
  }

  const handleStatusUpdate = (id, newStatus) => {
    setLeaveRequests(prev => 
      prev.map(request => 
        request.id === id ? { ...request, status: newStatus } : request
      )
    )
  }

  const stats = {
    total: leaveRequests.length,
    approved: leaveRequests.filter(r => r.status === 'Approved').length,
    pending: leaveRequests.filter(r => r.status === 'Pending').length,
    rejected: leaveRequests.filter(r => r.status === 'Rejected').length
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Leave Management</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Manage employee leave requests and approvals</p>
      
      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{stats.total}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Requests</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: '0' }}>{stats.approved}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Approved</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: '0' }}>{stats.pending}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Pending</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#ef4444', margin: '0' }}>{stats.rejected}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Rejected</p>
        </div>
      </div>

      {/* Add Leave Request Button */}
      <div style={{ marginBottom: '24px' }}>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          style={{ 
            padding: '12px 24px', 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          + Request Leave
        </button>
      </div>

      {/* Add Leave Request Form */}
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
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Request Leave</h3>
            <button
              onClick={() => {
                setShowAddForm(false)
                setFormData({
                  employee: '',
                  type: 'Annual Leave',
                  startDate: '',
                  endDate: '',
                  reason: ''
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
              name="employee"
              placeholder="Employee Name *" 
              value={formData.employee}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <select 
              name="type"
              value={formData.type}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            >
              {leaveTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            <input 
              type="date" 
              name="startDate"
              placeholder="Start Date *" 
              value={formData.startDate}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <input 
              type="date" 
              name="endDate"
              placeholder="End Date *" 
              value={formData.endDate}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <textarea 
              name="reason"
              placeholder="Reason *" 
              value={formData.reason}
              onChange={handleInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', width: '100%', minHeight: '80px' }} 
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <button
              onClick={handleAddLeaveRequest}
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
              Submit Request
            </button>
            <button
              onClick={() => {
                setShowAddForm(false)
                setFormData({
                  employee: '',
                  type: 'Annual Leave',
                  startDate: '',
                  endDate: '',
                  reason: ''
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

      {/* Leave Requests Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Leave Requests</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Employee</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Leave Type</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Duration</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Days</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Reason</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {leaveRequests.map((request) => (
              <tr key={request.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                  {request.employee}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {request.type}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {request.startDate} to {request.endDate}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {request.days}
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
                    backgroundColor: statusColors[request.status],
                    color: statusTextColors[request.status]
                  }}>
                    {request.status}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {request.status === 'Pending' && (
                      <>
                        <button
                          onClick={() => handleStatusUpdate(request.id, 'Approved')}
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
                          Approve
                        </button>
                        <button
                          onClick={() => handleStatusUpdate(request.id, 'Rejected')}
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
                          Reject
                        </button>
                      </>
                    )}
                    <button style={{ 
                      padding: '4px 8px', 
                      backgroundColor: '#3b82f6', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}>
                      View
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

export default LeaveManagement
