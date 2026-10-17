import { useEffect, useState } from 'react'
import { api, post } from '../api.js'
import { ago } from '../format.js'
import { useToast } from './Toast.jsx'
import { t } from '../i18n/index.js'

function RequestCard({ hr, owner, assistant, onDone }) {
  const toast = useToast()
  const [text, setText] = useState('')
  const [sign, setSign] = useState(false)
  const [busy, setBusy] = useState(false)

  const reply = async () => {
    setBusy(true)
    try {
      await post(`/help-requests/${hr.id}/reply/`, { text, sign })
      toast(t('Respuesta enviada al chat de {name}', { name: hr.client_name || t('la clienta') }))
      onDone()
    } catch (e) { toast(e.message, 'error') } finally { setBusy(false) }
  }
  const close = async () => { await post(`/help-requests/${hr.id}/close/`); toast(t('Marcada como resuelta')); onDone() }
  const onKey = (e) => { if (e.key === 'Enter' && (e.metaKey || e.ctrlKey) && text.trim()) reply() }

  return (
    <div className="card help-card">
      <div className="card-head">
        <strong>{hr.client_name || t('Clienta sin nombre')}</strong>
        <span className="muted small">{hr.channel === 'telegram' ? 'Telegram' : 'Web'} · {ago(hr.created_at)}</span>
      </div>
      <div className="thread" ref={(el) => { if (el) el.scrollTop = el.scrollHeight }}>
        {hr.recent.map((m, i) => (
          <div key={i} className={`thread-line ${m.role}`}>
            <span className="who-tag">{m.role === 'user' ? t('Clienta') : m.from_owner ? t('Tú (como {assistant})', { assistant }) : assistant}</span>
            {m.text}
          </div>
        ))}
      </div>
      {hr.contact && <div className="small">{t('Teléfono')}: <strong className="selectable">{hr.contact}</strong></div>}
      <label className="label" htmlFor={`hr-${hr.id}`}>{t('Contesta en su chat')}</label>
      <textarea id={`hr-${hr.id}`} rows={3} value={text} onChange={(e) => setText(e.target.value)} onKeyDown={onKey}
        placeholder={t(hr.channel === 'telegram' ? 'Escribe como si fueras {assistant}. Le llegará en su chat de Telegram.' : 'Escribe como si fueras {assistant}. Le llegará en su chat de la web.', { assistant })} />
      <label className="check"><input type="checkbox" checked={sign} onChange={(e) => setSign(e.target.checked)} /> {t('Firmar como {owner}', { owner })}</label>
      <div className="actions">
        <button className="btn primary" disabled={busy || !text.trim()} onClick={reply}>{t('Enviar como {name}', { name: sign ? owner : assistant })}</button>
        <button className="btn ghost" onClick={close}>{t('Ya lo he resuelto')}</button>
      </div>
      {hr.channel === 'web' && <p className="muted small">{t('Si la clienta ya cerró la página no verá la respuesta: en ese caso usa su teléfono.')}</p>}
    </div>
  )
}

/** Preguntas que la recepcionista no supo contestar y esperan a la dueña. */
export default function HelpRequests({ owner = 'Cris', assistant = 'Aura', refresh = 0, onChange }) {
  const [items, setItems] = useState(null)
  const load = () => api('/help-requests/?status=open').then(setItems).catch(() => setItems([]))
  useEffect(() => { load(); const t = setInterval(load, 15000); return () => clearInterval(t) }, [refresh])
  const done = () => { load(); onChange?.() }

  if (!items) return null
  return (
    <div className="help-requests">
      <h3 className="sub">{t('Clientas esperando a {owner}', { owner })} {items.length > 0 && <span className="count">{items.length}</span>}</h3>
      {!items.length && <p className="muted">{t('Nadie esperando. Cuando {assistant} no sepa contestar algo, aparecerá aquí y te llegará un aviso al móvil.', { assistant })}</p>}
      <div className="help-grid">
        {items.map((hr) => <RequestCard key={hr.id} hr={hr} owner={owner} assistant={assistant} onDone={done} />)}
      </div>
    </div>
  )
}
