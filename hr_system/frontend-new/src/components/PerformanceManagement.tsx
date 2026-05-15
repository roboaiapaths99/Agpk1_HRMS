import React, { useState } from 'react'

const PerformanceManagement: React.FC = () => {
  const [evaluations, setEvaluations] = useState([
    { id: 1, employee: 'Rahul Sharma', period: 'Q1 2026', rating: 4.5, status: 'Completed', reviewer: 'Tech Lead', date: '2026-04-01' },
    { id: 2, employee: 'Priya Verma', period: 'Q1 2026', rating: 4.2, status: 'In Progress', reviewer: 'HR Manager', date: '2026-04-05' },
    { id: 3, employee: 'Amit Kumar', period: 'Q1 2026', rating: 3.8, status: 'Pending', reviewer: 'Sales Manager', date: '2026-04-10' },
    { id: 4, employee: 'Sneha Patel', period: 'Q1 2026', rating: 4.7, status: 'Completed', reviewer: 'Marketing Head', date: '2026-03-28' },
    { id: 5, employee: 'Vikram Singh', period: 'Q1 2026', rating: 4.3, status: 'Completed', reviewer: 'DevOps Lead', date: '2026-04-02' }
  ])

  const [goals, setGoals] = useState([
    { id: 1, employee: 'Rahul Sharma', title: 'Complete React Migration', description: 'Migrate legacy system to React', targetDate: '2026-04-30', status: 'On Track', progress: 75 },
    { id: 2, employee: 'Priya Verma', title: 'Reduce Turnover Rate', description: 'Implement retention strategies', targetDate: '2026-06-30', status: 'At Risk', progress: 40 },
    { id: 3, employee: 'Amit Kumar', title: 'Increase Sales by 15%', description: 'Q2 sales target achievement', targetDate: '2026-06-30', status: 'On Track', progress: 60 },
    { id: 4, employee: 'Sneha Patel', title: 'Launch New Campaign', description: 'Q2 marketing campaign', targetDate: '2026-05-15', status: 'Completed', progress: 100 },
    { id: 5, employee: 'Vikram Singh', title: 'Improve System Uptime', description: 'Achieve 99.9% uptime', targetDate: '2026-04-30', status: 'On Track', progress: 85 }
  ])

  const [activeTab, setActiveTab] = useState('evaluations')
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState({
    employee: '',
    period: '',
    rating: '',
    reviewer: '',
    goals: '',
    achievements: '',
    areasForImprovement: ''
  })

  const statusColors = {
    'Completed': '#d1fae5',
    'In Progress': '#dbeafe',
    'Pending': '#fef3c7',
    'On Track': '#d1fae5',
    'At Risk': '#fee2e2'
  }

  const statusTextColors = {
    'Completed': '#065f46',
    'In Progress': '#1e40af',
    'Pending': '#92400e',
    'On Track': '#065f46',
    'At Risk': '#991b1b'
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddEvaluation = () => {
    if (!formData.employee || !formData.period || !formData.rating) {
      alert('Please fill in all required fields')
      return
    }

    const newEvaluation = {
      id: evaluations.length + 1,
      ...formData,
      date: new Date().toISOString().split('T')[0],
      status: 'In Progress'
    }

    setEvaluations(prev => [...prev, newEvaluation])
    setFormData({
      employee: '',
      period: '',
      rating: '',
      reviewer: '',
      goals: '',
      achievements: '',
      areasForImprovement: ''
    })
    setShowAddForm(false)
    alert('Performance evaluation created successfully!')
  }

  const stats = {
    totalEvaluations: evaluations.length,
    completedEvaluations: evaluations.filter(e => e.status === 'Completed').length,
    averageRating: (evaluations.reduce((acc, e) => acc + e.rating, 0) / evaluations.length).toFixed(1),
    totalGoals: goals.length,
    completedGoals: goals.filter(g => g.status === 'Completed').length
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Performance Management</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Manage employee performance evaluations and goals</p>
      
      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{stats.totalEvaluations}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Evaluations</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: '0' }}>{stats.completedEvaluations}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Completed</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: '0' }}>{stats.averageRating}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Average Rating</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#3b82f6', margin: '0' }}>{stats.completedGoals}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Goals Completed</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0', marginBottom: '24px', borderBottom: '1px solid #e5e7eb' }}>
        <button
          onClick={() => setActiveTab('evaluations')}
          style={{ 
            padding: '12px 24px', 
            border: 'none', 
            borderBottom: activeTab === 'evaluations' ? '2px solid #3b82f6' : '2px solid transparent',
            backgroundColor: 'transparent',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            color: activeTab === 'evaluations' ? '#3b82f6' : '#6b7280'
          }}
        >
          Performance Evaluations
        </button>
        <button
          onClick={() => setActiveTab('goals')}
          style={{ 
            padding: '12px 24px', 
            border: 'none', 
            borderBottom: activeTab === 'goals' ? '2px solid #3b82f6' : '2px solid transparent',
            backgroundColor: 'transparent',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            color: activeTab === 'goals' ? '#3b82f6' : '#6b7280'
          }}
        >
          Goals & Objectives
        </button>
      </div>

      {/* Performance Evaluations Tab */}
      {activeTab === 'evaluations' && (
        <>
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
              + New Evaluation
            </button>
          </div>

          {/* Add Evaluation Form */}
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
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Create Performance Evaluation</h3>
                <button
                  onClick={() => setShowAddForm(false)}
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
                  name="period"
                  value={formData.period}
                  onChange={handleInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                >
                  <option value="">Select Period</option>
                  <option value="Q1 2026">Q1 2026</option>
                  <option value="Q4 2025">Q4 2025</option>
                  <option value="Q3 2025">Q3 2025</option>
                </select>
                <select 
                  name="rating"
                  value={formData.rating}
                  onChange={handleInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                >
                  <option value="">Select Rating</option>
                  <option value="5">5 - Outstanding</option>
                  <option value="4">4 - Exceeds Expectations</option>
                  <option value="3">3 - Meets Expectations</option>
                  <option value="2">2 - Needs Improvement</option>
                  <option value="1">1 - Unsatisfactory</option>
                </select>
                <input 
                  type="text" 
                  name="reviewer"
                  placeholder="Reviewer Name *" 
                  value={formData.reviewer}
                  onChange={handleInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                />
              </div>
              <div style={{ marginTop: '16px' }}>
                <textarea 
                  name="goals"
                  placeholder="Goals and Objectives"
                  value={formData.goals}
                  onChange={handleInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', width: '100%', minHeight: '80px', marginBottom: '16px' }} 
                />
                <textarea 
                  name="achievements"
                  placeholder="Key Achievements"
                  value={formData.achievements}
                  onChange={handleInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', width: '100%', minHeight: '80px', marginBottom: '16px' }} 
                />
                <textarea 
                  name="areasForImprovement"
                  placeholder="Areas for Improvement"
                  value={formData.areasForImprovement}
                  onChange={handleInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', width: '100%', minHeight: '80px' }} 
                />
              </div>
              <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                <button
                  onClick={handleAddEvaluation}
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
                  Create Evaluation
                </button>
                <button
                  onClick={() => setShowAddForm(false)}
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

          {/* Evaluations Table */}
          <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
            <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Performance Evaluations</h3>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f9fafb' }}>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Employee</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Period</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Rating</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Reviewer</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Date</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {evaluations.map((evaluation) => (
                  <tr key={evaluation.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                      {evaluation.employee}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      {evaluation.period}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontSize: '16px', fontWeight: 'bold' }}>{evaluation.rating}</span>
                        <div style={{ display: 'flex', gap: '2px' }}>
                          {[1, 2, 3, 4, 5].map((star) => (
                            <span key={star} style={{ color: star <= evaluation.rating ? '#f59e0b' : '#e5e7eb' }}>
                              ★
                            </span>
                          ))}
                        </div>
                      </div>
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      {evaluation.reviewer}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      {evaluation.date}
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: statusColors[evaluation.status as keyof typeof statusColors],
                        color: statusTextColors[evaluation.status as keyof typeof statusTextColors]
                      }}>
                        {evaluation.status}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <div style={{ display: 'flex', gap: '8px' }}>
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
                        <button style={{ 
                          padding: '4px 8px', 
                          backgroundColor: '#10b981', 
                          color: 'white', 
                          border: 'none', 
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}>
                          Edit
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Goals & Objectives Tab */}
      {activeTab === 'goals' && (
        <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
          <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Goals & Objectives</h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Employee</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Goal Title</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Description</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Target Date</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Progress</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {goals.map((goal) => (
                <tr key={goal.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                    {goal.employee}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    {goal.title}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    {goal.description}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    {goal.targetDate}
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{ flex: 1, height: '8px', backgroundColor: '#f3f4f6', borderRadius: '4px', overflow: 'hidden' }}>
                        <div style={{ 
                          height: '100%', 
                          backgroundColor: goal.progress === 100 ? '#10b981' : goal.progress >= 60 ? '#3b82f6' : '#f59e0b', 
                          borderRadius: '4px',
                          width: `${goal.progress}%`
                        }}></div>
                      </div>
                      <span style={{ fontSize: '12px', color: '#6b7280', minWidth: '35px' }}>{goal.progress}%</span>
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '4px', 
                      fontSize: '12px',
                      fontWeight: '500',
                      backgroundColor: statusColors[goal.status as keyof typeof statusColors],
                      color: statusTextColors[goal.status as keyof typeof statusTextColors]
                    }}>
                      {goal.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
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
                      <button style={{ 
                        padding: '4px 8px', 
                        backgroundColor: '#10b981', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '12px'
                      }}>
                        Update
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default PerformanceManagement
