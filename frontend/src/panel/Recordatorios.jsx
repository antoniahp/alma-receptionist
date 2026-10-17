import { useEffect, useState } from 'react'
import { api, post } from '../api.js'
import TelegramLink from '../components/TelegramLink.jsx'
import { useToast } from '../components/Toast.jsx'
import { ago, hour, relDay } from '../format.js'
import { plural, t } from '../i18n/index.js'


const KIND = { reminder: 'Recordatorio', reactivation: 'Para repetir', confirmation: 'Confirmación', owner: 'Aviso para ti', review: 'Petición de reseña' }
const SENT = { sent: ['ok', 'Enviado'], simulated: ['warn', 'No enviado'], failed: ['bad', 'Error'] }

export default function Recordatorios({ onChange, telegram }) {
  const toast = useToast()
  const [pending, setPending] = useState(null)
  const [history, setHistory] = useState([])

  const load = () => {
    api('/notifications/pending/').then(setPending)
    api('/notifications/').then(setHistory)
  }
  useEffect(load, [])

  const done = (n, okText) => {
    if (n.status === 'sent') toast(okText)
    else toast(t('No ha salido: {error}. Se ha guardado el texto en el historial.', { error: n.error || t('Telegram no está configurado') }), 'error')
    load(); onChange()
  }
  const remind = async (a) => done(await post(`/appointments/${a.id}/remind/`), t('Recordatorio enviado'))
  const react = async (r) => {
    try { done(await post('/notifications/reactivate/', { client: r.client.id, service: r.service.id }), t('Mensaje enviado a {name}', { name: r.client.name.split(' ')[0] })) } catch (e) { toast(e.message, 'error') }
  }
  const runAll = async () => {
    const r = await post('/notifications/run/')
    toast(r.reminders + r.reactivations + (r.reviews || 0) ? t('Enviados: {reminders} recordatorios, {reactivations} mensajes para repetir y {reviews} peticiones de reseña', { reminders: r.reminders, reactivations: r.reactivations, reviews: r.reviews || 0 }) : t('Nada que enviar: las clientas pendientes aún no tienen Telegram vinculado'))
    load(); onChange()
  }

  return (
    <section>
      <div className="section-head">
        <div>
          <h2>{t('Recordatorios')}</h2>
          <p className="muted">{t('Salen solos por Telegram: el recordatorio 24 h antes de la cita y un mensaje cuando a una clienta le toca repetir. Aquí puedes adelantarlos.')}</p>
        </div>
        <button className="btn primary" onClick={runAll}>{t('Enviar ya lo pendiente')}</button>
      </div>
      <p className="note">
        <b>{t('¿Cómo le llega a una clienta?')}</b> {t('Por Telegram, si ha abierto el bot una vez desde su enlace. Al reservar en la web le sale el botón; si reservó por teléfono, copia su enlace aquí abajo y mándaselo por WhatsApp.')}
      </p>
      {telegram && !telegram.enabled && <p className="note">{t('Los recordatorios por Telegram aún no están activados. Aquí puedes ver los mensajes que se enviarían.')}</p>}

      <div className="grid2">
        <div>
          <h3 className="sub">{t('Recordatorios (próximas 24 h)')}</h3>
          {pending && !pending.reminders.length && <p className="muted">{t('Nada pendiente.')}</p>}
          {pending?.reminders.map(({ appointment: a, text }) => (
            <div className="card" key={a.id}>
              <div className="card-head"><strong>{a.client_name}</strong><span className="muted">{a.service_name} · {relDay(a.start)} {hour(a.start)}</span></div>
              <div className="msg">{text}</div>
              <div className="msg-buttons"><span>✅ {t('Allí estaré')}</span><span>🔄 {t('Cambiar la cita')}</span></div>
              {a.client_has_telegram ? (
                <div className="actions">
                  <span className="pill ok">{t('Telegram vinculado')}</span>
                  <button className="btn primary" onClick={() => remind(a)}>{t('Enviar ahora')}</button>
                </div>
              ) : (
                <>
                  <p className="muted small">{t('{name} aún no ha abierto el bot, así que el recordatorio no le puede llegar.', { name: a.client_name.split(' ')[0] })}</p>
                  <div className="actions"><TelegramLink name={a.client_name} link={a.client_telegram_link} withText /></div>
                </>
              )}
            </div>
          ))}
        </div>

        <div>
          <h3 className="sub">{t('Clientas a las que les toca repetir')}</h3>
          {pending && !pending.reactivations.length && <p className="muted">{t('Nadie pendiente estos días.')}</p>}
          {pending?.reactivations.map((r) => (
            <div className="card" key={`${r.client.id}-${r.service.id}`}>
              <div className="card-head">
                <strong>{r.client.name}</strong>
                <span className={`pill ${r.days_until_due < 0 ? 'warn' : 'acc'}`}>
                  {r.days_until_due < 0 ? plural(-r.days_until_due, 'Le tocaba hace {n} día', 'Le tocaba hace {n} días') : r.days_until_due === 0 ? t('Le toca hoy') : plural(r.days_until_due, 'Le toca en {n} día', 'Le toca en {n} días')}
                </span>
              </div>
              <div className="muted small">{r.service.name} · {plural(r.days_since, 'última visita hace {n} día', 'última visita hace {n} días')}</div>
              <div className="msg">{r.preview}</div>
              <div className="msg-buttons">{r.slots.map((s) => <span key={s}>{s}</span>)}<span>{t('Ahora no, gracias')}</span></div>
              <p className="muted small">{t('Al enviarlo, la recepcionista lo escribe con sus palabras; este es el texto de base.')}</p>
              {r.client.has_telegram
                ? <div className="actions"><button className="btn primary" onClick={() => react(r)}>{t('Enviar mensaje')}</button></div>
                : <><p className="muted small">{t('Aún no ha abierto el bot.')}</p><div className="actions"><TelegramLink name={r.client.name} link={r.client.telegram_link} withText /></div></>}
            </div>
          ))}
        </div>
      </div>

      <h3 className="sub">{t('Últimos mensajes')}</h3>
      {!history.length && <p className="muted">{t('Todavía no se ha enviado nada.')}</p>}
      <div className="history">
        {history.slice(0, 15).map((n) => {
          const [cls, label] = SENT[n.status]
          return (
            <div className="history-row" key={n.id}>
              <span className="muted small">{ago(n.created_at)}</span>
              <div className="who"><strong>{n.client_name || t('Tú')}</strong> <span className="muted">· {t(KIND[n.kind] || n.kind)}</span><div className="muted small clamp">{n.text}</div>{n.status !== 'sent' && n.error && <div className="small bad-text">{t('Motivo')}: {n.error}</div>}</div>
              <span className={`pill ${cls}`}>{t(label)}</span>
            </div>
          )
        })}
      </div>
    </section>
  )
}
