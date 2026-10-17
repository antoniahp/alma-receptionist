import { useEffect, useState } from 'react'
import { api } from '../api.js'
import HelpRequests from '../components/HelpRequests.jsx'
import usePushAlerts from '../components/usePushAlerts.js'
import { ago } from '../format.js'
import { t } from '../i18n/index.js'

/** Botón para recibir avisos emergentes en este navegador (como los de cualquier app), aunque el panel esté cerrado. */
function PushButton({ push }) {
  if (push.state === 'on') return <button className="btn ghost" disabled={push.busy} onClick={push.disable} title={t('Te llegan avisos en este navegador aunque tengas el panel cerrado')}>🔔 {t('Avisos activados')}</button>
  if (push.state === 'off') return <span className="push-off"><button className="btn primary" disabled={push.busy} onClick={push.enable}>🔔 {t('Activar avisos')}</button>{push.problem && <small className="bad-text">{push.problem}</small>}</span>
  if (push.state === 'denied') return <span className="muted small">{t('Los avisos están bloqueados en este navegador: actívalos en el candado de la barra de direcciones.')}</span>
  if (push.state === 'not-configured') return <span className="muted small">{t('Para recibir avisos falta configurar las claves VAPID en el servidor.')}</span>
  if (push.state === 'unsupported') return <span className="muted small">{t('Este navegador no admite avisos. En iPhone, primero añade la web a la pantalla de inicio y ábrela desde ahí.')}</span>
  if (push.state === 'error') return <span className="muted small bad-text">{t('No se pueden comprobar los avisos')}: {push.problem}</span>
  return null
}

/** Conversaciones recientes, recogidas: solo el nombre (si lo dio), por dónde escribió y cuándo.
 * Al pulsar una se ve lo que hablaron. */
function Conversations({ convs, assistant }) {
  const [shown, setShown] = useState(false)
  const [open, setOpen] = useState(null)
  if (!convs.length) return <p className="muted small conv-toggle">{t('Aún no ha escrito ninguna clienta.')}</p>
  return (
    <div className="conversations">
      <button className="btn ghost conv-toggle" aria-expanded={shown} onClick={() => setShown((v) => !v)}>
        💬 {shown ? t('Ocultar conversaciones') : t('Ver conversaciones recientes ({n})', { n: convs.length })}
      </button>
      {shown && (
        <ul className="conv-list">
          {convs.map((c) => (
            <li key={c.key}>
              <button className="conv-row" aria-expanded={open === c.key} onClick={() => setOpen(open === c.key ? null : c.key)}>
                <b>{c.client || t('Clienta sin nombre')}</b>
                <span className="muted small">{c.channel === 'telegram' ? 'Telegram' : t('Web')} · {ago(c.updated_at)}</span>
                <span className="conv-chevron" aria-hidden="true">{open === c.key ? '−' : '+'}</span>
              </button>
              {open === c.key && (
                <div className="conv-body">
                  {c.messages.map((m, i) => (
                    <div key={i} className={`conv-line ${m.role}`}><span className="muted small">{m.role === 'user' ? t('Clienta') : m.from_owner ? t('Tú (como {assistant})', { assistant }) : assistant}</span> {m.text}</div>
                  ))}
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

/** Lo que las clientas han hablado con la recepcionista, y las preguntas que te ha pasado a ti. */
export default function Mensajes({ status, onChange }) {
  const [convs, setConvs] = useState([])
  const [tick, setTick] = useState(0)
  const load = () => api('/conversations/').then(setConvs).catch(() => {})
  // Cada vez que se refresca la lista, también el contador de la pestaña
  useEffect(() => {
    load(); onChange?.()
    const timer = setInterval(() => { load(); setTick((n) => n + 1); onChange?.() }, 10000)
    return () => clearInterval(timer)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const name = status?.business?.assistant_name || 'Aura'
  const push = usePushAlerts()
  return (
    <section>
      <div className="section-head">
        <h2>{t('Mensajes')}</h2>
        <PushButton push={push} />
      </div>
      <p className="muted">
        {t('{name} contesta sola a las clientas en tu web y en Telegram. Cuando no sabe algo, la pregunta aparece aquí y te llega un aviso a Telegram. Tu respuesta le llega a la clienta en su chat.', { name })}
      </p>
      <p className="note">{t('¿Quieres ver cómo habla {name}?', { name })} <a href="/#aura" target="_blank" rel="noreferrer">{t('Abre tu web y escríbele como si fueras una clienta.')}</a></p>

      <HelpRequests owner={status?.business?.owner} assistant={name} refresh={tick} onChange={onChange} />

      <Conversations convs={convs} assistant={name} />
    </section>
  )
}
