import { createContext, useCallback, useContext, useRef, useState } from 'react'

const ToastContext = createContext(() => {})

/** Aviso abajo de la pantalla. Puede llevar un botón (p. ej. "Deshacer"): entonces dura más. */
export function ToastProvider({ children }) {
  const [msg, setMsg] = useState(null)
  const timer = useRef(null)
  const hide = useCallback(() => { clearTimeout(timer.current); setMsg(null) }, [])
  const show = useCallback((text, kind = 'info', action = null) => {
    setMsg({ text, kind, action })
    clearTimeout(timer.current)
    timer.current = setTimeout(() => setMsg(null), action ? 10000 : 3500)
  }, [])
  return (
    <ToastContext.Provider value={show}>
      {children}
      {msg && (
        <div className={`toast ${msg.kind}`} role="status">
          <span>{msg.text}</span>
          {msg.action && <button className="toast-action" onClick={() => { hide(); msg.action.onClick() }}>{msg.action.label}</button>}
        </div>
      )}
    </ToastContext.Provider>
  )
}

export const useToast = () => useContext(ToastContext)
