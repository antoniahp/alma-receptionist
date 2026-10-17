import { useEffect, useState } from 'react'
import { api, patch, post } from '../api.js'
import { useToast } from '../components/Toast.jsx'
import { euros } from '../format.js'
import { t } from '../i18n/index.js'

const CATEGORIES = [
  ['facial', 'Facial'],
  ['manos_pies', 'Manos y pies'],
  ['depilacion', 'Depilación'],
  ['cejas_pestanas', 'Cejas y pestañas'],
  ['maquillaje', 'Maquillaje'],
]
const EMPTY = { name: '', category: 'facial', description: '', name_en: '', description_en: '', price: '', duration_minutes: 60, repeat_every_days: '', active: true }

function ServiceForm({ initial = EMPTY, onSave, onCancel, saveLabel }) {
  const [form, setForm] = useState({ ...EMPTY, ...initial, price: String(initial.price ?? '').replace('.', ','), repeat_every_days: initial.repeat_every_days ?? '' })
  const [busy, setBusy] = useState(false)
  const id = initial.id || 'new'
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.type === 'checkbox' ? e.target.checked : e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      await onSave({
        ...form,
        price: form.price.replace(',', '.'),
        duration_minutes: Number(form.duration_minutes),
        repeat_every_days: form.repeat_every_days === '' ? null : Number(form.repeat_every_days),
      })
    } finally { setBusy(false) }
  }

  return (
    <form className="service-form" onSubmit={submit}>
      <div className="form-grid">
        <div className="field"><label className="label" htmlFor={`sv-name-${id}`}>{t('Nombre')}</label><input id={`sv-name-${id}`} required value={form.name} onChange={set('name')} /></div>
        <div className="field"><label className="label" htmlFor={`sv-cat-${id}`}>{t('Categoría')}</label>
          <select id={`sv-cat-${id}`} value={form.category} onChange={set('category')}>{CATEGORIES.map(([v, l]) => <option key={v} value={v}>{t(l)}</option>)}</select>
        </div>
        <div className="field"><label className="label" htmlFor={`sv-price-${id}`}>{t('Precio (€)')}</label><input id={`sv-price-${id}`} inputMode="decimal" required value={form.price} onChange={set('price')} /></div>
        <div className="field"><label className="label" htmlFor={`sv-min-${id}`}>{t('Duración (min)')}</label><input id={`sv-min-${id}`} type="number" min={10} max={480} step={5} required value={form.duration_minutes} onChange={set('duration_minutes')} /></div>
        <div className="field"><label className="label" htmlFor={`sv-rep-${id}`}>{t('Repetir cada (días)')}</label><input id={`sv-rep-${id}`} type="number" min={1} max={365} value={form.repeat_every_days} onChange={set('repeat_every_days')} placeholder={t('Vacío = no se avisa')} /></div>
      </div>
      <div className="field"><label className="label" htmlFor={`sv-desc-${id}`}>{t('Descripción (sale en la web y Aura la usa para recomendar)')}</label><textarea id={`sv-desc-${id}`} rows={2} value={form.description} onChange={set('description')} /></div>
      <details className="translation">
        <summary>{t('Texto en inglés para la web (opcional)')}</summary>
        <div className="field"><label className="label" htmlFor={`sv-name-en-${id}`}>{t('Nombre en inglés')}</label><input id={`sv-name-en-${id}`} value={form.name_en} onChange={set('name_en')} /></div>
        <div className="field"><label className="label" htmlFor={`sv-desc-en-${id}`}>{t('Descripción en inglés')}</label><textarea id={`sv-desc-en-${id}`} rows={2} value={form.description_en} onChange={set('description_en')} /></div>
      </details>
      {initial.id && <label className="check"><input type="checkbox" checked={form.active} onChange={set('active')} /> {t('Se puede reservar (si lo quitas, desaparece de la web)')}</label>}
      <div className="actions"><button className="btn primary" disabled={busy}>{saveLabel}</button><button type="button" className="btn ghost" onClick={onCancel}>{t('Cancelar')}</button></div>
    </form>
  )
}

/** Tratamientos y precios: lo que sale en la web y lo que ofrece Aura. */
export default function Tratamientos() {
  const toast = useToast()
  const [services, setServices] = useState(null)
  const [adding, setAdding] = useState(false)
  const [editing, setEditing] = useState(null)

  const load = () => api('/services/').then(setServices).catch((e) => toast(e.message, 'error'))
  useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const create = async (form) => {
    try {
      const s = await post('/services/', form)
      toast(t('{name} añadido a la web', { name: s.name }))
      setAdding(false); load()
    } catch (e) { toast(e.message, 'error') }
  }
  const update = async (form) => {
    try {
      const s = await patch(`/services/${form.id}/`, form)
      toast(t(s.active ? '{name} guardado' : '{name} ya no se puede reservar', { name: s.name }))
      setEditing(null); load()
    } catch (e) { toast(e.message, 'error') }
  }

  return (
    <section>
      <div className="section-head">
        <div>
          <h2>{t('Tratamientos')}</h2>
          <p className="muted">{t('Lo que cambies aquí sale al momento en tu web y en lo que ofrece Aura. Las citas ya reservadas mantienen su precio.')}</p>
        </div>
        {!adding && <button className="btn primary" onClick={() => setAdding(true)}>{t('Añadir tratamiento')}</button>}
      </div>

      {adding && <div className="card"><h3>{t('Nuevo tratamiento')}</h3><ServiceForm onSave={create} onCancel={() => setAdding(false)} saveLabel={t('Añadir')} /></div>}
      {services === null && <p className="muted">{t('Cargando…')}</p>}

      {CATEGORIES.map(([key, label]) => {
        const list = services?.filter((s) => s.category === key) || []
        if (!list.length) return null
        return (
          <div key={key}>
            <h3 className="sub">{t(label)}</h3>
            <ul className="service-list">
              {list.map((s) => (
                <li key={s.id} className={`card ${s.active ? '' : 'dim'}`}>
                  {editing === s.id ? (
                    <ServiceForm initial={s} onSave={update} onCancel={() => setEditing(null)} saveLabel={t('Guardar')} />
                  ) : (
                    <div className="service-row">
                      <div>
                        <strong>{s.display_name}</strong>{!s.active && <span className="pill done">{t('No se reserva')}</span>}
                        <span className="muted small">{s.duration_minutes} min{s.repeat_every_days ? ` · ${t('se avisa para repetir a los {n} días', { n: s.repeat_every_days })}` : ''}</span>
                      </div>
                      <b className="service-price">{euros(s.price)}</b>
                      <button className="btn ghost" onClick={() => setEditing(s.id)}>{t('Editar')}</button>
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )
      })}
    </section>
  )
}
