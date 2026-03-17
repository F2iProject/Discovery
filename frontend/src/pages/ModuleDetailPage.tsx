import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { PageHeader } from '@/components/PageHeader'
import { StatusBadge } from '@/components/StatusBadge'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { formatDateTime } from '@/lib/utils'

const moduleMetadata: Record<string, { title: string; apiPath: string; listPath: string; fields: FieldDef[] }> = {
  documents: {
    title: 'Document',
    apiPath: '/documents',
    listPath: '/documents',
    fields: [
      { key: 'doc_number', label: 'Number', readOnly: true },
      { key: 'title', label: 'Title', editable: true },
      { key: 'doc_type', label: 'Type', editable: true, type: 'select', options: ['sop', 'protocol', 'method', 'form', 'policy', 'other'] },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['draft', 'in_review', 'approved', 'archived'] },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'current_version', label: 'Version', readOnly: true },
    ],
  },
  'change-controls': {
    title: 'Change Control',
    apiPath: '/change-controls',
    listPath: '/change-controls',
    fields: [
      { key: 'change_number', label: 'Number', readOnly: true },
      { key: 'title', label: 'Title', editable: true },
      { key: 'change_type', label: 'Type', editable: true, type: 'select', options: ['process', 'document', 'equipment', 'material', 'other'] },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['draft', 'submitted', 'under_review', 'approved', 'rejected', 'closed'] },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'justification', label: 'Justification', editable: true, type: 'textarea' },
      { key: 'impact_assessment', label: 'Impact Assessment', editable: true, type: 'textarea' },
    ],
  },
  capas: {
    title: 'CAPA',
    apiPath: '/capas',
    listPath: '/capas',
    fields: [
      { key: 'capa_number', label: 'Number', readOnly: true },
      { key: 'title', label: 'Title', editable: true },
      { key: 'capa_type', label: 'Type', editable: true, type: 'select', options: ['corrective', 'preventive'] },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['open', 'investigation', 'action_defined', 'implemented', 'closed'] },
      { key: 'priority', label: 'Priority', editable: true, type: 'select', options: ['low', 'medium', 'high', 'critical'] },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'root_cause', label: 'Root Cause', editable: true, type: 'textarea' },
      { key: 'source', label: 'Source', editable: true },
      { key: 'target_date', label: 'Target Date', editable: true, type: 'date' },
    ],
  },
  risks: {
    title: 'Risk',
    apiPath: '/risks',
    listPath: '/risks',
    fields: [
      { key: 'risk_number', label: 'Number', readOnly: true },
      { key: 'title', label: 'Title', editable: true },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['draft', 'active', 'mitigated', 'closed'] },
      { key: 'category', label: 'Category', editable: true },
      { key: 'severity', label: 'Severity (1-5)', editable: true, type: 'number' },
      { key: 'likelihood', label: 'Likelihood (1-5)', editable: true, type: 'number' },
      { key: 'risk_level', label: 'Risk Level', readOnly: true, type: 'status' },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'mitigation', label: 'Mitigation', editable: true, type: 'textarea' },
    ],
  },
  trainings: {
    title: 'Training',
    apiPath: '/trainings',
    listPath: '/trainings',
    fields: [
      { key: 'title', label: 'Title', editable: true },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['draft', 'active', 'retired'] },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
    ],
  },
  nonconformances: {
    title: 'Non-Conformance',
    apiPath: '/nonconformances',
    listPath: '/nonconformances',
    fields: [
      { key: 'nc_number', label: 'Number', readOnly: true },
      { key: 'title', label: 'Title', editable: true },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['open', 'under_review', 'dispositioned', 'closed'] },
      { key: 'severity', label: 'Severity', editable: true, type: 'select', options: ['minor', 'major', 'critical'] },
      { key: 'category', label: 'Category', editable: true },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'disposition', label: 'Disposition', editable: true, type: 'select', options: ['use_as_is', 'rework', 'scrap', 'return_to_supplier', 'other'] },
      { key: 'disposition_rationale', label: 'Disposition Rationale', editable: true, type: 'textarea' },
    ],
  },
  deviations: {
    title: 'Deviation',
    apiPath: '/deviations',
    listPath: '/deviations',
    fields: [
      { key: 'deviation_number', label: 'Number', readOnly: true },
      { key: 'title', label: 'Title', editable: true },
      { key: 'deviation_type', label: 'Type', editable: true, type: 'select', options: ['planned', 'unplanned'] },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['open', 'under_review', 'approved', 'rejected', 'closed'] },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'justification', label: 'Justification', editable: true, type: 'textarea' },
      { key: 'resolution', label: 'Resolution', editable: true, type: 'textarea' },
    ],
  },
  equipment: {
    title: 'Equipment',
    apiPath: '/equipment',
    listPath: '/equipment',
    fields: [
      { key: 'equipment_id', label: 'Equipment ID', readOnly: true },
      { key: 'name', label: 'Name', editable: true },
      { key: 'category', label: 'Category', editable: true },
      { key: 'manufacturer', label: 'Manufacturer', editable: true },
      { key: 'model', label: 'Model', editable: true },
      { key: 'serial_number', label: 'Serial Number', editable: true },
      { key: 'location', label: 'Location', editable: true },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['active', 'maintenance', 'retired', 'out_of_service'] },
      { key: 'notes', label: 'Notes', editable: true, type: 'textarea' },
    ],
  },
  calibrations: {
    title: 'Calibration',
    apiPath: '/calibrations',
    listPath: '/calibrations',
    fields: [
      { key: 'equipment_id', label: 'Equipment ID', readOnly: true },
      { key: 'calibration_date', label: 'Calibration Date', editable: true, type: 'date' },
      { key: 'next_due', label: 'Next Due', editable: true, type: 'date' },
      { key: 'interval_days', label: 'Interval (days)', editable: true, type: 'number' },
      { key: 'result', label: 'Result', editable: true, type: 'select', options: ['pass', 'fail', 'adjusted'] },
      { key: 'method', label: 'Method', editable: true },
      { key: 'certificate_ref', label: 'Certificate Ref', editable: true },
      { key: 'notes', label: 'Notes', editable: true, type: 'textarea' },
    ],
  },
  complaints: {
    title: 'Complaint',
    apiPath: '/complaints',
    listPath: '/complaints',
    fields: [
      { key: 'complaint_number', label: 'Number', readOnly: true },
      { key: 'title', label: 'Title', editable: true },
      { key: 'status', label: 'Status', editable: true, type: 'select', options: ['open', 'under_review', 'closed'] },
      { key: 'source', label: 'Source', editable: true },
      { key: 'product', label: 'Product', editable: true },
      { key: 'lot_number', label: 'Lot Number', editable: true },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'investigation_notes', label: 'Investigation Notes', editable: true, type: 'textarea' },
    ],
  },
  suppliers: {
    title: 'Supplier',
    apiPath: '/suppliers',
    listPath: '/suppliers',
    fields: [
      { key: 'name', label: 'Name', editable: true },
      { key: 'contact_name', label: 'Contact', editable: true },
      { key: 'contact_email', label: 'Email', editable: true },
      { key: 'contact_phone', label: 'Phone', editable: true },
      { key: 'website', label: 'Website', editable: true },
      { key: 'supplies', label: 'Supplies', editable: true },
      { key: 'qualification_status', label: 'Status', editable: true, type: 'select', options: ['pending', 'approved', 'conditional', 'disqualified'] },
      { key: 'notes', label: 'Notes', editable: true, type: 'textarea' },
    ],
  },
}

interface FieldDef {
  key: string
  label: string
  readOnly?: boolean
  editable?: boolean
  type?: 'text' | 'textarea' | 'select' | 'number' | 'date' | 'status'
  options?: string[]
}

export function ModuleDetailPage({ module }: { module: string }) {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const meta = moduleMetadata[module]
  const [item, setItem] = useState<Record<string, unknown> | null>(null)
  const [editing, setEditing] = useState(false)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [saving, setSaving] = useState(false)
  const [showDelete, setShowDelete] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get<Record<string, unknown>>(`${meta.apiPath}/${id}`)
      .then((data) => {
        setItem(data)
        const fd: Record<string, string> = {}
        meta.fields.forEach((f) => {
          fd[f.key] = data[f.key] != null ? String(data[f.key]) : ''
        })
        setFormData(fd)
      })
      .catch(() => navigate(meta.listPath))
      .finally(() => setLoading(false))
  }, [id, meta.apiPath])

  const handleSave = async () => {
    setSaving(true)
    try {
      const payload: Record<string, unknown> = {}
      meta.fields.forEach((f) => {
        if (f.editable && formData[f.key] !== String(item?.[f.key] ?? '')) {
          const val = formData[f.key]
          if (f.type === 'number') {
            payload[f.key] = val ? Number(val) : null
          } else {
            payload[f.key] = val || null
          }
        }
      })
      if (Object.keys(payload).length > 0) {
        const updated = await api.patch<Record<string, unknown>>(`${meta.apiPath}/${id}`, payload)
        setItem(updated)
      }
      setEditing(false)
    } catch (err) {
      console.error(err)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    await api.delete(`${meta.apiPath}/${id}`)
    navigate(meta.listPath)
  }

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 w-48 bg-navy-800 rounded" />
        <div className="card space-y-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="h-10 bg-navy-800 rounded" />
          ))}
        </div>
      </div>
    )
  }

  if (!item) return null

  return (
    <div>
      <PageHeader
        title={String(item.title || item.name || `${meta.title} Detail`)}
        subtitle={String(item[meta.fields[0]?.key] || '')}
        backTo={meta.listPath}
      />

      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-200">Details</h2>
          <div className="flex gap-2">
            {editing ? (
              <>
                <button onClick={() => setEditing(false)} className="btn-secondary">
                  Cancel
                </button>
                <button onClick={handleSave} disabled={saving} className="btn-primary">
                  {saving ? 'Saving...' : 'Save'}
                </button>
              </>
            ) : (
              <>
                <button onClick={() => setEditing(true)} className="btn-secondary">
                  Edit
                </button>
                <button onClick={() => setShowDelete(true)} className="btn-danger">
                  Delete
                </button>
              </>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {meta.fields.map((field) => (
            <div key={field.key} className={field.type === 'textarea' ? 'md:col-span-2' : ''}>
              <label className="block text-sm font-medium text-gray-500 mb-1">
                {field.label}
              </label>
              {editing && field.editable ? (
                field.type === 'textarea' ? (
                  <textarea
                    value={formData[field.key] || ''}
                    onChange={(e) => setFormData({ ...formData, [field.key]: e.target.value })}
                    className="input-field min-h-[80px] resize-y"
                  />
                ) : field.type === 'select' ? (
                  <select
                    value={formData[field.key] || ''}
                    onChange={(e) => setFormData({ ...formData, [field.key]: e.target.value })}
                    className="input-field"
                  >
                    <option value="">—</option>
                    {field.options?.map((opt) => (
                      <option key={opt} value={opt}>
                        {opt.replace(/_/g, ' ')}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={field.type === 'number' ? 'number' : field.type === 'date' ? 'date' : 'text'}
                    value={formData[field.key] || ''}
                    onChange={(e) => setFormData({ ...formData, [field.key]: e.target.value })}
                    className="input-field"
                  />
                )
              ) : field.type === 'status' ? (
                <StatusBadge status={String(item[field.key] || '')} />
              ) : (
                <p className="text-gray-200">
                  {item[field.key] != null ? String(item[field.key]) : '—'}
                </p>
              )}
            </div>
          ))}
        </div>

        {/* Metadata footer */}
        <div className="mt-8 pt-6 border-t border-navy-800 flex gap-8 text-xs text-gray-500">
          <span>Created: {formatDateTime(String(item.created_at))}</span>
          {item.updated_at ? <span>Updated: {formatDateTime(String(item.updated_at))}</span> : null}
          <span className="font-mono">{String(item.id)}</span>
        </div>
      </div>

      <ConfirmDialog
        open={showDelete}
        onClose={() => setShowDelete(false)}
        onConfirm={handleDelete}
        title={`Delete ${meta.title}`}
        message={`Are you sure you want to delete this ${meta.title.toLowerCase()}? This action cannot be undone.`}
        confirmLabel="Delete"
        danger
      />
    </div>
  )
}
