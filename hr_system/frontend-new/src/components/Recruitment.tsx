import React, { useState } from 'react'

const Recruitment: React.FC = () => {
  const [jobPostings, setJobPostings] = useState([
    { id: 1, title: 'Senior React Developer', department: 'Engineering', location: 'Mumbai', type: 'Full-time', status: 'Active', postedDate: '2026-04-01', applicants: 12, description: 'Looking for experienced React developer with 5+ years experience' },
    { id: 2, title: 'HR Manager', department: 'HR', location: 'Delhi', type: 'Full-time', status: 'Active', postedDate: '2026-04-05', applicants: 8, description: 'Seeking experienced HR Manager to lead our HR team' },
    { id: 3, title: 'Sales Executive', department: 'Sales', location: 'Bangalore', type: 'Full-time', status: 'Active', postedDate: '2026-04-08', applicants: 15, description: 'Dynamic sales professional needed for expanding team' },
    { id: 4, title: 'Marketing Specialist', department: 'Marketing', location: 'Pune', type: 'Contract', status: 'Closed', postedDate: '2026-03-15', applicants: 20, description: 'Marketing specialist for campaign management' },
    { id: 5, title: 'DevOps Engineer', department: 'Engineering', location: 'Hyderabad', type: 'Full-time', status: 'Active', postedDate: '2026-04-10', applicants: 6, description: 'DevOps engineer with cloud experience required' }
  ])

  const [candidates, setCandidates] = useState([
    { id: 1, name: 'John Doe', email: 'john.doe@email.com', phone: '+91 98765 43210', position: 'Senior React Developer', status: 'Screening', appliedDate: '2026-04-02', experience: '5 years', skills: 'React, Node.js, TypeScript' },
    { id: 2, name: 'Jane Smith', email: 'jane.smith@email.com', phone: '+91 98765 43211', position: 'HR Manager', status: 'Interview', appliedDate: '2026-04-06', experience: '8 years', skills: 'HR Management, Recruitment, Employee Relations' },
    { id: 3, name: 'Mike Johnson', email: 'mike.j@email.com', phone: '+91 98765 43212', position: 'Sales Executive', status: 'Offer', appliedDate: '2026-04-09', experience: '3 years', skills: 'Sales, CRM, Communication' },
    { id: 4, name: 'Sarah Wilson', email: 'sarah.w@email.com', phone: '+91 98765 43213', position: 'Marketing Specialist', status: 'Rejected', appliedDate: '2026-03-16', experience: '4 years', skills: 'Digital Marketing, SEO, Content' },
    { id: 5, name: 'David Brown', email: 'david.b@email.com', phone: '+91 98765 43214', position: 'DevOps Engineer', status: 'Screening', appliedDate: '2026-04-11', experience: '6 years', skills: 'AWS, Docker, Kubernetes, CI/CD' }
  ])

  const [activeTab, setActiveTab] = useState('jobs')
  const [showAddJobForm, setShowAddJobForm] = useState(false)
  const [jobFormData, setJobFormData] = useState({
    title: '',
    department: '',
    location: '',
    type: 'Full-time',
    description: '',
    requirements: '',
    salary: ''
  })

  const statusColors = {
    'Active': '#d1fae5',
    'Closed': '#fee2e2',
    'Screening': '#fef3c7',
    'Interview': '#dbeafe',
    'Offer': '#e0e7ff',
    'Rejected': '#fee2e2',
    'Hired': '#d1fae5'
  }

  const statusTextColors = {
    'Active': '#065f46',
    'Closed': '#991b1b',
    'Screening': '#92400e',
    'Interview': '#1e40af',
    'Offer': '#4338ca',
    'Rejected': '#991b1b',
    'Hired': '#065f46'
  }

  const handleJobInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setJobFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleAddJobPosting = () => {
    if (!jobFormData.title || !jobFormData.department || !jobFormData.location) {
      alert('Please fill in all required fields')
      return
    }

    const newJob = {
      id: jobPostings.length + 1,
      ...jobFormData,
      status: 'Active',
      postedDate: new Date().toISOString().split('T')[0],
      applicants: 0
    }

    setJobPostings(prev => [...prev, newJob])
    setJobFormData({
      title: '',
      department: '',
      location: '',
      type: 'Full-time',
      description: '',
      requirements: '',
      salary: ''
    })
    setShowAddJobForm(false)
    alert('Job posting created successfully!')
  }

  const handleCandidateStatusUpdate = (id: number, newStatus: string) => {
    setCandidates(prev => 
      prev.map(candidate => 
        candidate.id === id ? { ...candidate, status: newStatus } : candidate
      )
    )
  }

  const stats = {
    activeJobs: jobPostings.filter(j => j.status === 'Active').length,
    totalCandidates: candidates.length,
    screeningCandidates: candidates.filter(c => c.status === 'Screening').length,
    interviewCandidates: candidates.filter(c => c.status === 'Interview').length,
    offers: candidates.filter(c => c.status === 'Offer').length
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Recruitment Management</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Manage job postings and candidate pipeline</p>
      
      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{stats.activeJobs}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Active Jobs</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#3b82f6', margin: '0' }}>{stats.totalCandidates}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Candidates</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: '0' }}>{stats.interviewCandidates}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>In Interview</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: '0' }}>{stats.offers}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Offers Extended</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '0', marginBottom: '24px', borderBottom: '1px solid #e5e7eb' }}>
        <button
          onClick={() => setActiveTab('jobs')}
          style={{ 
            padding: '12px 24px', 
            border: 'none', 
            borderBottom: activeTab === 'jobs' ? '2px solid #3b82f6' : '2px solid transparent',
            backgroundColor: 'transparent',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            color: activeTab === 'jobs' ? '#3b82f6' : '#6b7280'
          }}
        >
          Job Postings
        </button>
        <button
          onClick={() => setActiveTab('candidates')}
          style={{ 
            padding: '12px 24px', 
            border: 'none', 
            borderBottom: activeTab === 'candidates' ? '2px solid #3b82f6' : '2px solid transparent',
            backgroundColor: 'transparent',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500',
            color: activeTab === 'candidates' ? '#3b82f6' : '#6b7280'
          }}
        >
          Candidates
        </button>
      </div>

      {/* Job Postings Tab */}
      {activeTab === 'jobs' && (
        <>
          <div style={{ marginBottom: '24px' }}>
            <button
              onClick={() => setShowAddJobForm(!showAddJobForm)}
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
              + Post New Job
            </button>
          </div>

          {/* Add Job Form */}
          {showAddJobForm && (
            <div style={{ 
              backgroundColor: 'white', 
              padding: '24px', 
              borderRadius: '12px', 
              border: '2px solid #3b82f6',
              marginBottom: '24px',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Create Job Posting</h3>
                <button
                  onClick={() => setShowAddJobForm(false)}
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
                  name="title"
                  placeholder="Job Title *" 
                  value={jobFormData.title}
                  onChange={handleJobInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                />
                <select 
                  name="department"
                  value={jobFormData.department}
                  onChange={handleJobInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                >
                  <option value="">Select Department</option>
                  <option value="Engineering">Engineering</option>
                  <option value="HR">HR</option>
                  <option value="Sales">Sales</option>
                  <option value="Marketing">Marketing</option>
                  <option value="Finance">Finance</option>
                </select>
                <input 
                  type="text" 
                  name="location"
                  placeholder="Location *" 
                  value={jobFormData.location}
                  onChange={handleJobInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                />
                <select 
                  name="type"
                  value={jobFormData.type}
                  onChange={handleJobInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                >
                  <option value="Full-time">Full-time</option>
                  <option value="Part-time">Part-time</option>
                  <option value="Contract">Contract</option>
                  <option value="Internship">Internship</option>
                </select>
                <input 
                  type="text" 
                  name="salary"
                  placeholder="Salary Range" 
                  value={jobFormData.salary}
                  onChange={handleJobInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
                />
              </div>
              <div style={{ marginTop: '16px' }}>
                <textarea 
                  name="description"
                  placeholder="Job Description *"
                  value={jobFormData.description}
                  onChange={handleJobInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', width: '100%', minHeight: '100px', marginBottom: '16px' }} 
                />
                <textarea 
                  name="requirements"
                  placeholder="Requirements & Qualifications"
                  value={jobFormData.requirements}
                  onChange={handleJobInputChange}
                  style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', width: '100%', minHeight: '100px' }} 
                />
              </div>
              <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                <button
                  onClick={handleAddJobPosting}
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
                  Post Job
                </button>
                <button
                  onClick={() => setShowAddJobForm(false)}
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

          {/* Job Postings Table */}
          <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
            <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
              <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Job Postings</h3>
            </div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ backgroundColor: '#f9fafb' }}>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Position</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Department</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Location</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Type</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Posted</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Applicants</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
                  <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobPostings.map((job) => (
                  <tr key={job.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                      <div>
                        <div style={{ fontWeight: '500' }}>{job.title}</div>
                        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>{job.description}</div>
                      </div>
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      {job.department}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      {job.location}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      {job.type}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      {job.postedDate}
                    </td>
                    <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: '#dbeafe',
                        color: '#1e40af'
                      }}>
                        {job.applicants}
                      </span>
                    </td>
                    <td style={{ padding: '12px 16px' }}>
                      <span style={{ 
                        padding: '4px 8px', 
                        borderRadius: '4px', 
                        fontSize: '12px',
                        fontWeight: '500',
                        backgroundColor: statusColors[job.status as keyof typeof statusColors],
                        color: statusTextColors[job.status as keyof typeof statusTextColors]
                      }}>
                        {job.status}
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
                        {job.status === 'Active' && (
                          <button style={{ 
                            padding: '4px 8px', 
                            backgroundColor: '#ef4444', 
                            color: 'white', 
                            border: 'none', 
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}>
                            Close
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Candidates Tab */}
      {activeTab === 'candidates' && (
        <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
          <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
            <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Candidates Pipeline</h3>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f9fafb' }}>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Candidate</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Position</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Applied</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Experience</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Skills</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
                <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {candidates.map((candidate) => (
                <tr key={candidate.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    <div>
                      <div style={{ fontWeight: '500' }}>{candidate.name}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>{candidate.email}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>{candidate.phone}</div>
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    {candidate.position}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    {candidate.appliedDate}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    {candidate.experience}
                  </td>
                  <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                    <div style={{ fontSize: '12px' }}>
                      {candidate.skills.split(',').map((skill, index) => (
                        <span key={index} style={{ 
                          display: 'inline-block',
                          padding: '2px 6px',
                          backgroundColor: '#f3f4f6',
                          borderRadius: '4px',
                          margin: '2px 2px 2px 0',
                          fontSize: '11px'
                        }}>
                          {skill.trim()}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <span style={{ 
                      padding: '4px 8px', 
                      borderRadius: '4px', 
                      fontSize: '12px',
                      fontWeight: '500',
                      backgroundColor: statusColors[candidate.status as keyof typeof statusColors],
                      color: statusTextColors[candidate.status as keyof typeof statusTextColors]
                    }}>
                      {candidate.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px 16px' }}>
                    <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
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
                      {candidate.status === 'Screening' && (
                        <button
                          onClick={() => handleCandidateStatusUpdate(candidate.id, 'Interview')}
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
                          Interview
                        </button>
                      )}
                      {candidate.status === 'Interview' && (
                        <button
                          onClick={() => handleCandidateStatusUpdate(candidate.id, 'Offer')}
                          style={{ 
                            padding: '4px 8px', 
                            backgroundColor: '#8b5cf6', 
                            color: 'white', 
                            border: 'none', 
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '12px'
                          }}
                        >
                          Offer
                        </button>
                      )}
                      {candidate.status === 'Offer' && (
                        <button
                          onClick={() => handleCandidateStatusUpdate(candidate.id, 'Hired')}
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
                          Hire
                        </button>
                      )}
                      <button
                        onClick={() => handleCandidateStatusUpdate(candidate.id, 'Rejected')}
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

export default Recruitment
