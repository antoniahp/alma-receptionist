import { useEffect, useRef, useState } from 'react'
import { api, post } from '../api.js'
import { t } from '../i18n/index.js'

// La conversación se recuerda en este navegador: si la clienta ya dio su móvil, Aura la reconoce al volver
const SESSION_KEY = 'aura_session'
const savedSession = () => { try { return localStorage.getItem(SESSION_KEY) } catch { return null } }
const saveSession = (value) => { try { localStorage.setItem(SESSION_KEY, value) } catch { /* sin almacenamiento */ } }

/** Chat con la recepcionista (el mismo cerebro que el bot de Telegram). */
export default function ChatBox({ title, subtitle, onActivity, compact = false }) {
  const [session, setSession] = useState(savedSession)
  const [log, setLog] = useState([])
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const lastId = useRef(null)
  const logRef = useRef(null)
  const started = useRef(false)

  const send = async (payload, mine) => {
    if (mine) setLog((l) => [...l.map((m) => ({ ...m, buttons: [] })), { who: 'me', text: mine }])
    setBusy(true)
    try {
      const r = await post('/public/chat/', { session, ...payload }, { auth: false })
      setSession(r.session)
      saveSession(r.session)
      if (r.last_id) lastId.current = r.last_id
      setLog((l) => [...l.map((m) => ({ ...m, buttons: [] })), { who: 'bot', text: r.text, buttons: r.buttons, ai: r.by_ai }])
      if (onActivity) onActivity()
    } catch (e) {
      setLog((l) => [...l, { who: 'bot', text: t('Uy, se me ha cortado la conexión. ¿Me lo repites en un momento?') }])
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    if (started.current) return
    started.current = true
    send({ start: true })
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { if (logRef.current) logRef.current.scrollTop = logRef.current.scrollHeight }, [log, busy])

  // Mensajes que la dueña contesta desde el panel o Telegram: aparecen en el chat como uno más
  useEffect(() => {
    if (!session) return
    const t = setInterval(async () => {
      try {
        const after = lastId.current ? `&after=${lastId.current}` : ''
        const news = await api(`/public/chat/updates/?session=${session}${after}`, { auth: false })
        if (news.length) {
          lastId.current = news[news.length - 1].id
          setLog((l) => [...l, ...news.map((m) => ({ who: 'bot', text: m.text }))])
        }
      } catch { /* sin conexión: reintenta en el siguiente ciclo */ }
    }, 4000)
    return () => clearInterval(t)
  }, [session])

  const submit = (e) => {
    e.preventDefault()
    const v = text.trim()
    if (!v || busy) return
    setText('')
    send({ message: v }, v)
  }

  // Empezar de nuevo limpia la pantalla pero sigue siendo la misma clienta
  const restart = () => { setLog([]); send({ start: true }) }

  return (
    <div className={`chat ${compact ? 'compact' : ''}`}>
      <div className="chat-head">
        <div className="chat-who">
          <span className="avatar" aria-hidden="true"><img src="/logo.png" alt="" /></span>
          <div><strong>{title}</strong><div className="muted small">{subtitle}</div></div>
        </div>
        <button className="btn ghost chat-restart" onClick={restart} aria-label={t('Empezar de nuevo')}><span aria-hidden="true">↺</span><span className="restart-label">{t('Empezar de nuevo')}</span></button>
      </div>
      <div className="chat-log" ref={logRef}>
        {log.map((m, i) => (
          <div key={i} className="chat-turn">
            <div className={`bubble ${m.who}`}>{m.text}</div>
            {m.buttons?.length > 0 && (
              <div className="quick">
                {m.buttons.flat().map((b) => (
                  <button key={b.data} className="chip" disabled={busy} onClick={() => send({ button: b.data }, b.label)}>{b.label}</button>
                ))}
              </div>
            )}
          </div>
        ))}
        {busy && <div className="bubble bot typing" aria-label={t('Escribiendo')}><span /><span /><span /></div>}
      </div>
      <form onSubmit={submit}>
        <input id="chat-input" value={text} onChange={(e) => setText(e.target.value)} placeholder={t('Escribe un mensaje…')} aria-label={t('Mensaje')} autoComplete="off" />
        <button className="btn primary" disabled={busy || !text.trim()}>{t('Enviar')}</button>
      </form>
    </div>
  )
}
