const API_BASE = import.meta.env.VITE_API_BASE || ''

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options)
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`)
    err.status = res.status
    err.data = await res.json().catch(() => ({}))
    throw err
  }
  return res.json()
}

// ====== AUTENTICACIÓN ======
export async function register(email, password) {
  return request('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
}

export async function login(email, password) {
  const data = await request('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  })
  // Guardar token
  localStorage.setItem('accessToken', data.access_token)
  localStorage.setItem('user', JSON.stringify({ user_id: data.user_id, email: data.email }))
  return data
}

export function logout() {
  localStorage.removeItem('accessToken')
  localStorage.removeItem('user')
}

export function isAuthenticated() {
  return !!localStorage.getItem('accessToken')
}

export function getCurrentUser() {
  const user = localStorage.getItem('user')
  return user ? JSON.parse(user) : null
}

// ====== ENDPOINTS DEL DASHBOARD ======
export function fetchDashboard(dispositivoId = 'esp8266') {
  return request(`/api/dashboard/actual?dispositivo_id=${dispositivoId}`)
}

export function fetchResumen(dispositivoId = 'esp8266') {
  return request(`/api/dashboard/resumen?dispositivo_id=${dispositivoId}`)
}

export function fetchHistorial(dispositivoId = 'esp8266', limit = 30) {
  return request(`/api/sensores/historial?dispositivo_id=${dispositivoId}&limit=${limit}`)
}

export function fetchHealth() {
  return request('/health')
}

export function fetchClimaPronostico(ciudad) {
  const q = ciudad ? `?ciudad=${encodeURIComponent(ciudad)}` : ''
  return request(`/api/clima/pronostico${q}`)
}

// ====== CONTROL MANUAL MQTT ======
export function fetchMqttStatus() {
  return request('/api/debug/mqtt')
}

export function iniciarRiegoManual() {
  return request('/api/riego/manual/iniciar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
}

export function detenerRiegoManual() {
  return request('/api/riego/manual/detener', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  })
}
