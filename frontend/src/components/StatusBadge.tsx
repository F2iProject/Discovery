import { cn } from '@/lib/utils'

const statusStyles: Record<string, string> = {
  // General
  draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  active: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  open: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  closed: 'bg-gray-500/20 text-gray-400 border-gray-500/30',

  // Documents
  in_review: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  approved: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  archived: 'bg-gray-500/20 text-gray-400 border-gray-500/30',

  // CAPA
  investigation: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  action_defined: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  implemented: 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30',

  // Change Control
  submitted: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  under_review: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  rejected: 'bg-red-500/20 text-red-400 border-red-500/30',

  // NC
  dispositioned: 'bg-purple-500/20 text-purple-400 border-purple-500/30',

  // Equipment
  maintenance: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  retired: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  out_of_service: 'bg-red-500/20 text-red-400 border-red-500/30',

  // Training
  assigned: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  in_progress: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  completed: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',

  // Calibration
  pass: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  fail: 'bg-red-500/20 text-red-400 border-red-500/30',
  adjusted: 'bg-amber-500/20 text-amber-400 border-amber-500/30',

  // Supplier
  pending: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  conditional: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
  disqualified: 'bg-red-500/20 text-red-400 border-red-500/30',

  // Risk
  mitigated: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',

  // Risk levels
  low: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  medium: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  high: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  critical: 'bg-red-500/20 text-red-400 border-red-500/30',

  // Priority
  low_priority: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  medium_priority: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
  high_priority: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
  critical_priority: 'bg-red-500/20 text-red-400 border-red-500/30',
}

interface StatusBadgeProps {
  status: string | null
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  if (!status) return <span className="text-gray-600">—</span>
  const style = statusStyles[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30'
  const label = status.replace(/_/g, ' ')

  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize',
        style,
        className,
      )}
    >
      {label}
    </span>
  )
}
