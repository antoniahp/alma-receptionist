// Formas de pago (las mismas claves que el backend). El bono solo se ofrece si la clienta tiene uno para ese servicio.
export const PAYMENT_METHODS = [
  { key: 'efectivo', label: 'Efectivo', icon: '💶' },
  { key: 'tarjeta', label: 'Tarjeta', icon: '💳' },
  { key: 'bizum', label: 'Bizum', icon: '📱' },
  { key: 'bono', label: 'Bono', icon: '🎟️' },
]
export const PACK_SALE_METHODS = PAYMENT_METHODS.filter((m) => m.key !== 'bono')
export const paymentMethod = (key) => PAYMENT_METHODS.find((m) => m.key === key)
// Las etiquetas se traducen al mostrarlas: t(method.label)
