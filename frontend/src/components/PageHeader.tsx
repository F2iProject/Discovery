import { Link } from 'react-router-dom'
import { Plus, ArrowLeft } from 'lucide-react'

interface PageHeaderProps {
  title: string
  subtitle?: string
  backTo?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export function PageHeader({ title, subtitle, backTo, action }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between mb-8">
      <div>
        {backTo && (
          <Link
            to={backTo}
            className="inline-flex items-center gap-1 text-sm text-gray-500 hover:text-gray-300 mb-2 transition-colors"
          >
            <ArrowLeft size={14} />
            Back
          </Link>
        )}
        <h1 className="text-2xl font-semibold text-gray-100">{title}</h1>
        {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
      </div>
      {action && (
        <button onClick={action.onClick} className="btn-primary flex items-center gap-2">
          <Plus size={18} />
          {action.label}
        </button>
      )}
    </div>
  )
}
