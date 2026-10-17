// Service worker del panel: recibe los avisos (Web Push) aunque el panel esté cerrado
// y los enseña como notificación del sistema. Al pulsarla abre el panel en la página que toca.

self.addEventListener('push', (event) => {
  let data = {}
  try { data = event.data ? event.data.json() : {} } catch { data = { body: event.data?.text() } }
  event.waitUntil(
    self.registration.showNotification(data.title || 'Alma', {
      body: data.body || '',
      icon: '/icon-192.png',
      badge: '/favicon.png',
      data: { url: data.url || '/panel' },
    }),
  )
})

self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const url = event.notification.data?.url || '/panel'
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windows) => {
      const open = windows.find((w) => new URL(w.url).pathname.startsWith('/panel'))
      if (open) { open.navigate(url); return open.focus() }
      return self.clients.openWindow(url)
    }),
  )
})
