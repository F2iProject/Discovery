import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { PageHeader } from '@/components/PageHeader'
import { DataTable, type Column } from '@/components/DataTable'
import { EmptyState } from '@/components/EmptyState'
import { StatusBadge } from '@/components/StatusBadge'
import { formatDate } from '@/lib/utils'

// Module configurations — defines columns and create payloads for each module
const moduleConfigs: Record<string, ModuleConfig> = {
  documents: {
    title: 'Documents',
    singular: 'Document',
    apiPath: '/documents',
    columns: [
      { key: 'doc_number', label: 'Number' },
      { key: 'title', label: 'Title' },
      { key: 'doc_type', label: 'Type', type: 'status' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'current_version', label: 'Version', type: 'number' },
      { key: 'created_at', label: 'Created', type: 'date' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'doc_type', label: 'Type', type: 'select', options: ['sop', 'protocol', 'method', 'form', 'policy', 'other'] },
      { name: 'description', label: 'Description', type: 'textarea' },
    ],
  },
  'change-controls': {
    title: 'Change Controls',
    singular: 'Change Control',
    apiPath: '/change-controls',
    columns: [
      { key: 'change_number', label: 'Number' },
      { key: 'title', label: 'Title' },
      { key: 'change_type', label: 'Type', type: 'status' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'created_at', label: 'Created', type: 'date' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'change_type', label: 'Type', type: 'select', options: ['process', 'document', 'equipment', 'material', 'other'] },
      { name: 'description', label: 'Description', type: 'textarea' },
      { name: 'justification', label: 'Justification', type: 'textarea' },
    ],
  },
  capas: {
    title: 'CAPAs',
    singular: 'CAPA',
    apiPath: '/capas',
    columns: [
      { key: 'capa_number', label: 'Number' },
      { key: 'title', label: 'Title' },
      { key: 'capa_type', label: 'Type', type: 'status' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'priority', label: 'Priority', type: 'status' },
      { key: 'target_date', label: 'Target', type: 'date' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'capa_type', label: 'Type', type: 'select', options: ['corrective', 'preventive'] },
      { name: 'priority', label: 'Priority', type: 'select', options: ['low', 'medium', 'high', 'critical'] },
      { name: 'description', label: 'Description', type: 'textarea' },
      { name: 'target_date', label: 'Target Date', type: 'date' },
    ],
  },
  risks: {
    title: 'Risks',
    singular: 'Risk',
    apiPath: '/risks',
    columns: [
      { key: 'risk_number', label: 'Number' },
      { key: 'title', label: 'Title' },
      { key: 'category', label: 'Category' },
      { key: 'severity', label: 'Severity', type: 'number' },
      { key: 'likelihood', label: 'Likelihood', type: 'number' },
      { key: 'risk_level', label: 'Level', type: 'status' },
      { key: 'status', label: 'Status', type: 'status' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'category', label: 'Category', type: 'text' },
      { name: 'severity', label: 'Severity (1-5)', type: 'number' },
      { name: 'likelihood', label: 'Likelihood (1-5)', type: 'number' },
      { name: 'description', label: 'Description', type: 'textarea' },
    ],
  },
  trainings: {
    title: 'Training',
    singular: 'Training',
    apiPath: '/trainings',
    columns: [
      { key: 'title', label: 'Title' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'created_at', label: 'Created', type: 'date' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'description', label: 'Description', type: 'textarea' },
    ],
  },
  nonconformances: {
    title: 'Non-Conformances',
    singular: 'Non-Conformance',
    apiPath: '/nonconformances',
    columns: [
      { key: 'nc_number', label: 'Number' },
      { key: 'title', label: 'Title' },
      { key: 'severity', label: 'Severity', type: 'status' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'disposition', label: 'Disposition', type: 'status' },
      { key: 'created_at', label: 'Created', type: 'date' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'severity', label: 'Severity', type: 'select', options: ['minor', 'major', 'critical'] },
      { name: 'category', label: 'Category', type: 'text' },
      { name: 'description', label: 'Description', type: 'textarea' },
    ],
  },
  deviations: {
    title: 'Deviations',
    singular: 'Deviation',
    apiPath: '/deviations',
    columns: [
      { key: 'deviation_number', label: 'Number' },
      { key: 'title', label: 'Title' },
      { key: 'deviation_type', label: 'Type', type: 'status' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'created_at', label: 'Created', type: 'date' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'deviation_type', label: 'Type', type: 'select', options: ['planned', 'unplanned'] },
      { name: 'description', label: 'Description', type: 'textarea' },
      { name: 'justification', label: 'Justification', type: 'textarea' },
    ],
  },
  equipment: {
    title: 'Equipment',
    singular: 'Equipment',
    apiPath: '/equipment',
    columns: [
      { key: 'equipment_id', label: 'ID' },
      { key: 'name', label: 'Name' },
      { key: 'category', label: 'Category' },
      { key: 'manufacturer', label: 'Manufacturer' },
      { key: 'location', label: 'Location' },
      { key: 'status', label: 'Status', type: 'status' },
    ],
    createFields: [
      { name: 'name', label: 'Name', type: 'text', required: true },
      { name: 'category', label: 'Category', type: 'text' },
      { name: 'manufacturer', label: 'Manufacturer', type: 'text' },
      { name: 'model', label: 'Model', type: 'text' },
      { name: 'serial_number', label: 'Serial Number', type: 'text' },
      { name: 'location', label: 'Location', type: 'text' },
    ],
  },
  calibrations: {
    title: 'Calibrations',
    singular: 'Calibration',
    apiPath: '/calibrations',
    columns: [
      { key: 'equipment_id', label: 'Equipment' },
      { key: 'calibration_date', label: 'Date', type: 'date' },
      { key: 'next_due', label: 'Next Due', type: 'date' },
      { key: 'result', label: 'Result', type: 'status' },
      { key: 'method', label: 'Method' },
    ],
    createFields: [
      { name: 'equipment_id', label: 'Equipment ID', type: 'text', required: true },
      { name: 'calibration_date', label: 'Calibration Date', type: 'date', required: true },
      { name: 'next_due', label: 'Next Due', type: 'date' },
      { name: 'result', label: 'Result', type: 'select', options: ['pass', 'fail', 'adjusted'] },
      { name: 'method', label: 'Method', type: 'text' },
      { name: 'certificate_ref', label: 'Certificate Reference', type: 'text' },
      { name: 'notes', label: 'Notes', type: 'textarea' },
    ],
  },
  complaints: {
    title: 'Complaints',
    singular: 'Complaint',
    apiPath: '/complaints',
    columns: [
      { key: 'complaint_number', label: 'Number' },
      { key: 'title', label: 'Title' },
      { key: 'source', label: 'Source' },
      { key: 'product', label: 'Product' },
      { key: 'status', label: 'Status', type: 'status' },
      { key: 'created_at', label: 'Created', type: 'date' },
    ],
    createFields: [
      { name: 'title', label: 'Title', type: 'text', required: true },
      { name: 'source', label: 'Source', type: 'text' },
      { name: 'product', label: 'Product', type: 'text' },
      { name: 'lot_number', label: 'Lot Number', type: 'text' },
      { name: 'description', label: 'Description', type: 'textarea' },
    ],
  },
  suppliers: {
    title: 'Suppliers',
    singular: 'Supplier',
    apiPath: '/suppliers',
    columns: [
      { key: 'name', label: 'Name' },
      { key: 'contact_name', label: 'Contact' },
      { key: 'contact_email', label: 'Email' },
      { key: 'supplies', label: 'Supplies' },
      { key: 'qualification_status', label: 'Status', type: 'status' },
    ],
    createFields: [
      { name: 'name', label: 'Company Name', type: 'text', required: true },
      { name: 'contact_name', label: 'Contact Name', type: 'text' },
      { name: 'contact_email', label: 'Contact Email', type: 'text' },
      { name: 'contact_phone', label: 'Phone', type: 'text' },
      { name: 'website', label: 'Website', type: 'text' },
      { name: 'supplies', label: 'What they supply', type: 'text' },
    ],
  },
}

interface CreateField {
  name: string
  label: string
  type: 'text' | 'textarea' | 'select' | 'number' | 'date'
  required?: boolean
  options?: string[]
}

interface ModuleConfig {
  title: string
  singular: string
  apiPath: string
  columns: Column<Record<string, unknown>>[]
  createFields: CreateField[]
}

export function ModuleListPage({ module }: { module: string }) {
  const config = moduleConfigs[module]
  const navigate = useNavigate()
  const [items, setItems] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    api.get<Record<string, unknown>[]>(config.apiPath)
      .then(setItems)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [config.apiPath])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setCreating(true)
    setError('')
    try {
      // Convert number fields
      const payload: Record<string, unknown> = { ...formData }
      config.createFields.forEach((f) => {
        if (f.type === 'number' && payload[f.name]) {
          payload[f.name] = Number(payload[f.name])
        }
      })
      const newItem = await api.post<Record<string, unknown>>(config.apiPath, payload)
      setItems((prev) => [newItem, ...prev])
      setShowCreate(false)
      setFormData({})
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create')
    } finally {
      setCreating(false)
    }
  }

  if (!config) return <div className="text-red-400">Unknown module: {module}</div>

  return (
    <div>
      <PageHeader
        title={config.title}
        subtitle={`${items.length} ${items.length === 1 ? 'record' : 'records'}`}
        action={{ label: `New ${config.singular}`, onClick: () => setShowCreate(true) }}
      />

      {/* Create modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="fixed inset-0 bg-black/60" onClick={() => setShowCreate(false)} />
          <div className="relative bg-navy-900 border border-navy-700 rounded-xl p-6 w-full max-w-lg shadow-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-lg font-semibold text-gray-100 mb-4">
              New {config.singular}
            </h2>
            {error && (
              <div className="bg-red-500/10 border border-red-500/30 rounded-lg px-4 py-3 mb-4">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}
            <form onSubmit={handleCreate} className="space-y-4">
              {config.createFields.map((field) => (
                <div key={field.name}>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">
                    {field.label}
                    {field.required && <span className="text-red-400 ml-1">*</span>}
                  </label>
                  {field.type === 'textarea' ? (
                    <textarea
                      value={formData[field.name] || ''}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                      className="input-field min-h-[80px] resize-y"
                      required={field.required}
                    />
                  ) : field.type === 'select' ? (
                    <select
                      value={formData[field.name] || field.options?.[0] || ''}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                      className="input-field"
                    >
                      {field.options?.map((opt) => (
                        <option key={opt} value={opt}>
                          {opt.replace(/_/g, ' ')}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'}
                      value={formData[field.name] || ''}
                      onChange={(e) => setFormData({ ...formData, [field.name]: e.target.value })}
                      className="input-field"
                      required={field.required}
                      min={field.type === 'number' ? 1 : undefined}
                      max={field.type === 'number' ? 5 : undefined}
                    />
                  )}
                </div>
              ))}
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowCreate(false)} className="btn-secondary">
                  Cancel
                </button>
                <button type="submit" disabled={creating} className="btn-primary">
                  {creating ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {!loading && items.length === 0 ? (
        <EmptyState
          title={`No ${config.title.toLowerCase()} yet`}
          description={`Create your first ${config.singular.toLowerCase()} to get started.`}
          action={{ label: `New ${config.singular}`, onClick: () => setShowCreate(true) }}
        />
      ) : (
        <DataTable
          columns={config.columns}
          data={items as (Record<string, unknown> & { id: string })[]}
          onRowClick={(item) => navigate(`/${module}/${item.id}`)}
          loading={loading}
        />
      )}
    </div>
  )
}
