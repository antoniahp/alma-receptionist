import { lang, locale } from './i18n/index.js'

const DAYS = {
  es: ['domingo', 'lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado'],
  en: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
}
const DAYS_SHORT = {
  es: ['dom', 'lun', 'mar', 'mié', 'jue', 'vie', 'sáb'],
  en: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
}
const MONTHS = {
  es: ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
  en: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
}
export const monthNames = MONTHS[lang]
export const shortMonthNames = MONTHS[lang].map((m) => m.slice(0, 3))

const pad = (n) => String(n).padStart(2, '0')

// Las fechas de la API vienen con la hora local del centro (p. ej. 2026-10-15T17:00:00+02:00).
// Usamos esa hora "de pared" tal cual, para que se vea igual aunque el navegador esté en otra zona horaria.
export function wall(v) {
  if (v instanceof Date) return v
  const m = /^(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/.exec(v)
  if (!m) return new Date(v)
  return new Date(+m[1], +m[2] - 1, +m[3], +(m[4] || 0), +(m[5] || 0))
}
export const isoDate = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
export const addDays = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x }
export const hour = (v) => { const d = wall(v); return `${pad(d.getHours())}:${pad(d.getMinutes())}` }
export const dayLong = (v) => {
  const d = wall(v)
  return lang === 'en'
    ? `${DAYS.en[d.getDay()]} ${d.getDate()} ${MONTHS.en[d.getMonth()]}`
    : `${DAYS.es[d.getDay()]} ${d.getDate()} de ${MONTHS.es[d.getMonth()]}`
}
export const dayShort = (v) => { const d = wall(v); return `${DAYS_SHORT[lang][d.getDay()]} ${d.getDate()}` }
export const euros = (n) => Number(n).toLocaleString(locale, { style: 'currency', currency: 'EUR' })
export const shortDate = (iso) => (iso ? new Date(iso).toLocaleDateString(locale, { day: 'numeric', month: 'short', year: 'numeric' }) : '—')
export const localDate = (iso) => new Date(iso).toLocaleDateString(locale)

export function relDay(v) {
  const d = wall(v); const today = new Date()
  const diff = Math.round((new Date(d.getFullYear(), d.getMonth(), d.getDate()) - new Date(today.getFullYear(), today.getMonth(), today.getDate())) / 864e5)
  if (diff === 0) return lang === 'en' ? 'Today' : 'Hoy'
  if (diff === 1) return lang === 'en' ? 'Tomorrow' : 'Mañana'
  return dayLong(v).replace(/^./, (c) => c.toUpperCase())
}

export const ago = (v) => {
  const min = Math.round((Date.now() - new Date(v)) / 60000)
  const en = lang === 'en'
  if (min < 1) return en ? 'just now' : 'ahora'
  if (min < 60) return en ? `${min} min ago` : `hace ${min} min`
  if (min < 1440) return en ? `${Math.round(min / 60)} h ago` : `hace ${Math.round(min / 60)} h`
  return en ? `${Math.round(min / 1440)} days ago` : `hace ${Math.round(min / 1440)} días`
}
