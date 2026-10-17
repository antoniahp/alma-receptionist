import EN from './en.js'

// Idioma de la app: español (el del centro) o inglés (para quien no habla español, p. ej. el jurado del hackathon).
// Se recuerda en el navegador; la primera vez se elige según el idioma del navegador.
const KEY = 'lang'

function detect() {
  try {
    const saved = localStorage.getItem(KEY)
    if (saved === 'es' || saved === 'en') return saved
  } catch { /* sin almacenamiento */ }
  return (navigator.language || 'es').toLowerCase().startsWith('es') ? 'es' : 'en'
}

export const lang = detect()
export const locale = lang === 'en' ? 'en-GB' : 'es-ES'
document.documentElement.lang = lang

export function setLang(value) {
  try { localStorage.setItem(KEY, value) } catch { /* sin almacenamiento */ }
  window.location.reload()
}

/** Traduce un texto escrito en español. Las variables van entre llaves: t('Hola, {name}', { name }). */
export function t(text, vars = {}) {
  let result = lang === 'en' ? (EN[text] ?? text) : text
  for (const [key, value] of Object.entries(vars)) result = result.replaceAll(`{${key}}`, value)
  return result
}

/** Singular o plural según el número: plural(n, '{n} cita', '{n} citas'). */
export function plural(n, one, many, vars = {}) {
  return t(n === 1 ? one : many, { n, ...vars })
}
