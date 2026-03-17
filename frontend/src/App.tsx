import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import { Sidebar } from '@/components/Sidebar'
import { LoginPage } from '@/pages/LoginPage'
import { DashboardPage } from '@/pages/DashboardPage'
import { ModuleListPage } from '@/pages/ModuleListPage'
import { ModuleDetailPage } from '@/pages/ModuleDetailPage'

function ProtectedLayout() {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-navy-950">
        <div className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!isAuthenticated) return <Navigate to="/login" replace />

  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-64 p-8">
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/documents" element={<ModuleListPage module="documents" />} />
          <Route path="/documents/:id" element={<ModuleDetailPage module="documents" />} />
          <Route path="/change-controls" element={<ModuleListPage module="change-controls" />} />
          <Route path="/change-controls/:id" element={<ModuleDetailPage module="change-controls" />} />
          <Route path="/capas" element={<ModuleListPage module="capas" />} />
          <Route path="/capas/:id" element={<ModuleDetailPage module="capas" />} />
          <Route path="/risks" element={<ModuleListPage module="risks" />} />
          <Route path="/risks/:id" element={<ModuleDetailPage module="risks" />} />
          <Route path="/trainings" element={<ModuleListPage module="trainings" />} />
          <Route path="/trainings/:id" element={<ModuleDetailPage module="trainings" />} />
          <Route path="/nonconformances" element={<ModuleListPage module="nonconformances" />} />
          <Route path="/nonconformances/:id" element={<ModuleDetailPage module="nonconformances" />} />
          <Route path="/deviations" element={<ModuleListPage module="deviations" />} />
          <Route path="/deviations/:id" element={<ModuleDetailPage module="deviations" />} />
          <Route path="/equipment" element={<ModuleListPage module="equipment" />} />
          <Route path="/equipment/:id" element={<ModuleDetailPage module="equipment" />} />
          <Route path="/calibrations" element={<ModuleListPage module="calibrations" />} />
          <Route path="/calibrations/:id" element={<ModuleDetailPage module="calibrations" />} />
          <Route path="/complaints" element={<ModuleListPage module="complaints" />} />
          <Route path="/complaints/:id" element={<ModuleDetailPage module="complaints" />} />
          <Route path="/suppliers" element={<ModuleListPage module="suppliers" />} />
          <Route path="/suppliers/:id" element={<ModuleDetailPage module="suppliers" />} />
        </Routes>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={<ProtectedLayout />} />
      </Routes>
    </AuthProvider>
  )
}
