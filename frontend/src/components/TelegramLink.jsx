import { useState } from 'react'
import { useToast } from './Toast.jsx'
import { t } from '../i18n/index.js'

// Icono que copia el enlace con el que una clienta vincula su Telegram (para mandárselo por WhatsApp o SMS).
// Solo tiene que abrirlo y pulsar "Iniciar" una vez; desde entonces le llegan los recordatorios.
export default function TelegramLink({ name, link, withText = false }) {
  const toast = useToast()
  const [copied, setCopied] = useState(false)
  if (!link) return null

  const firstName = name.split(' ')[0]
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(link)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
      toast(t('Enlace copiado. Mándaselo a {name} para que lo abra en Telegram.', { name: firstName }))
    } catch {
      toast(t('Copia este enlace: {link}', { link }))
    }
  }

  const label = t('Copiar el enlace de Telegram para {name}', { name: firstName })
  return (
    <button type="button" className={`icon-button ${copied ? 'done' : ''} ${withText ? 'with-text' : ''}`} onClick={copy} title={label} aria-label={label}>
      {copied ? (
        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5 10 17l9-10" /></svg>
      ) : (
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path d="M21 4 3 11l6 2 2 6 3-4 5 4 2-15Z" />
          <path d="m9 13 8-6" />
        </svg>
      )}
      {withText && <span>{copied ? t('Copiado') : t('Copiar enlace de Telegram')}</span>}
    </button>
  )
}
