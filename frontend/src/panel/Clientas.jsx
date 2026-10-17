import { useEffect, useState } from 'react'
import { api, patch, post } from '../api.js'
import ClientFile from '../components/ClientFile.jsx'
import TelegramLink from '../components/TelegramLink.jsx'
import { useToast } from '../components/Toast.jsx'
import { shortDate } from '../format.js'
import { t } from '../i18n/index.js'

const EMPTY = { name: '', phone: '', email: '', notes: '', accepts_reminders: true }

/** Formulario de alta y de edición (son los mismos datos). */
function ClientForm({ initial = EMPTY, onSave, onCancel, saveLabel }) {
  const [form, setForm] = useState({ ...EMPTY, ...initial })
  const [busy, setBusy] = useState(false)
  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))
  const id = initial.id || 'new'

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try { await onSave(form) } finally { setBusy(false) }
  }

  return (
    <form className="client-form" onSubmit={submit}>
      <div className="form-grid">
        <div className="field"><label className="label" htmlFor={`cl-name-${id}`}>{t('Nombre y apellidos')}</label><input id={`cl-name-${id}`} required value={form.name} onChange={set('name')} /></div>
        <div className="field"><label className="label" htmlFor={`cl-phone-${id}`}>{t('Móvil')}</label><input id={`cl-phone-${id}`} inputMode="tel" value={form.phone} onChange={set('phone')} placeholder="600 000 000" /></div>
        <div className="field"><label className="label" htmlFor={`cl-email-${id}`}>{t('Correo (opcional)')}</label><input id={`cl-email-${id}`} type="email" value={form.email} onChange={set('email')} /></div>
      </div>
      <div className="field"><label className="label" htmlFor={`cl-notes-${id}`}>{t('Notas (alergias, preferencias…)')}</label><textarea id={`cl-notes-${id}`} rows={2} value={form.notes} onChange={set('notes')} /></div>
      {initial.id && (
        <label className="check"><input type="checkbox" checked={form.accepts_reminders} onChange={set('accepts_reminders')} /> {t('Quiere mensajes para repetir tratamientos')}</label>
      )}
      <div className="actions">
        <button className="btn primary" disabled={busy}>{saveLabel}</button>
        <button type="button" className="btn ghost" onClick={onCancel}>{t('Cancelar')}</button>
      </div>
    </form>
  )
}

export default function Clientas() {
  const toast = useToast()
  const [clients, setClients] = useState(null)
  const [search, setSearch] = useState('')
  const [adding, setAdding] = useState(false)
  const [editing, setEditing] = useState(null)
  const [openClient, setOpenClient] = useState(null)

  const load = () => api(`/clients/?q=${encodeURIComponent(search.trim())}`).then(setClients).catch((e) => toast(e.message, 'error'))
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t) }, [search]) // eslint-disable-line react-hooks/exhaustive-deps

  const create = async (form) => {
    try {
      const client = await post('/clients/', form)
      toast(t('{name} añadida', { name: client.name }))
      setAdding(false); load()
    } catch (e) { toast(e.message, 'error') }
  }
  const update = async (form) => {
    try {
      const client = await patch(`/clients/${form.id}/`, form)
      toast(t('Datos de {name} guardados', { name: client.name }))
      setEditing(null); load()
    } catch (e) { toast(e.message, 'error') }
  }

  return (
    <section>
      <div className="section-head">
        <div>
          <h2>{t('Clientas')}</h2>
          <p className="muted">{t('Las que reservan por la web o por Telegram aparecen solas. Aquí puedes añadir a quien te llama o viene al centro.')}</p>
        </div>
        {!adding && <button className="btn primary" onClick={() => setAdding(true)}>{t('Añadir clienta')}</button>}
      </div>

      {adding && (
        <div className="card">
          <h3>{t('Nueva clienta')}</h3>
          <ClientForm onSave={create} onCancel={() => setAdding(false)} saveLabel={t('Guardar clienta')} />
        </div>
      )}

      <div className="field search-field">
        <label className="label" htmlFor="cl-search">{t('Buscar')}</label>
        <input id="cl-search" type="search" value={search} onChange={(e) => setSearch(e.target.value)} placeholder={t('Nombre, teléfono o correo')} />
      </div>

      {clients === null && <p className="muted">{t('Cargando…')}</p>}
      {clients?.length === 0 && <p className="muted">{search ? t('No hay ninguna clienta con ese nombre o teléfono.') : t('Todavía no hay clientas.')}</p>}

      <ul className="client-list">
        {clients?.map((c) => (
          <li key={c.id} className="card">
            {editing === c.id ? (
              <ClientForm initial={c} onSave={update} onCancel={() => setEditing(null)} saveLabel={t('Guardar cambios')} />
            ) : (
              <div className="client-row">
                <div className="client-main">
                  <button className="client-link" onClick={() => setOpenClient(c.id)}>{c.name}</button>
                  <span className="muted small">
                    {c.phone ? <a href={`tel:${c.phone.replace(/\s/g, '')}`}>{c.phone}</a> : t('Sin teléfono')}
                    {c.email && <> · {c.email}</>}
                  </span>
                  {c.notes && <span className="small client-notes">{c.notes}</span>}
                </div>
                <dl className="client-stats">
                  <div><dt>{t('Visitas')}</dt><dd>{c.visits_count}</dd></div>
                  <div><dt>{t('Última')}</dt><dd>{shortDate(c.last_visit)}</dd></div>
                  <div><dt>{t('Próxima cita')}</dt><dd>{shortDate(c.next_visit)}</dd></div>
                </dl>
                <div className="client-actions">
                  {c.has_telegram ? <span className="pill ok" title={t('Le llegan los recordatorios')}>Telegram ✓</span> : <TelegramLink name={c.name} link={c.telegram_link} />}
                  <button className="btn" onClick={() => setOpenClient(c.id)}>{t('Ficha')}</button>
                  <button className="btn ghost" onClick={() => setEditing(c.id)}>{t('Editar')}</button>
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>
      {openClient && <ClientFile clientId={openClient} onClose={() => setOpenClient(null)} onChange={load} />}
    </section>
  )
}
