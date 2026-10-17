import { useEffect, useState } from 'react'
import { api, post } from '../api.js'
import ClientFile from '../components/ClientFile.jsx'
import { PAYMENT_METHODS, paymentMethod } from '../components/payment.js'
import { useToast } from '../components/Toast.jsx'
import { addDays, dayShort, euros, hour, isoDate, relDay, wall } from '../format.js'
import { plural, t } from '../i18n/index.js'

const STATUS = {
  booked: ['acc', 'Reservada'],
  confirmed: ['ok', 'Confirmada'],
  completed: ['done', 'Completada'],
  cancelled: ['bad', 'Cancelada'],
  no_show: ['warn', 'No vino'],
}
const firstName = (name) => name.split(' ')[0]

function NewAppointment({ day, onDone }) {
  const toast = useToast()
  const [services, setServices] = useState([])
  const [clients, setClients] = useState([])
  const [form, setForm] = useState({ client: '', service: '', date: day, start: '' })
  const [slots, setSlots] = useState([])

  useEffect(() => {
    api('/services/').then((s) => { setServices(s); setForm((f) => ({ ...f, service: s.find((x) => x.active)?.id || '' })) })
    api('/clients/').then(setClients)
  }, [])
  useEffect(() => {
    if (!form.service || !form.date) return
    api(`/public/availability/?service=${form.service}&date=${form.date}`, { auth: false }).then((r) => setSlots(r.slots)).catch(() => setSlots([]))
  }, [form.service, form.date])

  const set = (k) => (e) => {
    const value = e.target.value
    setForm((f) => ({ ...f, [k]: value, ...(k === 'service' || k === 'date' ? { start: '' } : {}) }))
  }

  const submit = async (e) => {
    e.preventDefault()
    try {
      let client = clients.find((c) => c.name.toLowerCase() === form.client.trim().toLowerCase())
      if (!client) client = await post('/clients/', { name: form.client.trim() })
      await post('/appointments/', { client: client.id, service: form.service, start: form.start })
      toast(t('Cita apuntada para {name}', { name: client.name }))
      onDone()
    } catch (err) { toast(err.message, 'error') }
  }

  return (
    <form className="card new-appt" onSubmit={submit}>
      <h3>{t('Apuntar cita de mostrador')}</h3>
      <div className="form-grid">
        <div className="field">
          <label className="label" htmlFor="na-client">{t('Clienta')}</label>
          <input id="na-client" list="na-clients" required value={form.client} onChange={set('client')} placeholder={t('Nombre (nueva o existente)')} />
          <datalist id="na-clients">{clients.map((c) => <option key={c.id} value={c.name} />)}</datalist>
        </div>
        <div className="field">
          <label className="label" htmlFor="na-service">{t('Servicio')}</label>
          <select id="na-service" value={form.service} onChange={set('service')}>
            {services.filter((s) => s.active).map((s) => <option key={s.id} value={s.id}>{s.display_name} · {s.duration_minutes} min</option>)}
          </select>
        </div>
        <div className="field">
          <label className="label" htmlFor="na-date">{t('Día')}</label>
          <input id="na-date" type="date" value={form.date} onChange={set('date')} />
        </div>
        <div className="field">
          <label className="label" htmlFor="na-start">{t('Hora libre')}</label>
          <select id="na-start" required value={form.start} onChange={set('start')}>
            <option value="">{slots.length ? t('Elige hora') : t('Sin huecos ese día')}</option>
            {slots.map((s) => <option key={s} value={s}>{hour(s)}</option>)}
          </select>
        </div>
      </div>
      <div className="actions"><button className="btn primary" disabled={!form.start}>{t('Guardar cita')}</button><button type="button" className="btn ghost" onClick={onDone}>{t('Cerrar')}</button></div>
    </form>
  )
}

/** Bloquear unas horas (médico, formación, vacaciones…): ni la web ni Aura darán cita ahí. */
function BlockHours({ day, onDone }) {
  const toast = useToast()
  const [form, setForm] = useState({ day, from: '16:00', to: '20:00', untilDay: '', reason: '' })
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const submit = async (e) => {
    e.preventDefault()
    try {
      await post('/blocks/', { start: `${form.day}T${form.from}`, end: `${form.untilDay || form.day}T${form.to}`, reason: form.reason })
      toast(t('Horas bloqueadas: no se podrán reservar'))
      onDone(true)
    } catch (err) { toast(err.message, 'error') }
  }
  return (
    <form className="card new-appt" onSubmit={submit}>
      <h3>{t('Bloquear horas')}</h3>
      <p className="muted small">{t('Para el médico, una formación o vacaciones. Ni la web ni Aura ofrecerán esas horas. Las citas que ya tengas no se tocan.')}</p>
      <div className="form-grid">
        <div className="field"><label className="label" htmlFor="bl-day">{t('Día')}</label><input id="bl-day" type="date" required value={form.day} onChange={set('day')} /></div>
        <div className="field"><label className="label" htmlFor="bl-from">{t('Desde')}</label><input id="bl-from" type="time" required value={form.from} onChange={set('from')} /></div>
        <div className="field"><label className="label" htmlFor="bl-to">{t('Hasta')}</label><input id="bl-to" type="time" required value={form.to} onChange={set('to')} /></div>
        <div className="field"><label className="label" htmlFor="bl-until">{t('Hasta el día (opcional)')}</label><input id="bl-until" type="date" min={form.day} value={form.untilDay} onChange={set('untilDay')} /></div>
      </div>
      <div className="field"><label className="label" htmlFor="bl-reason">{t('Motivo (solo lo ves tú)')}</label><input id="bl-reason" value={form.reason} onChange={set('reason')} placeholder={t('Ej.: médico, formación, vacaciones')} /></div>
      <div className="actions"><button className="btn primary">{t('Bloquear')}</button><button type="button" className="btn ghost" onClick={() => onDone(false)}>{t('Cerrar')}</button></div>
    </form>
  )
}

/** Caja del día: cómo ha pagado cada clienta y, si quiere, el cierre (contar el efectivo del cajón). */
function CashSheet({ onClose }) {
  const toast = useToast()
  const [cash, setCash] = useState(null)
  const [closingForm, setClosingForm] = useState(false)
  const [counted, setCounted] = useState('')
  const [notes, setNotes] = useState('')
  useEffect(() => { api('/cash/').then(setCash).catch(() => {}) }, [])
  useEffect(() => {
    const onKey = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const close = async (e) => {
    e.preventDefault()
    try {
      const r = await post('/cash/', { day: cash.day, counted_cash: counted.replace(',', '.') || '0', notes })
      const diff = Number(r.closing.difference)
      toast(diff === 0 ? t('Caja cerrada: cuadra') : t(diff > 0 ? 'Caja cerrada: sobran {amount}' : 'Caja cerrada: faltan {amount}', { amount: euros(Math.abs(diff)) }))
      setCash(r)
    } catch (err) { toast(err.message, 'error') }
  }

  const methods = [['💶', 'Efectivo', cash?.cash], ['💳', 'Tarjeta', cash?.card], ['📱', 'Bizum', cash?.bizum]]
  const closing = cash?.closing
  const diff = closing ? Number(closing.difference) : 0
  return (
    <div className="sheet-backdrop" onClick={onClose}>
      <aside className="sheet" role="dialog" aria-modal="true" aria-label={t('Caja del día')} onClick={(e) => e.stopPropagation()}>
        <button className="sheet-close" onClick={onClose} aria-label={t('Cerrar')}>×</button>
        {!cash ? <p className="muted">{t('Cargando…')}</p> : (
          <section className="cash">
            <div className="sheet-head"><span className="label">{t('Hoy')}</span><h2>{t('Caja del día')}</h2></div>
            <div className="card-head"><span className="muted">{t('Total cobrado')}</span><b className="cash-total">{euros(cash.total)}</b></div>
            <ul className="cash-methods">
              {methods.map(([icon, label, amount]) => <li key={label}><span className="cash-icon" aria-hidden="true">{icon}</span><span>{t(label)}</span><b>{euros(amount)}</b></li>)}
            </ul>
            {!cash.charges.length && <p className="muted">{t('Todavía no has cobrado nada hoy.')}</p>}
            {cash.charges.length > 0 && (
              <ul className="charges" aria-label={t('Cobros de hoy')}>
                {cash.charges.map((c, i) => {
                  const m = paymentMethod(c.payment_method)
                  return (
                    <li key={i}>
                      <span className="mono muted">{hour(c.time)}</span>
                      <span className="charge-who"><b>{c.client_name}</b><small className="muted">{c.concept}</small></span>
                      <span className={`charge-method ${c.payment_method}`}><span aria-hidden="true">{m?.icon}</span>{t(m?.label || '')}</span>
                      <b className="charge-amount">{c.payment_method === 'bono' ? '—' : euros(c.amount)}</b>
                    </li>
                  )
                })}
              </ul>
            )}
            <p className="muted small">
              {plural(cash.appointments, '{n} cita cobrada', '{n} citas cobradas')}
              {cash.sessions_with_pack > 0 && <> · 🎟️ {t('{n} con bono (ya pagado)', { n: cash.sessions_with_pack })}</>}
              {cash.packs_sold > 0 && <> · {plural(cash.packs_sold, '{n} bono vendido', '{n} bonos vendidos')}</>}
            </p>
            {closing ? (
              <p className={`cash-closed ${diff === 0 ? 'ok' : 'off'}`}>
                ✓ {t('Cerrada a las {time}: contaste {amount} en efectivo.', { time: hour(closing.closed_at), amount: euros(closing.counted_cash) })}{' '}
                {diff === 0 ? t('Cuadra.') : t(diff > 0 ? 'Sobran {amount}.' : 'Faltan {amount}.', { amount: euros(Math.abs(diff)) })}
                {closing.notes && <span className="muted"> ({closing.notes})</span>}
              </p>
            ) : !closingForm ? (
              <button className="btn" onClick={() => setClosingForm(true)}>{t('Contar el cajón y cerrar caja')}</button>
            ) : (
              <form className="cash-close" onSubmit={close}>
                <div className="field"><label className="label" htmlFor="cash-counted">{t('Efectivo contado en el cajón (€)')}</label><input id="cash-counted" inputMode="decimal" required value={counted} onChange={(e) => setCounted(e.target.value)} placeholder={Number(cash.cash).toFixed(2)} /></div>
                <div className="field"><label className="label" htmlFor="cash-notes">{t('Nota (opcional)')}</label><input id="cash-notes" value={notes} onChange={(e) => setNotes(e.target.value)} placeholder={t('Ej.: cambio para mañana')} /></div>
                <button className="btn primary">{t('Cerrar caja')}</button>
              </form>
            )}
          </section>
        )}
      </aside>
    </div>
  )
}

/** Menú "⋯" de cada cita: lo que se usa poco va aquí para que la fila tenga un solo botón. */
function MoreMenu({ appointment: a, open, onToggle, onFile, onAsk, onCopyTelegram }) {
  const active = a.status === 'booked' || a.status === 'confirmed'
  return (
    <div className="more">
      <button className="btn ghost more-button" aria-haspopup="menu" aria-expanded={open} aria-label={t('Más opciones de la cita de {name}', { name: a.client_name })} onClick={(e) => { e.stopPropagation(); onToggle() }}>⋯</button>
      {open && (
        <div className="more-menu" role="menu" onClick={(e) => e.stopPropagation()}>
          <button role="menuitem" onClick={onFile}>{t('Ver ficha de {name}', { name: firstName(a.client_name) })}</button>
          {active && <button role="menuitem" onClick={() => onAsk('no-show')}>{t('No ha venido')}</button>}
          {active && <button role="menuitem" className="danger" onClick={() => onAsk('cancel')}>{t('Cancelar cita')}</button>}
          {!a.client_has_telegram && a.client_telegram_link && (
            <button role="menuitem" className="separated" onClick={onCopyTelegram}>{t('Copiar enlace de Telegram')}</button>
          )}
        </div>
      )}
    </div>
  )
}

export default function Citas({ onChange }) {
  const toast = useToast()
  const today = new Date()
  const days = Array.from({ length: 7 }, (_, i) => addDays(today, i))
  const [items, setItems] = useState([])
  const [blocks, setBlocks] = useState([])
  const [day, setDay] = useState(isoDate(today))
  const [panel, setPanel] = useState(null) // 'new' | 'block'
  const [cashOpen, setCashOpen] = useState(false)
  const [openClient, setOpenClient] = useState(null)
  const [menu, setMenu] = useState(null)
  const [confirming, setConfirming] = useState(null)
  const from = isoDate(today)
  const to = isoDate(addDays(today, 6))

  const load = () => {
    api(`/appointments/?from=${from}&to=${to}`).then(setItems)
    api(`/blocks/?start=${from}&end=${to}`).then(setBlocks).catch(() => setBlocks([]))
  }
  useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    const close = () => setMenu(null)
    window.addEventListener('click', close)
    return () => window.removeEventListener('click', close)
  }, [])
  const changed = () => { load(); onChange() }

  const act = async (a, what) => {
    setConfirming(null)
    try {
      await post(`/appointments/${a.id}/${what}/`)
      toast(what === 'cancel' ? t('Cita cancelada') : t('Marcada como no presentada'))
      changed()
    } catch (e) { toast(e.message, 'error') }
  }
  const undo = async (a) => {
    try {
      await post(`/appointments/${a.id}/undo-complete/`)
      toast(t('{name}: vuelve a estar pendiente', { name: firstName(a.client_name) }))
      changed()
    } catch (e) { toast(e.message, 'error') }
  }
  const charge = async (a, method) => {
    setConfirming(null)
    try {
      await post(`/appointments/${a.id}/complete/`, { payment_method: method.key })
      const paid = method.key === 'bono' ? t('sesión de bono') : euros(a.price)
      toast(`${method.icon} ${t('{name} cobrada', { name: firstName(a.client_name) })} · ${paid}`, 'info', { label: t('Deshacer'), onClick: () => undo(a) })
      changed()
    } catch (e) { toast(e.message, 'error') }
  }
  // Enlace para que la clienta active Telegram (se lo mandas por WhatsApp o SMS)
  const copyTelegram = async (a) => {
    try {
      await navigator.clipboard.writeText(a.client_telegram_link)
      toast(t('Enlace copiado. Mándaselo a {name} para que lo abra en Telegram.', { name: firstName(a.client_name) }))
    } catch { toast(t('Copia este enlace: {link}', { link: a.client_telegram_link })) }
  }
  const removeBlock = async (block) => {
    await api(`/blocks/${block.id}/`, { method: 'DELETE' })
    toast(t('Bloqueo quitado: esas horas vuelven a estar libres'))
    load()
  }

  const onDay = (iso) => items.filter((a) => isoDate(wall(a.start)) === iso)
  // Parte de cada bloqueo que cae en ese día (un bloqueo puede durar varios días)
  const blocksOn = (iso) => blocks.flatMap((b) => {
    const dayStart = wall(iso)
    const dayEnd = addDays(dayStart, 1)
    const start = wall(b.start); const end = wall(b.end)
    if (end <= dayStart || start >= dayEnd) return []
    return [{ ...b, from: start < dayStart ? '00:00' : hour(start), to: end > dayEnd ? '24:00' : hour(end) }]
  })

  const list = onDay(day)
  const dayBlocks = blocksOn(day)
  const pending = list.filter((a) => a.status === 'booked' || a.status === 'confirmed').length
  const closed = wall(day).getDay() === 0
  const summary = closed ? t('Cerrado') : !list.length ? t('Sin citas')
    : `${plural(list.length, '{n} cita', '{n} citas')}${pending && pending !== list.length ? ` · ${t('faltan {n}', { n: pending })}` : ''}`

  return (
    <section>
      <div className="agenda-head">
        <div>
          <h2>{relDay(day)}</h2>
          <p className="muted">{summary}</p>
        </div>
        <div className="head-actions">
          <button className="btn" onClick={() => setCashOpen(true)}>💶 {t('Caja del día')}</button>
          <button className="btn" onClick={() => setPanel(panel === 'block' ? null : 'block')}>{t('Bloquear horas')}</button>
          <button className="btn primary" onClick={() => setPanel(panel === 'new' ? null : 'new')}>{t('Apuntar cita')}</button>
        </div>
      </div>

      <div className="day-picker" role="tablist" aria-label={t('Día')}>
        {days.map((d) => {
          const iso = isoDate(d)
          const count = onDay(iso).length
          return (
            <button key={iso} role="tab" aria-selected={day === iso} className="day-chip" onClick={() => { setDay(iso); setConfirming(null) }}>
              <span>{iso === from ? t('Hoy') : dayShort(d)}</span>
              <small>{d.getDay() === 0 ? t('cerrado') : count ? plural(count, '{n} cita', '{n} citas') : '—'}</small>
            </button>
          )
        })}
      </div>

      {panel === 'new' && <NewAppointment day={day} onDone={() => { setPanel(null); changed() }} />}
      {panel === 'block' && <BlockHours day={day} onDone={(saved) => { setPanel(null); if (saved) load() }} />}

      <div className="day">
        {!closed && !list.length && !dayBlocks.length && <div className="empty">{t('No hay citas este día.')}</div>}
        {closed && !list.length && <div className="empty">{t('Los domingos el centro está cerrado.')}</div>}
        {dayBlocks.map((b) => (
          <div className="row blocked" key={b.id}>
            <span className="mono">{b.from}</span>
            <div className="who"><strong>{t('Bloqueado hasta las {time}', { time: b.to })}</strong><span className="muted">{b.reason || t('Sin motivo')} · {t('no se puede reservar')}</span></div>
            <div className="row-actions"><button className="btn ghost" onClick={() => removeBlock(b)}>{t('Quitar')}</button></div>
          </div>
        ))}
        {list.map((a) => {
          const active = a.status === 'booked' || a.status === 'confirmed'
          const paid = paymentMethod(a.payment_method)
          const first = firstName(a.client_name)
          const asking = confirming?.id === a.id ? confirming.what : null
          return (
            <div className={`row ${active ? '' : 'dim'}`} key={a.id}>
              <span className="mono">{hour(a.start)}</span>
              <div className="who">
                <button className="client-link" onClick={() => setOpenClient(a.client)}>{a.client_name}</button>
                <span className="muted">{a.service_name} · {a.duration_minutes} min · {euros(a.price)}{a.client_has_pack && active && <> · <span className="pack-hint">🎟️ {t('tiene bono')}</span></>}</span>
              </div>
              {asking === 'pay' ? (
                <div className="row-actions pay-inline" role="group" aria-label={t('Cómo ha pagado {name}', { name: first })}>
                  <span>{t('¿Cómo paga?')}</span>
                  {PAYMENT_METHODS.filter((m) => m.key !== 'bono' || a.client_has_pack).map((m) => (
                    <button key={m.key} className="pay-option" onClick={() => charge(a, m)}><span aria-hidden="true">{m.icon}</span>{t(m.label)}</button>
                  ))}
                  <button className="btn ghost" onClick={() => setConfirming(null)}>{t('Volver')}</button>
                </div>
              ) : asking ? (
                <div className="row-actions confirm-inline" role="alertdialog" aria-label={t('Confirmar')}>
                  <span>{asking === 'cancel' ? t('¿Cancelar la cita de {name}?', { name: first }) : t('¿{name} no ha venido?', { name: first })}</span>
                  <button className="btn primary" onClick={() => act(a, asking)}>{asking === 'cancel' ? t('Sí, cancelar') : t('Sí, no vino')}</button>
                  <button className="btn ghost" onClick={() => setConfirming(null)}>{t('No')}</button>
                </div>
              ) : (
                <div className="row-actions">
                  {paid && <span className={`paid-tag ${a.payment_method}`} title={t('Pagado con: {method}', { method: t(paid.label) })}><span aria-hidden="true">{paid.icon}</span>{t(paid.label)}{a.payment_method !== 'bono' && <> · {euros(a.price)}</>}</span>}
                  {!paid && !active && <span className={`pill ${STATUS[a.status][0]}`}>{t(STATUS[a.status][1])}</span>}
                  {active && <button className="btn primary" onClick={() => setConfirming({ id: a.id, what: 'pay' })}>{t('Cobrar')}</button>}
                  <MoreMenu
                    appointment={a}
                    open={menu === a.id}
                    onToggle={() => setMenu(menu === a.id ? null : a.id)}
                    onFile={() => { setMenu(null); setOpenClient(a.client) }}
                    onAsk={(what) => { setMenu(null); setConfirming({ id: a.id, what }) }}
                    onCopyTelegram={() => { setMenu(null); copyTelegram(a) }}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
      {pending > 0 && <p className="muted small hint">{t('Pulsa Cobrar cuando termine la cita. Si te equivocas, sale un Deshacer unos segundos.')}</p>}
      {cashOpen && <CashSheet onClose={() => setCashOpen(false)} />}
      {openClient && <ClientFile clientId={openClient} onClose={() => setOpenClient(null)} onChange={load} />}
    </section>
  )
}
