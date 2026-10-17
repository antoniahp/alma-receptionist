import { useEffect, useState } from 'react'
import { useLocation, NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { api, getToken, setToken } from './api.js'
import Logo from './components/Logo.jsx'
import { t } from './i18n/index.js'
import { ToastProvider } from './components/Toast.jsx'
import useOwnerAlerts from './components/useOwnerAlerts.js'
import Citas from './panel/Citas.jsx'
import Clientas from './panel/Clientas.jsx'
import Cuentas from './panel/Cuentas.jsx'
import Login from './panel/Login.jsx'
import Mensajes from './panel/Mensajes.jsx'
import Productos from './panel/Productos.jsx'
import Recordatorios from './panel/Recordatorios.jsx'
import Tratamientos from './panel/Tratamientos.jsx'
import Legal from './web/Legal.jsx'
import Web from './web/Web.jsx'

function StatusChips({ status }) {
  if (!status) return null
  const assistant = status.business?.assistant_name || 'Aura'
  return (
    <div className="chips">
      <span className={`chip-status ${status.llm.available ? 'on' : 'off'}`} title={status.llm.available ? t('Usa el modelo {model}', { model: status.llm.model }) : t('La IA no responde: contesta con respuestas fijas')}>
        {assistant} · {status.llm.available ? t('con IA') : t('modo básico')}
      </span>
      <span className={`chip-status ${status.telegram.enabled ? 'on' : 'off'}`} title={status.telegram.enabled ? t('Los mensajes salen por Telegram') : t('Falta el token del bot en backend/.env')}>
        Telegram · {status.telegram.enabled ? t('conectado') : t('sin conectar')}
      </span>
    </div>
  )
}

// Al cambiar de página se vuelve arriba (si no, se queda la posición de la página anterior)
function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])
  return null
}

function Panel() {
  const [status, setStatus] = useState(null)
  const [dash, setDash] = useState(null)
  const navigate = useNavigate()

  const refreshDash = () => api('/dashboard/').then(setDash).catch(() => {})
  useEffect(() => {
    api('/status/').then((s) => { setStatus(s); document.title = `${t('Panel')} · ${s.business?.name || 'Alma'}` }).catch(() => {})
    refreshDash()
    const timer = setInterval(refreshDash, 10000)
    return () => clearInterval(timer)
  }, [])

  useOwnerAlerts(dash)
  const logout = () => { setToken(null); navigate('/panel/login') }
  const badge = (n) => <span className="count" data-zero={!n || undefined}>{n ?? 0}</span>
  const owner = status?.business?.owner

  return (
    <div className="wrap">
      <header className="top">
        <div>
          <div className="brand">
            <Logo className="logo-panel" />
            <div>
              <div className="label">{owner ? t('Panel de {owner}', { owner }) : t('Panel')}<span className="only-you"> · {t('solo lo ves tú')}</span></div>
              <h1>{status?.business?.name || t('Panel')}</h1>
            </div>
          </div>
        </div>
        <div className="top-actions">
          <StatusChips status={status} />
          <a className="btn ghost" href="/" target="_blank" rel="noreferrer">{t('Ver mi web')}</a>
          <button className="btn ghost" onClick={logout}>{t('Salir')}</button>
        </div>
      </header>

      {status?.demo && <p className="demo-banner">{t('Estás en la demo: los datos son de ejemplo y se reinician solos. No se envía ningún correo de verdad.')}</p>}
      <nav className="tabs">
        <NavLink to="/panel" end>{t('Citas')}</NavLink>
        <NavLink to="/panel/clientas">{t('Clientas')}</NavLink>
        <NavLink to="/panel/mensajes">{t('Mensajes')} {badge((dash?.help_requests_open || 0) + (dash?.reminders_due || 0) + (dash?.reactivations_due || 0))}</NavLink>
        <NavLink to="/panel/productos">{t('Productos')} {badge((dash?.orders_to_approve || 0) + (dash?.products_to_order || 0))}</NavLink>
        <NavLink to="/panel/cuentas">{t('Cuentas')}</NavLink>
        <NavLink to="/panel/tratamientos">{t('Tratamientos')}</NavLink>
      </nav>

      <Routes>
        <Route index element={<Citas onChange={refreshDash} />} />
        <Route path="clientas" element={<Clientas />} />
        <Route path="mensajes" element={<><Mensajes status={status} onChange={refreshDash} /><Recordatorios onChange={refreshDash} telegram={status?.telegram} /></>} />
        <Route path="recordatorios" element={<Navigate to="/panel/mensajes" replace />} />
        <Route path="productos" element={<Productos onChange={refreshDash} />} />
        <Route path="tratamientos" element={<Tratamientos />} />
        <Route path="cuentas" element={<Cuentas />} />
        <Route path="*" element={<Navigate to="/panel" replace />} />
      </Routes>
    </div>
  )
}

function RequireLogin({ children }) {
  const [authed, setAuthed] = useState(Boolean(getToken()))
  useEffect(() => {
    const off = () => setAuthed(false)
    window.addEventListener('panel:logout', off)
    return () => window.removeEventListener('panel:logout', off)
  }, [])
  return authed ? children : <Navigate to="/panel/login" replace />
}

export default function App() {
  return (
    <ToastProvider>
      <ScrollToTop />
      <Routes>
        {/* Para las clientas: la web del centro */}
        <Route path="/" element={<Web />} />
        <Route path="/reservar" element={<Web />} />
        <Route path="/aviso-legal" element={<Legal page="aviso-legal" />} />
        <Route path="/privacidad" element={<Legal page="privacidad" />} />
        <Route path="/cookies" element={<Legal page="cookies" />} />
        {/* Para la dueña: el panel, con usuario y contraseña */}
        <Route path="/panel/login" element={<Login />} />
        <Route path="/panel/*" element={<RequireLogin><Panel /></RequireLogin>} />
        <Route path="/login" element={<Navigate to="/panel/login" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ToastProvider>
  )
}
