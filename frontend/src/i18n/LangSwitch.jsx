import { lang, setLang } from './index.js'

/** Botones ES · EN para cambiar el idioma. */
export default function LangSwitch({ className = '' }) {
  return (
    <span className={`lang-switch ${className}`} role="group" aria-label="Idioma / Language">
      <button type="button" aria-pressed={lang === 'es'} onClick={() => setLang('es')}>ES</button>
      <button type="button" aria-pressed={lang === 'en'} onClick={() => setLang('en')}>EN</button>
    </span>
  )
}
