import { formatDate } from '@/lib/utils'
import { StatusBadge } from './StatusBadge'

export interface Column<T> {
  key: string
  label: string
  render?: (item: T) => React.ReactNode
  type?: 'text' | 'status' | 'date' | 'number'
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  onRowClick?: (item: T) => void
  loading?: boolean
}

export function DataTable<T extends { id: string }>({
  columns,
  data,
  onRowClick,
  loading,
}: DataTableProps<T>) {
  if (loading) {
    return (
      <div className="card">
        <div className="animate-pulse space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-10 bg-navy-800 rounded" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden p-0">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-navy-800">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="text-left text-xs font-semibold uppercase tracking-wider text-gray-500 px-6 py-3"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr
                key={item.id}
                onClick={() => onRowClick?.(item)}
                className={`border-b border-navy-800/50 last:border-0 transition-colors ${
                  onRowClick ? 'cursor-pointer hover:bg-navy-800/50' : ''
                }`}
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-6 py-4 text-sm">
                    {col.render
                      ? col.render(item)
                      : col.type === 'status'
                      ? <StatusBadge status={(item as Record<string, unknown>)[col.key] as string} />
                      : col.type === 'date'
                      ? <span className="text-gray-400">{formatDate((item as Record<string, unknown>)[col.key] as string)}</span>
                      : <span className="text-gray-200">{String((item as Record<string, unknown>)[col.key] ?? '—')}</span>
                    }
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
