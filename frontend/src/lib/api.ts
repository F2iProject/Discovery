const API_BASE = '/api'

interface RequestOptions {
  method?: string
  body?: unknown
  headers?: Record<string, string>
}

class ApiClient {
  private getToken(): string | null {
    return localStorage.getItem('discovery_token')
  }

  private async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options
    const token = this.getToken()

    const config: RequestInit = {
      method,
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...headers,
      },
    }

    if (body) {
      config.body = JSON.stringify(body)
    }

    const response = await fetch(`${API_BASE}${path}`, config)

    if (response.status === 401) {
      localStorage.removeItem('discovery_token')
      window.location.href = '/login'
      throw new Error('Unauthorized')
    }

    if (response.status === 204) {
      return undefined as T
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Request failed' }))
      const detail = error.detail
      const message = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: { msg?: string }) => d.msg || String(d)).join(', ')
        : 'Request failed'
      throw new Error(message)
    }

    return response.json()
  }

  get<T>(path: string) {
    return this.request<T>(path)
  }

  post<T>(path: string, body: unknown) {
    return this.request<T>(path, { method: 'POST', body })
  }

  patch<T>(path: string, body: unknown) {
    return this.request<T>(path, { method: 'PATCH', body })
  }

  delete(path: string) {
    return this.request(path, { method: 'DELETE' })
  }

  async upload<T>(path: string, file: File, fields?: Record<string, string>): Promise<T> {
    const token = this.getToken()
    const formData = new FormData()
    formData.append('file', file)
    if (fields) {
      Object.entries(fields).forEach(([key, value]) => formData.append(key, value))
    }

    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    })

    if (response.status === 401) {
      localStorage.removeItem('discovery_token')
      window.location.href = '/login'
      throw new Error('Unauthorized')
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Upload failed' }))
      const detail = error.detail
      const message = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
        ? detail.map((d: { msg?: string }) => d.msg || String(d)).join(', ')
        : 'Upload failed'
      throw new Error(message)
    }

    return response.json()
  }
}

export const api = new ApiClient()
