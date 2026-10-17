import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api.js'
import Logo from '../components/Logo.jsx'
import LangSwitch from '../i18n/LangSwitch.jsx'
import { lang, t } from '../i18n/index.js'
import { PAGES_EN } from './LegalEn.jsx'
import './web.css'

// Plantillas pensadas para un centro de estética pequeño en España (LSSI-CE, RGPD y LOPDGDD).
// Son un punto de partida: la dueña debe revisarlas con su gestoría o asesoría antes de publicar la web.

const UPDATED = { es: '16 de octubre de 2026', en: '16 October 2026' }

function Missing({ children }) {
  return <mark className="legal-missing">{children}</mark>
}

function Owner({ info }) {
  return (
    <ul>
      <li><b>Titular:</b> {info.legal_name || <Missing>nombre y apellidos o razón social</Missing>}</li>
      <li><b>NIF:</b> {info.nif || <Missing>NIF</Missing>}</li>
      <li><b>Domicilio:</b> {info.address}</li>
      <li><b>Teléfono:</b> {info.phone}</li>
      <li><b>Correo:</b> {info.email ? <a href={`mailto:${info.email}`}>{info.email}</a> : <Missing>correo de contacto</Missing>}</li>
    </ul>
  )
}

function AvisoLegal({ info }) {
  return (
    <>
      <h1>Aviso legal</h1>
      <p>En cumplimiento de la Ley 34/2002, de servicios de la sociedad de la información y de comercio electrónico (LSSI-CE), estos son los datos de quien gestiona esta web:</p>
      <Owner info={info} />
      <h2>Para qué sirve esta web</h2>
      <p>Informar de los tratamientos y precios de {info.name} y permitir pedir cita, por la propia web o hablando con {info.assistant_name}, la recepcionista virtual del centro.</p>
      <h2>Precios</h2>
      <p>Los precios que se muestran son finales, con el IVA incluido. Pueden cambiar; se respeta siempre el precio que había cuando reservaste.</p>
      <h2>Recepcionista virtual</h2>
      <p>{info.assistant_name} es un programa automático, no una persona. Responde con la información del centro y, si no sabe algo, se lo pasa a {info.owner}. Sus respuestas son orientativas: no sustituyen el consejo de un profesional sanitario.</p>
      <h2>Propiedad intelectual</h2>
      <p>Los textos, el logotipo y las imágenes de esta web pertenecen a su titular. No se pueden copiar sin permiso.</p>
      <h2>Responsabilidad</h2>
      <p>Cuidamos que la información sea correcta y esté al día, pero puede haber errores. Si ves alguno, avísanos y lo corregimos.</p>
      <h2>Ley aplicable</h2>
      <p>Esta web se rige por la ley española.</p>
    </>
  )
}

function Privacidad({ info }) {
  return (
    <>
      <h1>Política de privacidad</h1>
      <p>Te contamos de forma sencilla qué datos tuyos usamos y para qué, según el Reglamento General de Protección de Datos (RGPD) y la Ley Orgánica 3/2018 (LOPDGDD).</p>

      <h2>Quién es responsable de tus datos</h2>
      <Owner info={info} />

      <h2>Qué datos usamos</h2>
      <ul>
        <li><b>Para reservar:</b> tu nombre y tu móvil, el tratamiento y la hora.</li>
        <li><b>Si usas Telegram:</b> tu identificador de chat de Telegram y los mensajes que nos escribes.</li>
        <li><b>Si escribes en el chat de la web:</b> los mensajes de la conversación.</li>
        <li><b>Si nos lo cuentas:</b> notas para atenderte bien, como alergias o tipo de piel. Son datos de salud: solo los apuntamos si tú nos los das, y solo para hacer el tratamiento con seguridad.</li>
        <li><b>Tu historial en el centro:</b> citas, bonos y cómo pagaste, porque lo exige la ley para las cuentas.</li>
      </ul>
      <p>No pedimos más datos de los necesarios ni los usamos para hacer perfiles publicitarios.</p>

      <h2>Para qué los usamos y por qué podemos hacerlo</h2>
      <ul>
        <li><b>Gestionar tus citas</b> (reservar, recordártelas, cambiarlas o cancelarlas): porque lo pides tú al reservar (art. 6.1.b RGPD).</li>
        <li><b>Avisarte cuando toque repetir un tratamiento</b> y, una sola vez tras varias visitas, <b>pedirte una reseña en Google</b>: por interés legítimo del centro en atender a sus clientas. Si no los quieres, díselo a {info.owner} y dejarán de llegarte.</li>
        <li><b>Las notas de salud</b>: con tu consentimiento expreso (art. 9.2.a RGPD), que puedes retirar cuando quieras.</li>
        <li><b>Cumplir obligaciones contables y fiscales</b>: por obligación legal (art. 6.1.c RGPD).</li>
      </ul>

      <h2>La recepcionista virtual</h2>
      <p>
        {info.assistant_name} usa un modelo de inteligencia artificial de código abierto para entender tus mensajes y contestarte.
        No toma decisiones por ti: solo informa y reserva lo que tú le pides. Si prefieres hablar con una persona, díselo y te atenderá {info.owner}.
      </p>

      <h2>Quién más ve tus datos</h2>
      <p>
        Nadie más, salvo los proveedores que necesitamos para que esto funcione y que solo los tratan por cuenta nuestra:
        el servicio de alojamiento de la web, el servicio de inteligencia artificial que lee los mensajes del chat y, si la usas, Telegram.
        No vendemos ni cedemos tus datos. Solo los daríamos a la Administración si una ley nos obliga.
      </p>

      <h2>Cuánto tiempo los guardamos</h2>
      <ul>
        <li>Tus datos de clienta, notas y conversaciones: mientras sigas viniendo al centro, o hasta que nos pidas que los borremos.</li>
        <li>Los datos de cobros: los años que exige la ley fiscal. Si nos pides que te borremos, se quedan sin tu nombre.</li>
      </ul>

      <h2>Tus derechos</h2>
      <p>
        Puedes pedir ver tus datos, corregirlos, borrarlos, llevártelos, limitar su uso u oponerte a él.
        Escríbenos a {info.email ? <a href={`mailto:${info.email}`}>{info.email}</a> : <Missing>correo de contacto</Missing>}, llámanos al {info.phone} o díselo en el centro.
        Te contestamos en menos de un mes. Si crees que no lo hemos hecho bien, puedes reclamar ante la
        {' '}<a href="https://www.aepd.es" target="_blank" rel="noreferrer">Agencia Española de Protección de Datos</a>.
      </p>
    </>
  )
}

function Cookies({ info }) {
  return (
    <>
      <h1>Política de cookies</h1>
      <p>Esta web <b>no usa cookies de publicidad ni de analítica</b>, y no te sigue por otras webs. Por eso no te sale el típico aviso de cookies.</p>
      <h2>Qué guardamos en tu navegador</h2>
      <ul>
        <li><b>Clientas:</b> el idioma que elijas (español o inglés) y un identificador de tu conversación con {info.assistant_name}, para que te reconozca si vuelves. No guarda tus mensajes ni tus datos en el navegador: están en el centro. Son necesarios para que el chat funcione.</li>
        <li><b>Panel del centro:</b> cuando {info.owner} entra en su panel, el navegador guarda su sesión para no pedirle la contraseña cada vez. Es técnicamente necesario y no hace falta consentimiento (art. 22.2 LSSI-CE).</li>
      </ul>
      <h2>Enlaces a otras webs</h2>
      <p>Si abres Google Maps, Telegram o Google para dejar una reseña, esas webs tienen sus propias cookies y políticas.</p>
    </>
  )
}

const PAGES = { 'aviso-legal': AvisoLegal, privacidad: Privacidad, cookies: Cookies }

/** Páginas legales de la web del centro. Los datos del titular salen de la configuración (BUSINESS_LEGAL_NAME, BUSINESS_NIF, BUSINESS_EMAIL). */
export default function Legal({ page }) {
  const [info, setInfo] = useState(null)
  useEffect(() => { api('/public/info/', { auth: false }).then(setInfo) }, [])
  useEffect(() => { if (info) document.title = `${t({ 'aviso-legal': 'Aviso legal', privacidad: 'Privacidad', cookies: 'Cookies' }[page])} · ${info.name}` }, [info, page])

  if (!info) return <div className="site"><p className="site-loading">{t('Cargando…')}</p></div>
  const Page = (lang === 'en' ? PAGES_EN : PAGES)[page]
  const incomplete = !info.legal_name || !info.nif || !info.email
  return (
    <div className="site">
      <header className="legal-top">
        <Link to="/" className="legal-brand"><Logo className="logo-small" /><span>{info.name}</span></Link>
        <Link to="/">← {t('Volver a la web')}</Link>
      </header>
      <main className="legal">
        {incomplete && <p className="legal-warning">{t('Faltan los datos marcados en amarillo. El centro tiene que completarlos antes de publicar la web.')}</p>}
        <Page info={info} />
        <p className="legal-updated">{t('Última actualización')}: {UPDATED[lang]}.</p>
      </main>
      <LegalFooter info={info} />
    </div>
  )
}

export function LegalFooter({ info }) {
  return (
    <footer className="site-footer">
      <p>{info.name}, {info.address}</p>
      <p className="legal-links">
        <Link to="/aviso-legal">{t('Aviso legal')}</Link>
        <Link to="/privacidad">{t('Privacidad')}</Link>
        <Link to="/cookies">{t('Cookies')}</Link>
        <LangSwitch />
      </p>
      <p><Link to="/panel">{t('Acceso para el centro')}</Link></p>
    </footer>
  )
}
