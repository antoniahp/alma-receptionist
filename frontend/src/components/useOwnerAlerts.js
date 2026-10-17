import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { t } from '../i18n/index.js'
import { useToast } from './Toast.jsx'

/** Con el panel abierto: aviso dentro del panel y contador en el título de la pestaña cuando Aura le pasa
 * una pregunta a la dueña. (Los avisos emergentes del sistema llegan aparte, por Web Push: ver usePushAlerts.) */
export default function useOwnerAlerts(dash) {
  const toast = useToast()
  const navigate = useNavigate()
  const seen = useRef(null)
  const unread = useRef(0)
  const baseTitle = useRef(document.title)

  // Al volver a la pestaña se quita el contador del título
  useEffect(() => {
    const reset = () => { unread.current = 0; document.title = baseTitle.current }
    window.addEventListener('focus', reset)
    return () => window.removeEventListener('focus', reset)
  }, [])

  useEffect(() => {
    if (!dash) return
    const question = dash.latest_help_request
    // La primera vez solo se apunta lo que ya había: no se avisa de lo antiguo
    if (seen.current === null) {
      seen.current = question?.id
      baseTitle.current = document.title
      return
    }
    if (!question || question.id === seen.current) return
    seen.current = question.id
    const who = question.client_name || t('Una clienta')
    toast(`🙋 ${t('{name} tiene una pregunta', { name: who })}: ${question.question}`, 'info', { label: t('Ver'), onClick: () => navigate('/panel/mensajes') })
    if (document.hidden) {
      unread.current += 1
      document.title = `(${unread.current}) ${baseTitle.current}`
    }
  }, [dash]) // eslint-disable-line react-hooks/exhaustive-deps
}
