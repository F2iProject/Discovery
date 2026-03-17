import { Link, useLocation } from 'react-router-dom'
import {
  FileText, GitBranch, Shield, AlertTriangle, GraduationCap,
  XCircle, AlertOctagon, Wrench, Gauge, MessageSquare,
  Truck, LayoutDashboard, LogOut,
} from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { cn } from '@/lib/utils'

const navGroups = [
  {
    label: 'Overview',
    items: [
      { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    ],
  },
  {
    label: 'Organize',
    items: [
      { to: '/documents', label: 'Documents', icon: FileText },
      { to: '/equipment', label: 'Equipment', icon: Wrench },
      { to: '/calibrations', label: 'Calibrations', icon: Gauge },
      { to: '/suppliers', label: 'Suppliers', icon: Truck },
    ],
  },
  {
    label: 'Track',
    items: [
      { to: '/capas', label: 'CAPAs', icon: Shield },
      { to: '/risks', label: 'Risks', icon: AlertTriangle },
      { to: '/nonconformances', label: 'Non-Conformances', icon: XCircle },
      { to: '/deviations', label: 'Deviations', icon: AlertOctagon },
      { to: '/complaints', label: 'Complaints', icon: MessageSquare },
    ],
  },
  {
    label: 'Develop',
    items: [
      { to: '/change-controls', label: 'Change Control', icon: GitBranch },
      { to: '/trainings', label: 'Training', icon: GraduationCap },
    ],
  },
]

export function Sidebar() {
  const location = useLocation()
  const { user, logout } = useAuth()

  return (
    <aside className="w-64 h-screen bg-navy-900 border-r border-navy-800 flex flex-col fixed left-0 top-0 z-30">
      {/* Logo */}
      <div className="h-16 flex items-center px-6 border-b border-navy-800">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-cyan-500 rounded-lg flex items-center justify-center">
            <span className="text-navy-950 font-bold text-sm">D</span>
          </div>
          <span className="text-lg font-semibold text-gray-100">Discovery</span>
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-4 px-3">
        {navGroups.map((group) => (
          <div key={group.label} className="mb-6">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-gray-500 px-3 mb-2">
              {group.label}
            </p>
            {group.items.map((item) => {
              const isActive = location.pathname === item.to ||
                (item.to !== '/' && location.pathname.startsWith(item.to))
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors mb-0.5',
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-navy-800'
                  )}
                >
                  <item.icon size={18} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </div>
        ))}
      </nav>

      {/* User */}
      <div className="border-t border-navy-800 p-4">
        <div className="flex items-center justify-between">
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-200 truncate">
              {user?.full_name}
            </p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="text-gray-500 hover:text-gray-300 transition-colors p-1"
            title="Sign out"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  )
}
