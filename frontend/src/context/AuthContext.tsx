import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { api } from '@/lib/api'
import type { User, TokenResponse } from '@/types'

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string, orgName: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    try {
      const token = localStorage.getItem('discovery_token')
      if (!token) {
        setLoading(false)
        return
      }
      const user = await api.get<User>('/auth/me')
      setUser(user)
    } catch {
      localStorage.removeItem('discovery_token')
      setUser(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = async (email: string, password: string) => {
    const data = await api.post<TokenResponse>('/auth/login', { email, password })
    localStorage.setItem('discovery_token', data.access_token)
    await fetchUser()
  }

  const register = async (email: string, password: string, fullName: string, orgName: string) => {
    const data = await api.post<TokenResponse>('/auth/register', {
      email,
      password,
      full_name: fullName,
      organization_name: orgName,
    })
    localStorage.setItem('discovery_token', data.access_token)
    await fetchUser()
  }

  const logout = () => {
    localStorage.removeItem('discovery_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within AuthProvider')
  return context
}
