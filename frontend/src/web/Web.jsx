import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import ChatBox from '../components/ChatBox.jsx'
import { euros } from '../format.js'
import BookingForm from './BookingForm.jsx'
import Logo from '../components/Logo.jsx'
import { LegalFooter } from './Legal.jsx'
import { t } from '../i18n/index.js'
import './web.css'

/** La web del centro: lo que ven las clientas. */
export default function Web() {
  const [info, setInfo] = useState(null)
  const [service, setService] = useState(null)
  const [chatOpen, setChatOpen] = useState(false)
  const [category, setCategory] = useState(null)

  useEffect(() => {
    api('/public/info/', { auth: false }).then((i) => {
      document.title = i.name
      const firstCategory = i.categories[0]?.key
      setInfo(i)
      setCategory(firstCategory)
      setService(i.services.find((s) => s.category === firstCategory)?.id)
    })
  }, [])

  // /reservar lleva directamente al formulario
  useEffect(() => {
    if (info && window.location.pathname === '/reservar') document.getElementById('reservar')?.scrollIntoView()
  }, [info])

  const bookService = (id) => {
    setService(id)
    document.getElementById('reservar')?.scrollIntoView({ behavior: 'smooth' })
  }
  const openChat = () => {
    setChatOpen(true)
    document.getElementById('aura')?.scrollIntoView({ behavior: 'smooth' })
  }

  if (!info) return <div className="site"><p className="site-loading">{t('Cargando…')}</p></div>

  const assistant = info.assistant_name
  const phoneLink = `tel:${info.phone.replace(/\s/g, '')}`
  const categoryNames = info.categories.map((c) => t(c.label).toLowerCase()).join(', ').replace(/, ([^,]*)$/, ` ${t('y')} $1`)
  const shownServices = info.services.filter((s) => s.category === category)
  const mapLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${info.address} ${info.name}`)}`

  return (
    <div className="site">

      <main>
        <section className="hero" id="inicio">
          <div className="hero-text">
            <h1 className="logo"><Logo className="logo-hero" /><span>{info.name}</span></h1>
            <p className="lead">
              {t('Centro de estética en {address}: {categories}.', { address: info.address, categories: categoryNames })}{' '}
              {t('Pide cita en un minuto o escríbele a {assistant}, que te contesta al momento.', { assistant })}
            </p>
            <div className="hero-actions">
              <a className="btn primary big" href="#reservar">{t('Pedir cita')}</a>
              <button className="btn quiet big" onClick={openChat}>{t('Preguntar a {assistant}', { assistant })}</button>
            </div>
          </div>
          <aside className="hero-card" aria-label={t('Datos de contacto')}>
            <p><b>{t('Dónde')}</b><a href={mapLink} target="_blank" rel="noreferrer">{info.address}</a></p>
            <p><b>{t('Teléfono')}</b><a href={phoneLink}>{info.phone}</a></p>
            <p><b>{t('Horario')}</b>{t(info.hours)}</p>
          </aside>
        </section>

        <section className="site-section" id="tratamientos">
          <h2>{t('Tratamientos y precios')}</h2>
          <p className="section-intro">{t('Precios finales, con todo incluido. Si no sabes cuál elegir, pregúntale a {assistant}.', { assistant })}</p>
          <div className="category-tabs" role="tablist" aria-label={t('Categorías')}>
            {info.categories.map((c) => (
              <button key={c.key} role="tab" aria-selected={category === c.key} className="category-tab" onClick={() => setCategory(c.key)}>{t(c.label)}</button>
            ))}
          </div>
          <ul className="menu">
            {shownServices.map((s) => (
              <li key={s.id}>
                <div className="menu-line">
                  <h3>{s.name}</h3>
                  <span className="leader" aria-hidden="true" />
                  <span className="price">{euros(s.price)}</span>
                </div>
                <p className="menu-detail"><span className="duration">{s.duration_minutes} min</span>{s.description}</p>
                <button className="link-button" onClick={() => bookService(s.id)}>{t('Reservar {service}', { service: s.name.toLowerCase() })}</button>
              </li>
            ))}
          </ul>
        </section>

        <section className="site-section booking-section" id="reservar">
          <h2>{t('Pide tu cita')}</h2>
          <p className="section-intro">{t('Solo te enseñamos las horas libres. Te llevará un minuto.')}</p>
          <BookingForm info={info} service={service} onServiceChange={setService} />
        </section>

        <section className="site-section" id="aura">
          <h2>{t('¿Tienes dudas? Pregúntale a {assistant}', { assistant })}</h2>
          <p className="section-intro">
            {t('{assistant} es la recepcionista virtual del centro. Te dice precios y horarios, te recomienda tratamiento y te reserva. Si no sabe algo, se lo pasa a {owner} y te contesta ella.', { assistant, owner: info.owner })}
            {info.telegram_bot && <> {t('También puedes escribirle por')} <a href={`https://t.me/${info.telegram_bot.replace('@', '')}`} target="_blank" rel="noreferrer">Telegram</a>.</>}
          </p>
          {chatOpen
            ? <ChatBox title={assistant} subtitle={t('Recepción de {name}', { name: info.name })} />
            : <button className="btn primary big" onClick={() => setChatOpen(true)}>{t('Hablar con {assistant}', { assistant })}</button>}
          <p className="privacy-note">
            {t('{assistant} es un asistente automático con IA de código abierto. Usamos lo que le escribas solo para atenderte y gestionar tu cita.', { assistant })}
            {' '}<Link to="/privacidad">{t('Política de privacidad')}</Link>.
          </p>
        </section>

        <section className="site-section contact" id="contacto">
          <h2>{t('Cómo llegar')}</h2>
          <dl>
            <div><dt>{t('Dirección')}</dt><dd><a href={mapLink} target="_blank" rel="noreferrer">{info.address}</a></dd></div>
            <div><dt>{t('Teléfono')}</dt><dd><a href={phoneLink}>{info.phone}</a></dd></div>
            <div><dt>{t('Horario')}</dt><dd>{t(info.hours)}</dd></div>
          </dl>
        </section>
      </main>

      <LegalFooter info={info} />

      {/* Con el chat abierto la barra de abajo taparía donde se escribe */}
      <div className={`mobile-bar ${chatOpen ? 'hidden' : ''}`}>
        <a className="btn primary" href="#reservar">{t('Pedir cita')}</a>
        <a className="btn quiet" href={phoneLink}>{t('Llamar')}</a>
      </div>
    </div>
  )
}
