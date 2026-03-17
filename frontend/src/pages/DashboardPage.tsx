import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useAuth } from '@/context/AuthContext'
import { PageHeader } from '@/components/PageHeader'
import {
  FileText, GitBranch, Shield, AlertTriangle, GraduationCap,
  XCircle, AlertOctagon, Wrench, Gauge, MessageSquare, Truck,
} from 'lucide-react'

interface ModuleStat {
  key: string
  label: string
  path: string
  icon: React.ElementType
  count: number
  color: string
}

const moduleConfig = [
  { key: 'documents', label: 'Documents', path: '/documents', icon: FileText, color: 'text-blue-400' },
  { key: 'capas', label: 'CAPAs', path: '/capas', icon: Shield, color: 'text-cyan-400' },
  { key: 'risks', label: 'Risks', path: '/risks', icon: AlertTriangle, color: 'text-amber-400' },
  { key: 'trainings', label: 'Training', path: '/trainings', icon: GraduationCap, color: 'text-purple-400' },
  { key: 'change-controls', label: 'Change Control', path: '/change-controls', icon: GitBranch, color: 'text-emerald-400' },
  { key: 'nonconformances', label: 'Non-Conformances', path: '/nonconformances', icon: XCircle, color: 'text-red-400' },
  { key: 'deviations', label: 'Deviations', path: '/deviations', icon: AlertOctagon, color: 'text-orange-400' },
  { key: 'equipment', label: 'Equipment', path: '/equipment', icon: Wrench, color: 'text-sky-400' },
  { key: 'calibrations', label: 'Calibrations', path: '/calibrations', icon: Gauge, color: 'text-teal-400' },
  { key: 'complaints', label: 'Complaints', path: '/complaints', icon: MessageSquare, color: 'text-pink-400' },
  { key: 'suppliers', label: 'Suppliers', path: '/suppliers', icon: Truck, color: 'text-lime-400' },
]

export function DashboardPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [stats, setStats] = useState<ModuleStat[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchCounts() {
      const results = await Promise.allSettled(
        moduleConfig.map(async (mod) => {
          const items = await api.get<{ id: string }[]>(`/${mod.key}`)
          return { ...mod, count: items.length }
        })
      )
      setStats(
        results.map((r, i) =>
          r.status === 'fulfilled' ? r.value : { ...moduleConfig[i], count: 0 }
        )
      )
      setLoading(false)
    }
    fetchCounts()
  }, [])

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.full_name?.split(' ')[0] || 'Scientist'}`}
        subtitle="Here's what's happening in your lab"
      />

      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {[...Array(11)].map((_, i) => (
            <div key={i} className="card animate-pulse h-28" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {stats.map((mod) => (
            <button
              key={mod.key}
              onClick={() => navigate(mod.path)}
              className="card hover:border-navy-600 transition-colors text-left group"
            >
              <div className="flex items-center gap-3 mb-3">
                <mod.icon size={20} className={mod.color} />
                <span className="text-sm font-medium text-gray-400 group-hover:text-gray-200 transition-colors">
                  {mod.label}
                </span>
              </div>
              <p className="text-3xl font-semibold text-gray-100">{mod.count}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
