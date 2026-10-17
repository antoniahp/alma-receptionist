import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// En local /api se redirige al backend. Con Docker Compose el backend se llama "backend".
const backendUrl = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    // Para probar en el móvil con un túnel HTTPS (cloudflared): deja entrar a esas direcciones
    allowedHosts: ['.trycloudflare.com'],
    proxy: { '/api': { target: backendUrl, changeOrigin: true } },
  },
})
