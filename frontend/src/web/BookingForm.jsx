import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, post } from '../api.js'
import { addDays, dayLong, dayShort, euros, hour, isoDate } from '../format.js'
import { t } from '../i18n/index.js'

/** Formulario de reserva de la web del centro. El tratamiento elegido puede venir de fuera (tarjetas de tratamientos). */
export default function BookingForm({ info, service, onServiceChange }) {
  const [day, setDay] = useState(isoDate(new Date()))
  const [slots, setSlots] = useState(null)
  const [start, setStart] = useState(null)
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [privacy, setPrivacy] = useState(false)
  const [error, setError] = useState('')
  const [done, setDone] = useState(null)
  // Mientras la clienta no elija día, saltamos solas al primer día con horas libres
  const [dayChosen, setDayChosen] = useState(false)

  const days = Array.from({ length: 14 }, (_, i) => addDays(new Date(), i)).filter((d) => d.getDay() !== 0)

  const loadSlots = () => {
    if (!service) return
    setSlots(null); setStart(null)
    api(`/public/availability/?service=${service}&date=${day}`, { auth: false })
      .then((r) => {
        const next = days.find((d) => isoDate(d) > day)
        if (!r.slots.length && !dayChosen && next) setDay(isoDate(next))
        else setSlots(r.slots)
      })
      .catch(() => setSlots([]))
  }
  useEffect(loadSlots, [service, day]) // eslint-disable-line react-hooks/exhaustive-deps

  const chooseDay = (d) => { setDayChosen(true); setDay(isoDate(d)) }
  const svc = info.services.find((s) => s.id === service)
  const category = svc?.category
  // Al cambiar de categoría se elige su primer tratamiento
  const chooseCategory = (key) => onServiceChange(info.services.find((s) => s.category === key)?.id)

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    try {
      setDone(await post('/public/book/', { service, start, name, phone, privacy_accepted: privacy }, { auth: false }))
    } catch (err) {
      setError(err.message)
      loadSlots()
    }
  }

  const again = () => { setDone(null); setStart(null); setDayChosen(false); setDay(isoDate(new Date())) }

  if (done) {
    return (
      <div className="booking confirm">
        <h2>{t('¡Te esperamos, {name}!', { name: done.client_name })}</h2>
        <p><strong>{done.service}</strong><br /><span className="mono">{dayLong(done.start)} · {hour(done.start)}</span></p>
        {done.telegram_link ? (
          <>
            <p>{t('¿Te avisamos el día antes? Abre este enlace en Telegram y pulsa Iniciar. Desde ahí también podrás confirmar o cambiar la cita.')}</p>
            <a className="btn primary wide" href={done.telegram_link} target="_blank" rel="noreferrer">{t('Recibir avisos por Telegram')}</a>
          </>
        ) : (
          <p className="muted">{t('Si te surge algo, llámanos al {phone}.', { phone: info.phone })}</p>
        )}
        <button className="btn ghost wide" onClick={again}>{t('Hacer otra reserva')}</button>
      </div>
    )
  }

  return (
    <form className="booking" onSubmit={submit}>
      <h3 className="step">1. {t('Tratamiento')}</h3>
      <div className="category-tabs" role="tablist" aria-label={t('Categorías')}>
        {info.categories.map((c) => (
          <button type="button" key={c.key} role="tab" aria-selected={category === c.key} className="category-tab" onClick={() => chooseCategory(c.key)}>{t(c.label)}</button>
        ))}
      </div>
      <div className="svc">
        {info.services.filter((s) => s.category === category).map((s) => (
          <button type="button" key={s.id} className="chip" aria-pressed={service === s.id} onClick={() => onServiceChange(s.id)}>
            {s.name}<small>{s.duration_minutes} min, {euros(s.price)}</small>
          </button>
        ))}
      </div>
      {svc?.description && <p className="muted small">{svc.description}</p>}

      <h3 className="step">2. {t('Día')}</h3>
      <div className="days">
        {days.map((d) => (
          <button type="button" key={isoDate(d)} className="chip" aria-pressed={day === isoDate(d)} onClick={() => chooseDay(d)}>{dayShort(d)}</button>
        ))}
      </div>

      <h3 className="step">3. {t('Hora')}</h3>
      <div className="slots">
        {slots === null && <span className="muted">{t('Buscando huecos…')}</span>}
        {slots?.length === 0 && <span className="muted">{t('Ese día no quedan huecos. Prueba otro.')}</span>}
        {slots?.map((s) => (
          <button type="button" key={s} className="chip mono" aria-pressed={start === s} onClick={() => setStart(s)}>{hour(s)}</button>
        ))}
      </div>

      <h3 className="step">4. {t('Tus datos')}</h3>
      <div className="field"><label className="label" htmlFor="bk-name">{t('Nombre')}</label><input id="bk-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder={t('Tu nombre y apellido')} /></div>
      <div className="field"><label className="label" htmlFor="bk-phone">{t('Móvil')}</label><input id="bk-phone" inputMode="tel" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="600 000 000" /></div>
      <label className="check consent">
        <input type="checkbox" required checked={privacy} onChange={(e) => setPrivacy(e.target.checked)} />
        <span>{t('He leído la')} <Link to="/privacidad" target="_blank">{t('política de privacidad')}</Link> {t('y acepto que {name} use mis datos para gestionar mi cita.', { name: info.name })}</span>
      </label>
      {error && <p className="error">{error}</p>}
      <button className="btn primary wide" disabled={!start}>{start ? t('Confirmar cita a las {time}', { time: hour(start) }) : t('Elige una hora')}</button>
    </form>
  )
}
