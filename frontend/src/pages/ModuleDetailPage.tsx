import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { PageHeader } from '@/components/PageHeader'
import { StatusBadge } from '@/components/StatusBadge'
import { ConfirmDialog } from '@/components/ConfirmDialog'
import { formatDateTime } from '@/lib/utils'
import type { DocumentVersion, DocumentAttachment, EquipmentPhoto, SupplierDocument, TrainingMaterial } from '@/types'

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
      { key: 'url', label: 'Link / URL', editable: true },
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
      { key: 'mpn', label: 'MPN', editable: true },
      { key: 'description', label: 'Description', editable: true, type: 'textarea' },
      { key: 'contact_name', label: 'Contact Name', editable: true },
      { key: 'contact_email', label: 'Contact Email', editable: true },
      { key: 'contact_phone', label: 'Contact Phone', editable: true },
      { key: 'phone', label: 'Phone Number', editable: true },
      { key: 'address', label: 'Address', editable: true, type: 'textarea' },
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

// File icon based on extension
function fileIcon(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase() || ''
  if (['pdf'].includes(ext)) return '📄'
  if (['doc', 'docx', 'odt', 'rtf'].includes(ext)) return '📝'
  if (['xls', 'xlsx', 'csv', 'ods'].includes(ext)) return '📊'
  if (['ppt', 'pptx', 'odp'].includes(ext)) return '📑'
  if (['png', 'jpg', 'jpeg', 'gif', 'svg'].includes(ext)) return '🖼️'
  if (['zip', 'tar', 'gz'].includes(ext)) return '📦'
  return '📎'
}

// Image component that loads via fetch with auth header
function AuthImage({ src, alt, className }: { src: string; alt: string; className?: string }) {
  const [blobUrl, setBlobUrl] = useState<string | null>(null)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('discovery_token')
    fetch(src, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        if (!res.ok) throw new Error('Failed to load')
        return res.blob()
      })
      .then((blob) => setBlobUrl(URL.createObjectURL(blob)))
      .catch(() => setFailed(true))
    return () => { if (blobUrl) URL.revokeObjectURL(blobUrl) }
  }, [src])

  if (failed) return <span className="text-4xl">🖼️</span>
  if (!blobUrl) return <span className="text-gray-600 text-sm">Loading...</span>
  return <img src={blobUrl} alt={alt} className={className} />
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
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

  // Document file upload state
  const [versions, setVersions] = useState<DocumentVersion[]>([])
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const [changeSummary, setChangeSummary] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const attachmentInputRef = useRef<HTMLInputElement>(null)
  const photoInputRef = useRef<HTMLInputElement>(null)
  const vendorDocInputRef = useRef<HTMLInputElement>(null)
  const isDocuments = module === 'documents'
  const isEquipment = module === 'equipment'
  const isSuppliers = module === 'suppliers'
  const isTrainings = module === 'trainings'

  // Attachment state (documents module)
  const [attachments, setAttachments] = useState<DocumentAttachment[]>([])
  const [attachUploading, setAttachUploading] = useState(false)
  const [attachError, setAttachError] = useState('')
  const [attachDragOver, setAttachDragOver] = useState(false)
  const [attachDescription, setAttachDescription] = useState('')

  // Equipment photo state
  const [photos, setPhotos] = useState<EquipmentPhoto[]>([])
  const [photoUploading, setPhotoUploading] = useState(false)
  const [photoError, setPhotoError] = useState('')
  const [photoDragOver, setPhotoDragOver] = useState(false)
  const [photoDescription, setPhotoDescription] = useState('')

  // Supplier document state
  const [vendorDocs, setVendorDocs] = useState<SupplierDocument[]>([])
  const [vendorDocUploading, setVendorDocUploading] = useState(false)
  const [vendorDocError, setVendorDocError] = useState('')
  const [vendorDocDragOver, setVendorDocDragOver] = useState(false)
  const [vendorDocDescription, setVendorDocDescription] = useState('')

  // Training material state
  const materialInputRef = useRef<HTMLInputElement>(null)
  const [materials, setMaterials] = useState<TrainingMaterial[]>([])
  const [materialUploading, setMaterialUploading] = useState(false)
  const [materialError, setMaterialError] = useState('')
  const [materialDragOver, setMaterialDragOver] = useState(false)
  const [materialDescription, setMaterialDescription] = useState('')

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

  // Load versions and attachments for documents
  useEffect(() => {
    if (isDocuments && id) {
      api.get<DocumentVersion[]>(`/documents/${id}/versions`)
        .then(setVersions)
        .catch(() => setVersions([]))
      api.get<DocumentAttachment[]>(`/documents/${id}/attachments`)
        .then(setAttachments)
        .catch(() => setAttachments([]))
    }
  }, [isDocuments, id])

  // Load photos for equipment
  useEffect(() => {
    if (isEquipment && id) {
      api.get<EquipmentPhoto[]>(`/equipment/${id}/photos`)
        .then(setPhotos)
        .catch(() => setPhotos([]))
    }
  }, [isEquipment, id])

  // Load documents for suppliers
  useEffect(() => {
    if (isSuppliers && id) {
      api.get<SupplierDocument[]>(`/suppliers/${id}/documents`)
        .then(setVendorDocs)
        .catch(() => setVendorDocs([]))
    }
  }, [isSuppliers, id])

  // Load materials for trainings
  useEffect(() => {
    if (isTrainings && id) {
      api.get<TrainingMaterial[]>(`/trainings/${id}/materials`)
        .then(setMaterials)
        .catch(() => setMaterials([]))
    }
  }, [isTrainings, id])

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
        // Update formData to match new state
        const fd: Record<string, string> = {}
        meta.fields.forEach((f) => {
          fd[f.key] = updated[f.key] != null ? String(updated[f.key]) : ''
        })
        setFormData(fd)
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

  const handleFileUpload = useCallback(async (file: File) => {
    if (!id) return
    setUploading(true)
    setUploadError('')
    try {
      const newVersion = await api.upload<DocumentVersion>(
        `/documents/${id}/upload`,
        file,
        changeSummary ? { change_summary: changeSummary } : undefined
      )
      setVersions((prev) => [...prev, newVersion])
      // Update the item's current_version
      setItem((prev) => prev ? { ...prev, current_version: newVersion.version_number } : prev)
      setChangeSummary('')
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (err) {
      setUploadError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setUploading(false)
    }
  }, [id, changeSummary])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFileUpload(file)
  }, [handleFileUpload])

  const handleDeleteVersion = async (version: DocumentVersion) => {
    if (!confirm(`Delete ${version.filename || 'this version'}?`)) return
    try {
      await api.delete(`/documents/${id}/versions/${version.id}`)
      setVersions((prev) => prev.filter((v) => v.id !== version.id))
      // Update current_version
      const remaining = versions.filter((v) => v.id !== version.id)
      const maxVersion = remaining.length > 0
        ? Math.max(...remaining.map((v) => v.version_number))
        : 0
      setItem((prev) => prev ? { ...prev, current_version: maxVersion } : prev)
    } catch (err) {
      console.error('Failed to delete version:', err)
    }
  }

  // --- Attachment handlers ---
  const handleAttachmentUpload = useCallback(async (file: File) => {
    if (!id) return
    setAttachUploading(true)
    setAttachError('')
    try {
      const newAttachment = await api.upload<DocumentAttachment>(
        `/documents/${id}/attachments`,
        file,
        attachDescription ? { description: attachDescription } : undefined
      )
      setAttachments((prev) => [...prev, newAttachment])
      setAttachDescription('')
      if (attachmentInputRef.current) attachmentInputRef.current.value = ''
    } catch (err) {
      setAttachError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setAttachUploading(false)
    }
  }, [id, attachDescription])

  const handleAttachmentDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setAttachDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleAttachmentUpload(file)
  }, [handleAttachmentUpload])

  const handleDeleteAttachment = async (att: DocumentAttachment) => {
    if (!confirm(`Delete "${att.filename}"?`)) return
    try {
      await api.delete(`/documents/${id}/attachments/${att.id}`)
      setAttachments((prev) => prev.filter((a) => a.id !== att.id))
    } catch (err) {
      console.error('Failed to delete attachment:', err)
    }
  }

  // --- Equipment photo handlers ---
  const handlePhotoUpload = useCallback(async (file: File) => {
    if (!id) return
    setPhotoUploading(true)
    setPhotoError('')
    try {
      const newPhoto = await api.upload<EquipmentPhoto>(
        `/equipment/${id}/photos`,
        file,
        photoDescription ? { description: photoDescription } : undefined
      )
      setPhotos((prev) => [...prev, newPhoto])
      setPhotoDescription('')
      if (photoInputRef.current) photoInputRef.current.value = ''
    } catch (err) {
      setPhotoError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setPhotoUploading(false)
    }
  }, [id, photoDescription])

  const handlePhotoDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setPhotoDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handlePhotoUpload(file)
  }, [handlePhotoUpload])

  const handleDeletePhoto = async (photo: EquipmentPhoto) => {
    if (!confirm(`Delete "${photo.filename}"?`)) return
    try {
      await api.delete(`/equipment/${id}/photos/${photo.id}`)
      setPhotos((prev) => prev.filter((p) => p.id !== photo.id))
    } catch (err) {
      console.error('Failed to delete photo:', err)
    }
  }

  const handleDownloadPhoto = (photo: EquipmentPhoto) => {
    const token = localStorage.getItem('discovery_token')
    const url = `/api/equipment/${id}/photos/${photo.id}/download`
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.blob())
      .then((blob) => {
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = photo.filename
        a.click()
        URL.revokeObjectURL(a.href)
      })
  }

  // --- Supplier document handlers ---
  const handleVendorDocUpload = useCallback(async (file: File) => {
    if (!id) return
    setVendorDocUploading(true)
    setVendorDocError('')
    try {
      const newDoc = await api.upload<SupplierDocument>(
        `/suppliers/${id}/documents`,
        file,
        vendorDocDescription ? { description: vendorDocDescription } : undefined
      )
      setVendorDocs((prev) => [...prev, newDoc])
      setVendorDocDescription('')
      if (vendorDocInputRef.current) vendorDocInputRef.current.value = ''
    } catch (err) {
      setVendorDocError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setVendorDocUploading(false)
    }
  }, [id, vendorDocDescription])

  const handleVendorDocDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setVendorDocDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleVendorDocUpload(file)
  }, [handleVendorDocUpload])

  const handleDeleteVendorDoc = async (doc: SupplierDocument) => {
    if (!confirm(`Delete "${doc.filename}"?`)) return
    try {
      await api.delete(`/suppliers/${id}/documents/${doc.id}`)
      setVendorDocs((prev) => prev.filter((d) => d.id !== doc.id))
    } catch (err) {
      console.error('Failed to delete vendor document:', err)
    }
  }

  const handleDownloadVendorDoc = (doc: SupplierDocument) => {
    const token = localStorage.getItem('discovery_token')
    const url = `/api/suppliers/${id}/documents/${doc.id}/download`
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.blob())
      .then((blob) => {
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = doc.filename
        a.click()
        URL.revokeObjectURL(a.href)
      })
  }

  // --- Training material handlers ---
  const handleMaterialUpload = useCallback(async (file: File) => {
    if (!id) return
    setMaterialUploading(true)
    setMaterialError('')
    try {
      const newMaterial = await api.upload<TrainingMaterial>(
        `/trainings/${id}/materials`,
        file,
        materialDescription ? { description: materialDescription } : undefined
      )
      setMaterials((prev) => [...prev, newMaterial])
      setMaterialDescription('')
      if (materialInputRef.current) materialInputRef.current.value = ''
    } catch (err) {
      setMaterialError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setMaterialUploading(false)
    }
  }, [id, materialDescription])

  const handleMaterialDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setMaterialDragOver(false)
    const file = e.dataTransfer.files[0]
    if (file) handleMaterialUpload(file)
  }, [handleMaterialUpload])

  const handleDeleteMaterial = async (mat: TrainingMaterial) => {
    if (!confirm(`Delete "${mat.filename}"?`)) return
    try {
      await api.delete(`/trainings/${id}/materials/${mat.id}`)
      setMaterials((prev) => prev.filter((m) => m.id !== mat.id))
    } catch (err) {
      console.error('Failed to delete material:', err)
    }
  }

  const handleDownloadMaterial = (mat: TrainingMaterial) => {
    const token = localStorage.getItem('discovery_token')
    const url = `/api/trainings/${id}/materials/${mat.id}/download`
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.blob())
      .then((blob) => {
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = mat.filename
        a.click()
        URL.revokeObjectURL(a.href)
      })
  }

  const handleDownloadAttachment = (att: DocumentAttachment) => {
    const token = localStorage.getItem('discovery_token')
    const url = `/api/documents/${id}/attachments/${att.id}/download`
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => res.blob())
      .then((blob) => {
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = att.filename
        a.click()
        URL.revokeObjectURL(a.href)
      })
  }

  const handleDownload = (version: DocumentVersion) => {
    const token = localStorage.getItem('discovery_token')
    // Open download in new tab with auth
    const url = `/api/documents/${id}/versions/${version.id}/download`
    fetch(url, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((res) => res.blob())
      .then((blob) => {
        const a = document.createElement('a')
        a.href = URL.createObjectURL(blob)
        a.download = version.filename || 'download'
        a.click()
        URL.revokeObjectURL(a.href)
      })
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
              ) : field.type === 'status' || field.key === 'status' || field.key === 'qualification_status' || field.key === 'priority' || field.key === 'severity' ? (
                <StatusBadge status={String(item[field.key] || '')} />
              ) : field.key === 'url' && item[field.key] ? (
                <a
                  href={String(item[field.key])}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:text-cyan-300 underline break-all"
                >
                  {String(item[field.key])}
                </a>
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

      {/* Document Files & Versions Section */}
      {isDocuments && (
        <div className="card mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-4">Files & Versions</h2>

          {/* Upload Area */}
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer
              ${dragOver
                ? 'border-cyan-400 bg-cyan-400/5'
                : 'border-navy-700 hover:border-navy-600 hover:bg-navy-900/50'
              }
              ${uploading ? 'pointer-events-none opacity-60' : ''}
            `}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleFileUpload(file)
              }}
            />
            <div className="text-3xl mb-2">{uploading ? '⏳' : '📁'}</div>
            <p className="text-gray-400 text-sm">
              {uploading
                ? 'Uploading...'
                : 'Drop a file here or click to upload'
              }
            </p>
            <p className="text-gray-600 text-xs mt-1">
              PDF, Word, Excel, images, and more — up to 50 MB
            </p>
          </div>

          {/* Change summary input */}
          <div className="mt-3">
            <input
              type="text"
              placeholder="Change summary (optional) — describe what changed in this version"
              value={changeSummary}
              onChange={(e) => setChangeSummary(e.target.value)}
              className="input-field text-sm"
            />
          </div>

          {/* Upload error */}
          {uploadError && (
            <p className="text-red-400 text-sm mt-2">{uploadError}</p>
          )}

          {/* Version History */}
          {versions.length > 0 && (
            <div className="mt-6">
              <h3 className="text-sm font-medium text-gray-500 mb-3">Version History</h3>
              <div className="space-y-2">
                {[...versions].reverse().map((v) => (
                  <div
                    key={v.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-navy-900/50 border border-navy-800 hover:border-navy-700 transition-colors"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="text-lg flex-shrink-0">{fileIcon(v.filename || '')}</span>
                      <div className="min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-mono text-cyan-400 flex-shrink-0">v{v.version_number}</span>
                          <span className="text-sm text-gray-200 truncate">{v.filename || 'Untitled'}</span>
                        </div>
                        {v.change_summary && (
                          <p className="text-xs text-gray-500 mt-0.5 truncate">{v.change_summary}</p>
                        )}
                        <p className="text-xs text-gray-600 mt-0.5">{formatDateTime(v.created_at)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                      {v.file_path && (
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDownload(v) }}
                          className="btn-ghost text-xs"
                          title="Download"
                        >
                          ↓ Download
                        </button>
                      )}
                      <button
                        onClick={(e) => { e.stopPropagation(); handleDeleteVersion(v) }}
                        className="btn-ghost text-xs text-red-400 hover:text-red-300 hover:bg-red-400/10"
                        title="Delete version"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {versions.length === 0 && !uploading && (
            <p className="text-gray-600 text-sm mt-4 text-center">
              No files uploaded yet. Upload your first version above.
            </p>
          )}
        </div>
      )}

      {/* Attachments Section */}
      {isDocuments && (
        <div className="card mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-4">Attachments</h2>
          <p className="text-gray-500 text-sm mb-4">
            Supporting documents, addenda, reference materials, and other files.
          </p>

          {/* Attachment Upload Area */}
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
              ${attachDragOver
                ? 'border-cyan-400 bg-cyan-400/5'
                : 'border-navy-700 hover:border-navy-600 hover:bg-navy-900/50'
              }
              ${attachUploading ? 'pointer-events-none opacity-60' : ''}
            `}
            onDragOver={(e) => { e.preventDefault(); setAttachDragOver(true) }}
            onDragLeave={() => setAttachDragOver(false)}
            onDrop={handleAttachmentDrop}
            onClick={() => attachmentInputRef.current?.click()}
          >
            <input
              ref={attachmentInputRef}
              type="file"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleAttachmentUpload(file)
              }}
            />
            <div className="text-2xl mb-1">{attachUploading ? '⏳' : '📎'}</div>
            <p className="text-gray-400 text-sm">
              {attachUploading ? 'Uploading...' : 'Drop an attachment here or click to upload'}
            </p>
          </div>

          {/* Description input */}
          <div className="mt-3">
            <input
              type="text"
              placeholder="Description (optional) — what is this attachment?"
              value={attachDescription}
              onChange={(e) => setAttachDescription(e.target.value)}
              className="input-field text-sm"
            />
          </div>

          {attachError && (
            <p className="text-red-400 text-sm mt-2">{attachError}</p>
          )}

          {/* Attachment List */}
          {attachments.length > 0 && (
            <div className="mt-4 space-y-2">
              {attachments.map((att) => (
                <div
                  key={att.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-navy-900/50 border border-navy-800 hover:border-navy-700 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-lg flex-shrink-0">{fileIcon(att.filename)}</span>
                    <div className="min-w-0">
                      <span className="text-sm text-gray-200 truncate block">{att.filename}</span>
                      {att.description && (
                        <p className="text-xs text-gray-500 mt-0.5 truncate">{att.description}</p>
                      )}
                      <p className="text-xs text-gray-600 mt-0.5">
                        {att.file_size ? formatFileSize(att.file_size) + ' · ' : ''}{formatDateTime(att.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDownloadAttachment(att) }}
                      className="btn-ghost text-xs"
                      title="Download"
                    >
                      ↓ Download
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteAttachment(att) }}
                      className="btn-ghost text-xs text-red-400 hover:text-red-300 hover:bg-red-400/10"
                      title="Delete attachment"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {attachments.length === 0 && !attachUploading && (
            <p className="text-gray-600 text-sm mt-4 text-center">
              No attachments yet.
            </p>
          )}
        </div>
      )}

      {/* Equipment Photos Section */}
      {isEquipment && (
        <div className="card mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-4">📷 Photos</h2>
          <p className="text-gray-500 text-sm mb-4">
            Equipment photos, nameplates, labels, or setup images.
          </p>

          {/* Photo Upload Area */}
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
              ${photoDragOver
                ? 'border-cyan-400 bg-cyan-400/5'
                : 'border-navy-700 hover:border-navy-600 hover:bg-navy-900/50'
              }
              ${photoUploading ? 'pointer-events-none opacity-60' : ''}
            `}
            onDragOver={(e) => { e.preventDefault(); setPhotoDragOver(true) }}
            onDragLeave={() => setPhotoDragOver(false)}
            onDrop={handlePhotoDrop}
            onClick={() => photoInputRef.current?.click()}
          >
            <input
              ref={photoInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handlePhotoUpload(file)
              }}
            />
            <div className="text-2xl mb-1">{photoUploading ? '⏳' : '📷'}</div>
            <p className="text-gray-400 text-sm">
              {photoUploading ? 'Uploading...' : 'Drop a photo here or click to upload'}
            </p>
            <p className="text-gray-600 text-xs mt-1">
              PNG, JPG, GIF, SVG, WebP — up to 20 MB
            </p>
          </div>

          {/* Description input */}
          <div className="mt-3">
            <input
              type="text"
              placeholder="Description (optional) — e.g. nameplate, front panel, setup"
              value={photoDescription}
              onChange={(e) => setPhotoDescription(e.target.value)}
              className="input-field text-sm"
            />
          </div>

          {photoError && (
            <p className="text-red-400 text-sm mt-2">{photoError}</p>
          )}

          {/* Photo Grid */}
          {photos.length > 0 && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
              {photos.map((photo) => (
                <div
                  key={photo.id}
                  className="group relative rounded-lg border border-navy-800 overflow-hidden bg-navy-900/50 hover:border-navy-700 transition-colors"
                >
                  {/* Photo preview */}
                  <div className="aspect-square bg-navy-900 flex items-center justify-center overflow-hidden">
                    <AuthImage
                      src={`/api/equipment/${id}/photos/${photo.id}/download`}
                      alt={photo.description || photo.filename}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  {/* Photo info */}
                  <div className="p-2">
                    <p className="text-xs text-gray-300 truncate">{photo.filename}</p>
                    {photo.description && (
                      <p className="text-xs text-gray-500 truncate">{photo.description}</p>
                    )}
                    <p className="text-xs text-gray-600 mt-0.5">
                      {photo.file_size ? formatFileSize(photo.file_size) : ''}
                    </p>
                  </div>
                  {/* Overlay actions */}
                  <div className="absolute top-1 right-1 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDownloadPhoto(photo) }}
                      className="bg-navy-900/80 text-gray-300 hover:text-white rounded p-1 text-xs"
                      title="Download"
                    >
                      ↓
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeletePhoto(photo) }}
                      className="bg-navy-900/80 text-red-400 hover:text-red-300 rounded p-1 text-xs"
                      title="Delete"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {photos.length === 0 && !photoUploading && (
            <p className="text-gray-600 text-sm mt-4 text-center">
              No photos yet. Upload an image above.
            </p>
          )}
        </div>
      )}

      {/* Supplier / Vendor Documents Section */}
      {isSuppliers && (
        <div className="card mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-4">Vendor Documents</h2>
          <p className="text-gray-500 text-sm mb-4">
            Certificates, agreements, qualification records, and other vendor documentation.
          </p>

          {/* Vendor Doc Upload Area */}
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
              ${vendorDocDragOver
                ? 'border-cyan-400 bg-cyan-400/5'
                : 'border-navy-700 hover:border-navy-600 hover:bg-navy-900/50'
              }
              ${vendorDocUploading ? 'pointer-events-none opacity-60' : ''}
            `}
            onDragOver={(e) => { e.preventDefault(); setVendorDocDragOver(true) }}
            onDragLeave={() => setVendorDocDragOver(false)}
            onDrop={handleVendorDocDrop}
            onClick={() => vendorDocInputRef.current?.click()}
          >
            <input
              ref={vendorDocInputRef}
              type="file"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleVendorDocUpload(file)
              }}
            />
            <div className="text-2xl mb-1">{vendorDocUploading ? '⏳' : '📋'}</div>
            <p className="text-gray-400 text-sm">
              {vendorDocUploading ? 'Uploading...' : 'Drop a file here or click to upload'}
            </p>
            <p className="text-gray-600 text-xs mt-1">
              PDF, Word, Excel, images, and more — up to 50 MB
            </p>
          </div>

          {/* Description input */}
          <div className="mt-3">
            <input
              type="text"
              placeholder="Description (optional) — e.g. ISO certificate, supply agreement, qualification report"
              value={vendorDocDescription}
              onChange={(e) => setVendorDocDescription(e.target.value)}
              className="input-field text-sm"
            />
          </div>

          {vendorDocError && (
            <p className="text-red-400 text-sm mt-2">{vendorDocError}</p>
          )}

          {/* Vendor Document List */}
          {vendorDocs.length > 0 && (
            <div className="mt-4 space-y-2">
              {vendorDocs.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-navy-900/50 border border-navy-800 hover:border-navy-700 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-lg flex-shrink-0">{fileIcon(doc.filename)}</span>
                    <div className="min-w-0">
                      <span className="text-sm text-gray-200 truncate block">{doc.filename}</span>
                      {doc.description && (
                        <p className="text-xs text-gray-500 mt-0.5 truncate">{doc.description}</p>
                      )}
                      <p className="text-xs text-gray-600 mt-0.5">
                        {doc.file_size ? formatFileSize(doc.file_size) + ' · ' : ''}{formatDateTime(doc.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDownloadVendorDoc(doc) }}
                      className="btn-ghost text-xs"
                      title="Download"
                    >
                      ↓ Download
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteVendorDoc(doc) }}
                      className="btn-ghost text-xs text-red-400 hover:text-red-300 hover:bg-red-400/10"
                      title="Delete"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {vendorDocs.length === 0 && !vendorDocUploading && (
            <p className="text-gray-600 text-sm mt-4 text-center">
              No vendor documents yet.
            </p>
          )}
        </div>
      )}

      {/* Training Materials Section */}
      {isTrainings && (
        <div className="card mt-6">
          <h2 className="text-lg font-semibold text-gray-200 mb-4">Training Materials</h2>
          <p className="text-gray-500 text-sm mb-4">
            Slides, handouts, videos, SOPs, and other training content.
          </p>

          {/* Material Upload Area */}
          <div
            className={`
              relative border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
              ${materialDragOver
                ? 'border-cyan-400 bg-cyan-400/5'
                : 'border-navy-700 hover:border-navy-600 hover:bg-navy-900/50'
              }
              ${materialUploading ? 'pointer-events-none opacity-60' : ''}
            `}
            onDragOver={(e) => { e.preventDefault(); setMaterialDragOver(true) }}
            onDragLeave={() => setMaterialDragOver(false)}
            onDrop={handleMaterialDrop}
            onClick={() => materialInputRef.current?.click()}
          >
            <input
              ref={materialInputRef}
              type="file"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleMaterialUpload(file)
              }}
            />
            <div className="text-2xl mb-1">{materialUploading ? '⏳' : '📚'}</div>
            <p className="text-gray-400 text-sm">
              {materialUploading ? 'Uploading...' : 'Drop a file here or click to upload'}
            </p>
            <p className="text-gray-600 text-xs mt-1">
              PDF, Word, Excel, PowerPoint, images, videos — up to 50 MB
            </p>
          </div>

          {/* Description input */}
          <div className="mt-3">
            <input
              type="text"
              placeholder="Description (optional) — e.g. slide deck, handout, training video"
              value={materialDescription}
              onChange={(e) => setMaterialDescription(e.target.value)}
              className="input-field text-sm"
            />
          </div>

          {materialError && (
            <p className="text-red-400 text-sm mt-2">{materialError}</p>
          )}

          {/* Material List */}
          {materials.length > 0 && (
            <div className="mt-4 space-y-2">
              {materials.map((mat) => (
                <div
                  key={mat.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-navy-900/50 border border-navy-800 hover:border-navy-700 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="text-lg flex-shrink-0">{fileIcon(mat.filename)}</span>
                    <div className="min-w-0">
                      <span className="text-sm text-gray-200 truncate block">{mat.filename}</span>
                      {mat.description && (
                        <p className="text-xs text-gray-500 mt-0.5 truncate">{mat.description}</p>
                      )}
                      <p className="text-xs text-gray-600 mt-0.5">
                        {mat.file_size ? formatFileSize(mat.file_size) + ' · ' : ''}{formatDateTime(mat.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDownloadMaterial(mat) }}
                      className="btn-ghost text-xs"
                      title="Download"
                    >
                      ↓ Download
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDeleteMaterial(mat) }}
                      className="btn-ghost text-xs text-red-400 hover:text-red-300 hover:bg-red-400/10"
                      title="Delete"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {materials.length === 0 && !materialUploading && (
            <p className="text-gray-600 text-sm mt-4 text-center">
              No materials yet. Upload training content above.
            </p>
          )}
        </div>
      )}

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
