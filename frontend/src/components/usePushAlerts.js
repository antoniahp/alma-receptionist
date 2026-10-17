import { useEffect, useState } from 'react'
import { api } from '../api.js'
import { t } from '../i18n/index.js'
import { useToast } from './Toast.jsx'

const supported = typeof window !== 'undefined' && 'serviceWorker' in navigator && 'PushManager' in window && 'Notification' in window

// La clave VAPID llega en base64url; el navegador la quiere en bytes
function keyToBytes(base64) {
  const padded = (base64 + '='.repeat((4 - (base64.length % 4)) % 4)).replace(/-/g, '+').replace(/_/g, '/')
  return Uint8Array.from(atob(padded), (c) => c.charCodeAt(0))
}

/** Avisos emergentes del sistema (como los de cualquier app) aunque el panel esté cerrado.
 * Estados: unsupported (navegador sin avisos), not-configured (faltan las claves en el servidor), error,
 * denied (la dueña los bloqueó en el navegador), off, on. */
export default function usePushAlerts() {
  const toast = useToast()
  const [state, setState] = useState('loading')
  const [busy, setBusy] = useState(false)
  const [problem, setProblem] = useState('')

  useEffect(() => {
    if (!supported) { setState('unsupported'); return }
    api('/push/').then(async (server) => {
      if (!server.enabled) { setState('not-configured'); return }
      if (Notification.permission === 'denied') { setState('denied'); return }
      const registration = await navigator.serviceWorker.register('/sw.js')
      const subscription = await registration.pushManager.getSubscription()
      setState(subscription ? 'on' : 'off')
    }).catch((e) => { setProblem(e.message); setState('error') })
  }, [])

  const enable = async () => {
    setBusy(true)
    try {
      const permission = await Notification.requestPermission()
      if (permission !== 'granted') { setState(permission === 'denied' ? 'denied' : 'off'); return }
      const { public_key: publicKey } = await api('/push/')
      const registration = await navigator.serviceWorker.register('/sw.js')
      await navigator.serviceWorker.ready
      const subscription = await registration.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: keyToBytes(publicKey) })
      await api('/push/', { method: 'POST', body: subscription.toJSON() })
      setState('on')
      toast(t('Avisos activados: te llegará uno de prueba ahora mismo'))
    } catch (e) {
      // Pasa, por ejemplo, en Brave (tiene los avisos apagados por defecto) o si el navegador no puede hablar con su servicio de avisos
      setProblem(e.message || '')
      toast(`${t('No se han podido activar los avisos')}: ${e.message || ''}`, 'error')
    } finally { setBusy(false) }
  }

  const disable = async () => {
    setBusy(true)
    try {
      const registration = await navigator.serviceWorker.getRegistration('/sw.js')
      const subscription = await registration?.pushManager.getSubscription()
      if (subscription) {
        await api('/push/', { method: 'DELETE', body: { endpoint: subscription.endpoint } })
        await subscription.unsubscribe()
      }
      setState('off')
      toast(t('Avisos desactivados en este navegador'))
    } finally { setBusy(false) }
  }

  return { state, busy, problem, enable, disable }
}
