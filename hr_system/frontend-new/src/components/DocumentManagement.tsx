import React, { useState } from 'react'

const DocumentManagement: React.FC = () => {
  const [documents, setDocuments] = useState([
    { id: 1, name: 'Employee Handbook.pdf', category: 'Company Policies', uploadedBy: 'HR Admin', uploadDate: '2026-04-01', size: '2.4 MB', status: 'Active', downloads: 45 },
    { id: 2, name: 'Employment Contract Template.docx', category: 'Templates', uploadedBy: 'Legal Team', uploadDate: '2026-04-05', size: '1.2 MB', status: 'Active', downloads: 32 },
    { id: 3, name: 'Performance Review Guidelines.pdf', category: 'HR Processes', uploadedBy: 'HR Manager', uploadDate: '2026-04-08', size: '1.8 MB', status: 'Active', downloads: 28 },
    { id: 4, name: 'Leave Policy 2026.pdf', category: 'Company Policies', uploadedBy: 'HR Admin', uploadDate: '2026-03-15', size: '3.1 MB', status: 'Archived', downloads: 67 },
    { id: 5, name: 'Onboarding Checklist.xlsx', category: 'Templates', uploadedBy: 'HR Team', uploadDate: '2026-04-10', size: '0.5 MB', status: 'Active', downloads: 19 },
    { id: 6, name: 'Salary Structure 2026.docx', category: 'Compensation', uploadedBy: 'Finance', uploadDate: '2026-04-12', size: '2.7 MB', status: 'Active', downloads: 8 },
    { id: 7, name: 'Code of Conduct.pdf', category: 'Company Policies', uploadedBy: 'Legal Team', uploadDate: '2026-04-02', size: '1.5 MB', status: 'Active', downloads: 52 },
    { id: 8, name: 'Training Materials.zip', category: 'Training', uploadedBy: 'L&D Team', uploadDate: '2026-04-11', size: '15.3 MB', status: 'Active', downloads: 15 }
  ])

  const [categories] = useState([
    'Company Policies',
    'Templates', 
    'HR Processes',
    'Compensation',
    'Training',
    'Legal Documents',
    'Forms'
  ])

  const [activeTab, setActiveTab] = useState('documents')
  const [showUploadForm, setShowUploadForm] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [uploadFormData, setUploadFormData] = useState({
    name: '',
    category: 'Company Policies',
    description: ''
  })

  const statusColors = {
    'Active': '#d1fae5',
    'Archived': '#fee2e2',
    'Draft': '#fef3c7'
  }

  const statusTextColors = {
    'Active': '#065f46',
    'Archived': '#991b1b',
    'Draft': '#92400e'
  }

  const handleUploadInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target
    setUploadFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleFileUpload = () => {
    if (!uploadFormData.name || !uploadFormData.category) {
      alert('Please fill in all required fields')
      return
    }

    const newDocument = {
      id: documents.length + 1,
      ...uploadFormData,
      uploadedBy: 'Current User',
      uploadDate: new Date().toISOString().split('T')[0],
      size: '0.0 MB',
      status: 'Active',
      downloads: 0
    }

    setDocuments(prev => [...prev, newDocument])
    setUploadFormData({
      name: '',
      category: 'Company Policies',
      description: ''
    })
    setShowUploadForm(false)
    alert('Document uploaded successfully!')
  }

  const handleDocumentStatusUpdate = (id: number, newStatus: string) => {
    setDocuments(prev => 
      prev.map(doc => 
        doc.id === id ? { ...doc, status: newStatus } : doc
      )
    )
  }

  const filteredDocuments = documents.filter(doc => {
    const matchesSearch = doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         doc.uploadedBy.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || doc.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const stats = {
    totalDocuments: documents.length,
    activeDocuments: documents.filter(d => d.status === 'Active').length,
    totalDownloads: documents.reduce((acc, doc) => acc + doc.downloads, 0),
    totalSize: '29.5 MB'
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Document Management</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Manage company documents, templates, and policies</p>
      
      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{stats.totalDocuments}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Documents</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: '0' }}>{stats.activeDocuments}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Active</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#3b82f6', margin: '0' }}>{stats.totalDownloads}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Downloads</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: '0' }}>{stats.totalSize}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Size</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <input
          type="text"
          placeholder="Search documents..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{ 
            flex: 1, 
            minWidth: '200px',
            padding: '8px 12px', 
            border: '1px solid #e5e7eb', 
            borderRadius: '6px',
            fontSize: '14px'
          }}
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          style={{ 
            padding: '8px 12px', 
            border: '1px solid #e5e7eb', 
            borderRadius: '6px',
            fontSize: '14px'
          }}
        >
          <option value="all">All Categories</option>
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
        <button
          onClick={() => setShowUploadForm(!showUploadForm)}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          + Upload Document
        </button>
      </div>

      {/* Upload Document Form */}
      {showUploadForm && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px', 
          border: '2px solid #3b82f6',
          marginBottom: '24px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', margin: 0 }}>Upload Document</h3>
            <button
              onClick={() => setShowUploadForm(false)}
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
              placeholder="Document Name *" 
              value={uploadFormData.name}
              onChange={handleUploadInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            />
            <select 
              name="category"
              value={uploadFormData.category}
              onChange={handleUploadInputChange}
              style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px' }} 
            >
              {categories.map(category => (
                <option key={category} value={category}>{category}</option>
              ))}
            </select>
            <div style={{ gridColumn: '1 / -1' }}>
              <input 
                type="file" 
                style={{ padding: '8px 12px', border: '1px solid #e5e7eb', borderRadius: '6px', width: '100%' }} 
              />
            </div>
            <textarea 
              name="description"
              placeholder="Description"
              value={uploadFormData.description}
              onChange={handleUploadInputChange}
              style={{ 
                padding: '8px 12px', 
                border: '1px solid #e5e7eb', 
                borderRadius: '6px', 
                width: '100%', 
                minHeight: '80px',
                gridColumn: '1 / -1'
              }} 
            />
          </div>
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
            <button
              onClick={handleFileUpload}
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
              Upload Document
            </button>
            <button
              onClick={() => setShowUploadForm(false)}
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

      {/* Documents Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>Documents Library</h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Document</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Category</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Uploaded By</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Upload Date</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Size</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Downloads</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredDocuments.map((doc) => (
              <tr key={doc.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ 
                      width: '32px', 
                      height: '32px', 
                      backgroundColor: '#f3f4f6', 
                      borderRadius: '6px', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      color: '#6b7280'
                    }}>
                      {doc.name.split('.').pop()?.toUpperCase()}
                    </div>
                    <div>
                      <div style={{ fontWeight: '500' }}>{doc.name}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>
                        ID: DOC-{doc.id.toString().padStart(4, '0')}
                      </div>
                    </div>
                  </div>
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    backgroundColor: '#f3f4f6',
                    color: '#374151'
                  }}>
                    {doc.category}
                  </span>
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {doc.uploadedBy}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {doc.uploadDate}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {doc.size}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ fontSize: '12px', color: '#6b7280' }}>↓</span>
                    {doc.downloads}
                  </div>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: statusColors[doc.status as keyof typeof statusColors],
                    color: statusTextColors[doc.status as keyof typeof statusTextColors]
                  }}>
                    {doc.status}
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
                      Download
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
                      View
                    </button>
                    {doc.status === 'Active' && (
                      <button
                        onClick={() => handleDocumentStatusUpdate(doc.id, 'Archived')}
                        style={{ 
                          padding: '4px 8px', 
                          backgroundColor: '#f59e0b', 
                          color: 'white', 
                          border: 'none', 
                          borderRadius: '4px',
                          cursor: 'pointer',
                          fontSize: '12px'
                        }}
                      >
                        Archive
                      </button>
                    )}
                    {doc.status === 'Archived' && (
                      <button
                        onClick={() => handleDocumentStatusUpdate(doc.id, 'Active')}
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
                        Restore
                      </button>
                    )}
                    <button style={{ 
                      padding: '4px 8px', 
                      backgroundColor: '#ef4444', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '12px'
                    }}>
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

export default DocumentManagement
