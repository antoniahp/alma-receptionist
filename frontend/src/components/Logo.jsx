/** Logo oficial del centro (frontend/public/logo.png). Para cambiarlo basta con sustituir ese archivo. */
export default function Logo({ className = 'logo-img', label = '' }) {
  return <img className={className} src="/logo.png" alt={label} aria-hidden={label ? undefined : 'true'} />
}
