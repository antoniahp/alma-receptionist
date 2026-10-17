import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, post, setToken } from '../api.js'
import Logo from '../components/Logo.jsx'
import LangSwitch from '../i18n/LangSwitch.jsx'
import { t } from '../i18n/index.js'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [businessName, setBusinessName] = useState('')
  const [demo, setDemo] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    api('/public/info/', { auth: false }).then((info) => { setBusinessName(info.name); setDemo(info.demo_login) }).catch(() => {})
  }, [])

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      const r = await post('/auth/login/', { username, password }, { auth: false })
      setToken(r.token)
      navigate('/panel')
    } catch {
      setError(t('Usuario o contraseña incorrectos.'))
    }
  }

  return (
    <div className="login">
      <form className="card login-card" onSubmit={submit}>
        <Logo className="logo-login" />
        <div className="label">{t('Panel del centro')}</div>
        <h1>{businessName || t('Panel')}</h1>
        <div className="field">
          <label className="label" htmlFor="login-user">{t('Usuario')}</label>
          <input id="login-user" value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        </div>
        <div className="field">
          <label className="label" htmlFor="login-pass">{t('Contraseña')}</label>
          <input id="login-pass" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" />
        </div>
        {demo && (
          <div className="demo-login">
            <b>{t('Demo pública')}</b>
            <span>{t('Usuario')}: <code>{demo.username}</code> · {t('Contraseña')}: <code>{demo.password}</code></span>
            <button type="button" className="btn wide" onClick={() => { setUsername(demo.username); setPassword(demo.password) }}>{t('Rellenar con el usuario de prueba')}</button>
          </div>
        )}
        {error && <p className="error">{error}</p>}
        <button className="btn primary wide">{t('Entrar')}</button>
        <LangSwitch className="login-lang" />
      </form>
    </div>
  )
}
