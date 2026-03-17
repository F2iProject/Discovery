// Auth
export interface User {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'member' | 'viewer'
  is_active: boolean
  tenant_id: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

// Documents
export interface Document {
  id: string
  title: string
  doc_number: string | null
  doc_type: string
  status: string
  description: string | null
  current_version: number
  created_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

export interface DocumentVersion {
  id: string
  document_id: string
  version_number: number
  filename: string
  file_path: string | null
  change_summary: string | null
  uploaded_by: string | null
  created_at: string
}

// Change Control
export interface ChangeControl {
  id: string
  title: string
  change_number: string | null
  status: string
  change_type: string
  description: string | null
  justification: string | null
  impact_assessment: string | null
  requested_by: string | null
  document_id: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

// CAPA
export interface CAPA {
  id: string
  title: string
  capa_number: string | null
  capa_type: string
  status: string
  priority: string
  description: string | null
  root_cause: string | null
  source: string | null
  source_id: string | null
  target_date: string | null
  closed_date: string | null
  created_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

export interface CAPAAction {
  id: string
  capa_id: string
  description: string
  action_type: string
  status: string
  assigned_to: string | null
  completed_at: string | null
  created_at: string
}

// Risk
export interface Risk {
  id: string
  title: string
  risk_number: string | null
  status: string
  category: string | null
  description: string | null
  severity: number
  likelihood: number
  risk_level: string | null
  mitigation: string | null
  created_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

// Training
export interface Training {
  id: string
  title: string
  description: string | null
  status: string
  document_id: string | null
  created_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

export interface TrainingAssignment {
  id: string
  training_id: string
  user_id: string
  status: string
  completed_at: string | null
  due_date: string | null
  created_at: string
}

// Non-Conformance
export interface NonConformance {
  id: string
  title: string
  nc_number: string | null
  status: string
  severity: string
  category: string | null
  description: string | null
  disposition: string | null
  disposition_rationale: string | null
  capa_id: string | null
  reported_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

// Deviation
export interface Deviation {
  id: string
  title: string
  deviation_number: string | null
  deviation_type: string
  status: string
  description: string | null
  justification: string | null
  resolution: string | null
  affected_document_id: string | null
  capa_id: string | null
  reported_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

// Equipment
export interface Equipment {
  id: string
  name: string
  equipment_id: string | null
  category: string | null
  manufacturer: string | null
  model: string | null
  serial_number: string | null
  location: string | null
  status: string
  notes: string | null
  added_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

// Calibration
export interface Calibration {
  id: string
  equipment_id: string
  calibration_date: string
  next_due: string | null
  interval_days: number | null
  result: string
  method: string | null
  certificate_ref: string | null
  notes: string | null
  performed_by: string | null
  tenant_id: string
  created_at: string
}

// Complaint
export interface Complaint {
  id: string
  title: string
  complaint_number: string | null
  status: string
  source: string | null
  product: string | null
  lot_number: string | null
  description: string | null
  investigation_notes: string | null
  capa_id: string | null
  reported_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}

// Supplier
export interface Supplier {
  id: string
  name: string
  contact_name: string | null
  contact_email: string | null
  contact_phone: string | null
  website: string | null
  supplies: string | null
  qualification_status: string
  notes: string | null
  added_by: string | null
  tenant_id: string
  created_at: string
  updated_at: string
}
