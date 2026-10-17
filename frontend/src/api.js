import { lang, t } from './i18n/index.js'

// En local Vite redirige /api al backend; en Render se indica la URL del backend con VITE_API_URL
const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
const TOKEN_KEY = 'panel_token'
const LOGIN_AT_KEY = 'panel_login_at'
// Igual que en el servidor (PANEL_SESSION_HOURS): pasado este tiempo se vuelve a pedir la contraseña
const SESSION_MS = 12 * 60 * 60 * 1000

export function getToken() {
  try {
    const token = localStorage.getItem(TOKEN_KEY)
    const loginAt = Number(localStorage.getItem(LOGIN_AT_KEY) || 0)
    if (token && Date.now() - loginAt > SESSION_MS) { setToken(null); return null }
    return token
  } catch { return null }
}
export function setToken(token) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token)
      localStorage.setItem(LOGIN_AT_KEY, String(Date.now()))
    } else {
      localStorage.removeItem(TOKEN_KEY)
      localStorage.removeItem(LOGIN_AT_KEY)
    }
  } catch { /* sin almacenamiento */ }
}

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status }
}

// Los errores de la API vienen en español; si el panel está en inglés se traducen los conocidos
function readError(data) {
  if (!data) return t('Algo ha fallado. Inténtalo de nuevo.')
  if (typeof data === 'string') return t(data)
  if (Array.isArray(data)) return data.map((m) => t(m)).join(' ')
  if (data.detail) return t(data.detail)
  return Object.values(data).flat().map((m) => t(m)).join(' ')
}

export async function api(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json', 'Accept-Language': lang }
  const token = getToken()
  if (auth && token) headers.Authorization = `Token ${token}`
  const res = await fetch(`${API_URL}/api${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined })
  const data = res.status === 204 ? null : await res.json().catch(() => null)
  if (res.status === 401 && auth) { setToken(null); window.dispatchEvent(new Event('panel:logout')) }
  if (!res.ok) throw new ApiError(readError(data), res.status)
  return data
}

export const post = (path, body, opts = {}) => api(path, { method: 'POST', body, ...opts })
export const patch = (path, body) => api(path, { method: 'PATCH', body })

/** Descarga un archivo de la API (con la sesión del panel) y lo guarda con ese nombre. */
export async function download(path, filename) {
  const res = await fetch(`${API_URL}/api${path}`, { headers: { Authorization: `Token ${getToken()}`, 'Accept-Language': lang } })
  if (!res.ok) throw new ApiError(t('No se ha podido descargar el archivo.'), res.status)
  const url = URL.createObjectURL(await res.blob())
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}
