import { useEffect, useState } from 'react'
import { api, patch, post } from '../api.js'
import { dayLong, euros, hour, localDate } from '../format.js'
import { t } from '../i18n/index.js'
import { PACK_SALE_METHODS, paymentMethod } from './payment.js'
import { useToast } from './Toast.jsx'

const STATUS = { booked: 'Reservada', confirmed: 'Confirmada', completed: 'Completada', cancelled: 'Cancelada', no_show: 'No vino' }

/** Vender un bono: tratamiento, sesiones, precio y cómo lo paga. */
function SellPack({ client, suggestedServiceId, onSold, onCancel }) {
  const toast = useToast()
  const [services, setServices] = useState([])
  const [form, setForm] = useState({ service: '', sessions: 5, price: '', payment_method: 'tarjeta' })
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api('/services/').then((list) => {
      const active = list.filter((s) => s.active)
      setServices(active)
      // Se propone el tratamiento que más se hace (el de su última cita); si no, el primero
      const first = active.find((s) => s.id === suggestedServiceId) || active[0]
      if (first) setForm((f) => ({ ...f, service: first.id, price: String(Math.round(Number(first.price) * f.sessions * 0.8)) }))
    })
  }, [])

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))
  const chooseService = (e) => {
    const service = services.find((s) => s.id === e.target.value)
    // Precio orientativo: paga 4 sesiones de cada 5. Se puede cambiar.
    setForm((f) => ({ ...f, service: service.id, price: String(Math.round(Number(service.price) * f.sessions * 0.8)) }))
  }
  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      await post('/packs/', { ...form, client: client.id, sessions: Number(form.sessions), price: form.price.replace(',', '.') })
      toast(t('Bono vendido a {name}', { name: client.name }))
      onSold()
    } catch (err) { toast(err.message, 'error') } finally { setBusy(false) }
  }

  return (
    <form className="sell-pack" onSubmit={submit}>
      <div className="form-grid">
        <div className="field"><label className="label" htmlFor="sp-service">{t('Tratamiento')}</label>
          <select id="sp-service" value={form.service} onChange={chooseService}>{services.map((s) => <option key={s.id} value={s.id}>{s.display_name} · {euros(s.price)}</option>)}</select>
        </div>
        <div className="field"><label className="label" htmlFor="sp-sessions">{t('Sesiones')}</label><input id="sp-sessions" type="number" min={2} max={50} value={form.sessions} onChange={set('sessions')} /></div>
        <div className="field"><label className="label" htmlFor="sp-price">{t('Precio del bono (€)')}</label><input id="sp-price" inputMode="decimal" required value={form.price} onChange={set('price')} /></div>
      </div>
      <span className="label">{t('Cómo lo paga')}</span>
      <div className="pay-options" role="radiogroup" aria-label={t('Forma de pago')}>
        {PACK_SALE_METHODS.map((m) => (
          <button type="button" key={m.key} role="radio" aria-checked={form.payment_method === m.key} className="pay-option" onClick={() => setForm((f) => ({ ...f, payment_method: m.key }))}>
            <span aria-hidden="true">{m.icon}</span>{t(m.label)}
          </button>
        ))}
      </div>
      <div className="actions"><button className="btn primary" disabled={busy || !form.service}>{t('Vender bono')}</button><button type="button" className="btn ghost" onClick={onCancel}>{t('Cancelar')}</button></div>
    </form>
  )
}

/** Ficha de la clienta: notas (alergias…), bonos, historial y protección de datos. Se abre desde Citas y Clientas. */
export default function ClientFile({ clientId, onClose, onChange }) {
  const toast = useToast()
  const [data, setData] = useState(null)
  const [notes, setNotes] = useState('')
  const [selling, setSelling] = useState(false)
  const [forgetting, setForgetting] = useState(false)

  const load = () => api(`/clients/${clientId}/`).then((d) => { setData(d); setNotes(d.client.notes) }).catch((e) => toast(e.message, 'error'))
  useEffect(() => { load() }, [clientId]) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const changed = () => { load(); onChange?.() }
  const saveNotes = async () => {
    try {
      await patch(`/clients/${clientId}/`, { ...data.client, notes })
      toast(t('Notas guardadas'))
      changed()
    } catch (e) { toast(e.message, 'error') }
  }
  const forget = async () => {
    try {
      await post(`/clients/${clientId}/forget/`)
      toast(t('Datos borrados'))
      onChange?.()
      onClose()
    } catch (e) { toast(e.message, 'error'); setForgetting(false) }
  }

  const client = data?.client
  const activePacks = data?.packs.filter((p) => p.sessions_left > 0) || []
  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <aside className="sheet" role="dialog" aria-modal="true" aria-label={t('Ficha de la clienta')} onClick={(e) => e.stopPropagation()}>
        <button className="sheet-close" onClick={onClose} aria-label={t('Cerrar')}>×</button>
        {!data && <p className="muted">{t('Cargando…')}</p>}
        {client && (
          <>
            <div className="sheet-head">
              <span className="label">{t('Ficha')}</span>
              <h2>{client.name}</h2>
              <p className="muted small">
                {client.phone ? <a href={`tel:${client.phone.replace(/\s/g, '')}`}>{client.phone}</a> : t('Sin teléfono')}
                {client.email && <> · {client.email}</>} · {client.has_telegram ? 'Telegram ✓' : t('Sin Telegram')}
              </p>
            </div>

            <dl className="client-stats sheet-stats">
              <div><dt>{t('Visitas')}</dt><dd>{data.visits}</dd></div>
              <div><dt>{t('Ha gastado')}</dt><dd>{euros(data.spent)}</dd></div>
              <div><dt>{t('Bonos activos')}</dt><dd>{activePacks.length}</dd></div>
            </dl>

            <div className="field">
              <label className="label" htmlFor="cf-notes">{t('Notas: alergias, piel, preferencias…')}</label>
              <textarea id="cf-notes" rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={t('Ej.: alérgica al látex, piel sensible')} />
              {notes !== client.notes && <div className="actions"><button className="btn primary" onClick={saveNotes}>{t('Guardar notas')}</button></div>}
            </div>

            <div className="section-head"><h3>{t('Bonos')}</h3>{!selling && <button className="btn" onClick={() => setSelling(true)}>🎟️ {t('Vender bono')}</button>}</div>
            {selling && <SellPack client={client} suggestedServiceId={data.appointments[0]?.service} onSold={() => { setSelling(false); changed() }} onCancel={() => setSelling(false)} />}
            {!data.packs.length && !selling && <p className="muted small">{t('No tiene bonos.')}</p>}
            <ul className="pack-list">
              {data.packs.map((p) => (
                <li key={p.id} className={p.sessions_left ? '' : 'dim'}>
                  <span><b>{p.service_name}</b><small className="muted"> · {t('{n} sesiones', { n: p.sessions_total })} · {euros(p.price)} {paymentMethod(p.payment_method)?.icon}</small></span>
                  <span className="pack-left">{p.sessions_left ? t('Quedan {n}', { n: p.sessions_left }) : t('Gastado')}</span>
                  <span className="pack-dots" aria-hidden="true">{Array.from({ length: p.sessions_total }, (_, i) => <i key={i} className={i < p.sessions_used ? 'used' : ''} />)}</span>
                </li>
              ))}
            </ul>

            <h3 className="sub">{t('Historial')}</h3>
            {!data.appointments.length && <p className="muted small">{t('Aún no tiene citas.')}</p>}
            <ul className="history">
              {data.appointments.map((a) => {
                const method = paymentMethod(a.payment_method)
                return (
                  <li key={a.id} className={a.status === 'cancelled' || a.status === 'no_show' ? 'dim' : ''}>
                    <span className="history-date">{dayLong(a.start)} · {hour(a.start)}</span>
                    <span><b>{a.service_name}</b> <small className="muted">{t(STATUS[a.status])}</small></span>
                    <span className="history-pay">{method && <span title={t(method.label)}>{method.icon}</span>} {a.payment_method === 'bono' ? t('Bono') : euros(a.price)}</span>
                  </li>
                )
              })}
            </ul>

            <h3 className="sub">{t('Protección de datos')}</h3>
            <p className="muted small">
              {data.privacy_accepted_at
                ? t('Aceptó la política de privacidad el {date}.', { date: localDate(data.privacy_accepted_at) })
                : t('Dada de alta en el centro o por Telegram: infórmale de la política de privacidad (está en tu web).')}
            </p>
            {forgetting ? (
              <div className="confirm-inline row-actions" role="alertdialog" aria-label={t('Confirmar borrado')}>
                <span>{t('¿Borrar sus datos? No se puede deshacer.')}</span>
                <button className="btn primary" onClick={forget}>{t('Sí, borrar')}</button>
                <button className="btn ghost" onClick={() => setForgetting(false)}>{t('No')}</button>
              </div>
            ) : (
              <button className="btn ghost danger" onClick={() => setForgetting(true)}>{t('Borrar sus datos (lo ha pedido ella)')}</button>
            )}
            <p className="muted small">{t('Se borran su nombre, teléfono, correo, notas y conversaciones. Sus citas pasadas quedan sin nombre para las cuentas.')}</p>
          </>
        )}
      </aside>
    </div>
  )
}
