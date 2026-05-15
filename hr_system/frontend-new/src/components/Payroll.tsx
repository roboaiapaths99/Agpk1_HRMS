import React, { useState } from 'react'

const Payroll: React.FC = () => {
  const [payrollRecords, setPayrollRecords] = useState([
    { 
      id: 1, 
      employee: 'Rahul Sharma', 
      department: 'Engineering', 
      basicSalary: 80000,
      hra: 24000,
      da: 8000,
      allowances: 12000,
      grossSalary: 124000,
      pf: 9600,
      professionalTax: 200,
      tds: 12000,
      otherDeductions: 1500,
      totalDeductions: 23300,
      netSalary: 100700,
      month: 'April 2026',
      status: 'Processed',
      paymentDate: '2026-04-30'
    },
    { 
      id: 2, 
      employee: 'Priya Verma', 
      department: 'HR', 
      basicSalary: 60000,
      hra: 18000,
      da: 6000,
      allowances: 8000,
      grossSalary: 92000,
      pf: 7200,
      professionalTax: 200,
      tds: 8000,
      otherDeductions: 1200,
      totalDeductions: 16600,
      netSalary: 75400,
      month: 'April 2026',
      status: 'Processed',
      paymentDate: '2026-04-30'
    },
    { 
      id: 3, 
      employee: 'Amit Kumar', 
      department: 'Sales', 
      basicSalary: 50000,
      hra: 15000,
      da: 5000,
      allowances: 10000,
      grossSalary: 80000,
      pf: 6000,
      professionalTax: 200,
      tds: 6000,
      otherDeductions: 1000,
      totalDeductions: 13200,
      netSalary: 66800,
      month: 'April 2026',
      status: 'Pending',
      paymentDate: ''
    },
    { 
      id: 4, 
      employee: 'Sneha Patel', 
      department: 'Marketing', 
      basicSalary: 65000,
      hra: 19500,
      da: 6500,
      allowances: 9000,
      grossSalary: 100000,
      pf: 7800,
      professionalTax: 200,
      tds: 10000,
      otherDeductions: 1300,
      totalDeductions: 19300,
      netSalary: 80700,
      month: 'April 2026',
      status: 'Processed',
      paymentDate: '2026-04-30'
    },
    { 
      id: 5, 
      employee: 'Vikram Singh', 
      department: 'Engineering', 
      basicSalary: 75000,
      hra: 22500,
      da: 7500,
      allowances: 11000,
      grossSalary: 116000,
      pf: 9000,
      professionalTax: 200,
      tds: 11000,
      otherDeductions: 1400,
      totalDeductions: 21600,
      netSalary: 94400,
      month: 'April 2026',
      status: 'Pending',
      paymentDate: ''
    }
  ])

  const [selectedMonth, setSelectedMonth] = useState('April 2026')
  const [showPayslip, setShowPayslip] = useState(false)
  const [selectedEmployee, setSelectedEmployee] = useState<any>(null)
  const [showProcessPayroll, setShowProcessPayroll] = useState(false)
  const [showCalculator, setShowCalculator] = useState(false)
  const [calculatorData, setCalculatorData] = useState({
    basicSalary: 50000,
    hraPercentage: 30,
    daPercentage: 10,
    allowancesPercentage: 15,
    pfPercentage: 12,
    professionalTax: 200,
    tdsPercentage: 10,
    otherDeductions: 750
  })

  const statusColors = {
    'Processed': '#d1fae5',
    'Pending': '#fef3c7',
    'Failed': '#fee2e2'
  }

  const statusTextColors = {
    'Processed': '#065f46',
    'Pending': '#92400e',
    'Failed': '#991b1b'
  }

  const calculateSalary = (basic: number, percentages: any) => {
    const hra = basic * (percentages.hraPercentage / 100)
    const da = basic * (percentages.daPercentage / 100)
    const allowances = basic * (percentages.allowancesPercentage / 100)
    const gross = basic + hra + da + allowances
    const pf = basic * (percentages.pfPercentage / 100)
    const professionalTax = percentages.professionalTax
    const tds = gross * (percentages.tdsPercentage / 100)
    const otherDeductions = percentages.otherDeductions
    const totalDeductions = pf + professionalTax + tds + otherDeductions
    const net = gross - totalDeductions

    return {
      basicSalary: basic,
      hra,
      da,
      allowances,
      grossSalary: gross,
      pf,
      professionalTax,
      tds,
      otherDeductions,
      totalDeductions,
      netSalary: net
    }
  }

  const currentCalculation = calculateSalary(calculatorData.basicSalary, calculatorData)

  const processPayroll = () => {
    const pendingRecords = payrollRecords.filter(record => record.status === 'Pending')
    const updatedRecords = payrollRecords.map(record => {
      if (record.status === 'Pending') {
        return {
          ...record,
          status: 'Processed',
          paymentDate: new Date().toISOString().split('T')[0]
        }
      }
      return record
    })
    setPayrollRecords(updatedRecords)
    setShowProcessPayroll(false)
    alert(`Successfully processed payroll for ${pendingRecords.length} employees!`)
  }

  const generatePayslip = (employee: any) => {
    setSelectedEmployee(employee)
    setShowPayslip(true)
  }

  const handleCalculatorChange = (field: string, value: string | number) => {
    setCalculatorData(prev => ({
      ...prev,
      [field]: field.includes('Percentage') || field === 'basicSalary' || field === 'professionalTax' || field === 'otherDeductions' 
        ? Number(value) 
        : value
    }))
  }

  const filteredRecords = payrollRecords.filter(record => record.month === selectedMonth)

  const stats = {
    totalEmployees: filteredRecords.length,
    processedEmployees: filteredRecords.filter(r => r.status === 'Processed').length,
    totalPayroll: filteredRecords.reduce((acc, r) => acc + r.netSalary, 0),
    pendingEmployees: filteredRecords.filter(r => r.status === 'Pending').length
  }

  return (
    <div>
      <h2 style={{ fontSize: '28px', fontWeight: 'bold', color: '#111827', marginBottom: '8px' }}>Payroll Management</h2>
      <p style={{ color: '#6b7280', marginBottom: '32px' }}>Process payroll and manage employee compensation</p>
      
      {/* Stats Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#111827', margin: '0' }}>{stats.totalEmployees}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Employees</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981', margin: '0' }}>{stats.processedEmployees}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Processed</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b', margin: '0' }}>{stats.pendingEmployees}</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Pending</p>
        </div>
        <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '12px', border: '1px solid #e5e7eb', textAlign: 'center' }}>
          <p style={{ fontSize: '32px', fontWeight: 'bold', color: '#3b82f6', margin: '0' }}>₹{(stats.totalPayroll / 100000).toFixed(1)}L</p>
          <p style={{ fontSize: '14px', color: '#6b7280', margin: '8px 0 0 0' }}>Total Payroll</p>
        </div>
      </div>

      {/* Month Selection and Actions */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px', alignItems: 'center', flexWrap: 'wrap' }}>
        <select
          value={selectedMonth}
          onChange={(e) => setSelectedMonth(e.target.value)}
          style={{ padding: '8px 12px', border: '1px solid #d1d5db', borderRadius: '6px' }}
        >
          <option value="April 2026">April 2026</option>
          <option value="March 2026">March 2026</option>
          <option value="February 2026">February 2026</option>
          <option value="January 2026">January 2026</option>
        </select>
        <button
          onClick={() => setShowCalculator(true)}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#8b5cf6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Salary Calculator
        </button>
        <button
          onClick={() => setShowProcessPayroll(true)}
          disabled={stats.pendingEmployees === 0}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: stats.pendingEmployees > 0 ? '#10b981' : '#9ca3af', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px',
            cursor: stats.pendingEmployees > 0 ? 'pointer' : 'not-allowed',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Process Payroll ({stats.pendingEmployees} pending)
        </button>
        <button
          onClick={() => alert('Payroll exported successfully!')}
          style={{ 
            padding: '8px 16px', 
            backgroundColor: '#3b82f6', 
            color: 'white', 
            border: 'none', 
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: '500'
          }}
        >
          Export Payroll
        </button>
      </div>

      {/* Salary Calculator Modal */}
      {showCalculator && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          backgroundColor: 'rgba(0, 0, 0, 0.5)', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            width: '90%', 
            maxWidth: '800px',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <div style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
                  Salary Calculator
                </h3>
                <button
                  onClick={() => setShowCalculator(false)}
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
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
                {/* Input Section */}
                <div>
                  <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Salary Structure</h4>
                  <div style={{ display: 'grid', gap: '12px' }}>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>Basic Salary (₹)</label>
                      <input
                        type="number"
                        value={calculatorData.basicSalary}
                        onChange={(e) => handleCalculatorChange('basicSalary', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>HRA Percentage (%)</label>
                      <input
                        type="number"
                        value={calculatorData.hraPercentage}
                        onChange={(e) => handleCalculatorChange('hraPercentage', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>DA Percentage (%)</label>
                      <input
                        type="number"
                        value={calculatorData.daPercentage}
                        onChange={(e) => handleCalculatorChange('daPercentage', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>Allowances Percentage (%)</label>
                      <input
                        type="number"
                        value={calculatorData.allowancesPercentage}
                        onChange={(e) => handleCalculatorChange('allowancesPercentage', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>PF Percentage (%)</label>
                      <input
                        type="number"
                        value={calculatorData.pfPercentage}
                        onChange={(e) => handleCalculatorChange('pfPercentage', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>Professional Tax (₹)</label>
                      <input
                        type="number"
                        value={calculatorData.professionalTax}
                        onChange={(e) => handleCalculatorChange('professionalTax', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>TDS Percentage (%)</label>
                      <input
                        type="number"
                        value={calculatorData.tdsPercentage}
                        onChange={(e) => handleCalculatorChange('tdsPercentage', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ fontSize: '12px', color: '#6b7280', marginBottom: '4px', display: 'block' }}>Other Deductions (₹)</label>
                      <input
                        type="number"
                        value={calculatorData.otherDeductions}
                        onChange={(e) => handleCalculatorChange('otherDeductions', e.target.value)}
                        style={{ 
                          width: '100%',
                          padding: '8px 12px', 
                          border: '1px solid #e5e7eb', 
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                  </div>
                </div>

                {/* Calculation Results */}
                <div>
                  <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', marginBottom: '16px' }}>Calculation Results</h4>
                  
                  <div style={{ marginBottom: '20px' }}>
                    <h5 style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '12px' }}>Earnings</h5>
                    <div style={{ backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>Basic Salary</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.basicSalary.toLocaleString()}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>HRA ({calculatorData.hraPercentage}%)</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.hra.toLocaleString()}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>DA ({calculatorData.daPercentage}%)</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.da.toLocaleString()}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>Allowances ({calculatorData.allowancesPercentage}%)</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.allowances.toLocaleString()}</span>
                      </div>
                      <div style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        paddingTop: '8px', 
                        borderTop: '2px solid #e5e7eb',
                        fontWeight: 'bold'
                      }}>
                        <span style={{ fontSize: '14px' }}>Gross Salary</span>
                        <span style={{ fontSize: '14px' }}>₹{currentCalculation.grossSalary.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ marginBottom: '20px' }}>
                    <h5 style={{ fontSize: '14px', fontWeight: '600', color: '#111827', marginBottom: '12px' }}>Deductions</h5>
                    <div style={{ backgroundColor: '#fef2f2', padding: '16px', borderRadius: '8px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>Provident Fund ({calculatorData.pfPercentage}%)</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.pf.toLocaleString()}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>Professional Tax</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.professionalTax}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>TDS ({calculatorData.tdsPercentage}%)</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.tds.toLocaleString()}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px' }}>Other Deductions</span>
                        <span style={{ fontSize: '14px', fontWeight: '500' }}>₹{currentCalculation.otherDeductions.toLocaleString()}</span>
                      </div>
                      <div style={{ 
                        display: 'flex', 
                        justifyContent: 'space-between', 
                        paddingTop: '8px', 
                        borderTop: '2px solid #fecaca',
                        fontWeight: 'bold'
                      }}>
                        <span style={{ fontSize: '14px' }}>Total Deductions</span>
                        <span style={{ fontSize: '14px' }}>₹{currentCalculation.totalDeductions.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ backgroundColor: '#f0f9ff', padding: '16px', borderRadius: '8px' }}>
                    <div style={{ 
                      display: 'flex', 
                      justifyContent: 'space-between', 
                      fontSize: '18px', 
                      fontWeight: 'bold',
                      color: '#0369a1'
                    }}>
                      <span>Net Salary</span>
                      <span>₹{currentCalculation.netSalary.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                <button
                  onClick={() => alert('Calculation saved successfully!')}
                  style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#10b981', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    flex: 1
                  }}
                >
                  Save Calculation
                </button>
                <button
                  onClick={() => alert('Calculation exported successfully!')}
                  style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#3b82f6', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    flex: 1
                  }}
                >
                  Export Calculation
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Process Payroll Confirmation */}
      {showProcessPayroll && (
        <div style={{ 
          backgroundColor: 'white', 
          padding: '24px', 
          borderRadius: '12px', 
          border: '2px solid #10b981',
          marginBottom: '24px',
          boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)'
        }}>
          <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#111827', marginBottom: '16px' }}>
            Process Payroll Confirmation
          </h3>
          <p style={{ color: '#6b7280', marginBottom: '16px' }}>
            You are about to process payroll for {stats.pendingEmployees} employees for {selectedMonth}. 
            This will calculate salaries and mark payments as processed.
          </p>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={processPayroll}
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
              Confirm Process
            </button>
            <button
              onClick={() => setShowProcessPayroll(false)}
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

      {/* Payroll Table */}
      <div style={{ backgroundColor: 'white', borderRadius: '12px', border: '1px solid #e5e7eb', overflow: 'hidden' }}>
        <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb', backgroundColor: '#f9fafb' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', margin: 0 }}>
            Payroll Records - {selectedMonth}
          </h3>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#f9fafb' }}>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Employee</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Department</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Basic Salary</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Gross Salary</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Deductions</th>
              <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Net Salary</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Status</th>
              <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '14px', fontWeight: '600', color: '#6b7280' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.map((record) => (
              <tr key={record.id} style={{ borderBottom: '1px solid #f3f4f6' }}>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: '500' }}>
                  {record.employee}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827' }}>
                  {record.department}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right' }}>
                  ₹{record.basicSalary.toLocaleString()}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right' }}>
                  ₹{record.grossSalary.toLocaleString()}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', textAlign: 'right' }}>
                  ₹{record.totalDeductions.toLocaleString()}
                </td>
                <td style={{ padding: '12px 16px', fontSize: '14px', color: '#111827', fontWeight: 'bold', textAlign: 'right' }}>
                  ₹{record.netSalary.toLocaleString()}
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <span style={{ 
                    padding: '4px 8px', 
                    borderRadius: '4px', 
                    fontSize: '12px',
                    fontWeight: '500',
                    backgroundColor: statusColors[record.status as keyof typeof statusColors],
                    color: statusTextColors[record.status as keyof typeof statusTextColors]
                  }}>
                    {record.status}
                  </span>
                </td>
                <td style={{ padding: '12px 16px' }}>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      onClick={() => generatePayslip(record)}
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
                      Payslip
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

      {/* Payslip Modal */}
      {showPayslip && selectedEmployee && (
        <div style={{ 
          position: 'fixed', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          backgroundColor: 'rgba(0, 0, 0, 0.5)', 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{ 
            backgroundColor: 'white', 
            borderRadius: '12px', 
            width: '90%', 
            maxWidth: '600px',
            maxHeight: '90vh',
            overflow: 'auto'
          }}>
            <div style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h3 style={{ fontSize: '20px', fontWeight: 'bold', color: '#111827', margin: 0 }}>
                  Payslip - {selectedEmployee.month}
                </h3>
                <button
                  onClick={() => setShowPayslip(false)}
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
              
              <div style={{ marginBottom: '24px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                  <div>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 4px 0' }}>Employee Name</p>
                    <p style={{ fontSize: '16px', fontWeight: '500', margin: '0' }}>{selectedEmployee.employee}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 4px 0' }}>Department</p>
                    <p style={{ fontSize: '16px', fontWeight: '500', margin: '0' }}>{selectedEmployee.department}</p>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                  <div>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 4px 0' }}>Month</p>
                    <p style={{ fontSize: '16px', fontWeight: '500', margin: '0' }}>{selectedEmployee.month}</p>
                  </div>
                  <div>
                    <p style={{ fontSize: '12px', color: '#6b7280', margin: '0 0 4px 0' }}>Payment Date</p>
                    <p style={{ fontSize: '16px', fontWeight: '500', margin: '0' }}>
                      {selectedEmployee.paymentDate || 'Pending'}
                    </p>
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', marginBottom: '12px' }}>Earnings</h4>
                <div style={{ backgroundColor: '#f9fafb', padding: '16px', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Basic Salary</span>
                    <span>₹{selectedEmployee.basicSalary.toLocaleString()}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>HRA (30%)</span>
                    <span>₹{selectedEmployee.hra.toLocaleString()}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>DA (10%)</span>
                    <span>₹{selectedEmployee.da.toLocaleString()}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Allowances (15%)</span>
                    <span>₹{selectedEmployee.allowances.toLocaleString()}</span>
                  </div>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    paddingTop: '8px', 
                    borderTop: '2px solid #e5e7eb',
                    fontWeight: 'bold'
                  }}>
                    <span>Gross Salary</span>
                    <span>₹{selectedEmployee.grossSalary.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ fontSize: '16px', fontWeight: '600', color: '#111827', marginBottom: '12px' }}>Deductions</h4>
                <div style={{ backgroundColor: '#fef2f2', padding: '16px', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Provident Fund (12%)</span>
                    <span>₹{selectedEmployee.pf.toLocaleString()}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Professional Tax</span>
                    <span>₹{selectedEmployee.professionalTax}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>TDS (10%)</span>
                    <span>₹{selectedEmployee.tds.toLocaleString()}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Other Deductions</span>
                    <span>₹{selectedEmployee.otherDeductions.toLocaleString()}</span>
                  </div>
                  <div style={{ 
                    display: 'flex', 
                    justifyContent: 'space-between', 
                    paddingTop: '8px', 
                    borderTop: '2px solid #fecaca',
                    fontWeight: 'bold'
                  }}>
                    <span>Total Deductions</span>
                    <span>₹{selectedEmployee.totalDeductions.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div style={{ backgroundColor: '#f0f9ff', padding: '16px', borderRadius: '8px' }}>
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'space-between', 
                  fontSize: '18px', 
                  fontWeight: 'bold',
                  color: '#0369a1'
                }}>
                  <span>Net Salary</span>
                  <span>₹{selectedEmployee.netSalary.toLocaleString()}</span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
                <button
                  onClick={() => alert('Payslip downloaded successfully!')}
                  style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#3b82f6', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    flex: 1
                  }}
                >
                  Download PDF
                </button>
                <button
                  onClick={() => alert('Payslip emailed successfully!')}
                  style={{ 
                    padding: '8px 16px', 
                    backgroundColor: '#10b981', 
                    color: 'white', 
                    border: 'none', 
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                    flex: 1
                  }}
                >
                  Email Payslip
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Payroll
