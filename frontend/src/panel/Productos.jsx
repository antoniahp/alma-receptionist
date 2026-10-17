import { Fragment, useEffect, useState } from 'react'
import { api, patch, post } from '../api.js'
import { useToast } from '../components/Toast.jsx'
import { euros } from '../format.js'
import { lang, plural, t } from '../i18n/index.js'

const LEVEL = { ok: ['ok', 'Bien'], watch: ['warn', 'Vigilar'], order: ['bad', 'Pedir'], ordered: ['acc', 'Pedido en curso'] }

function DraftCard({ order, onChange }) {
  const toast = useToast()
  const [subject, setSubject] = useState(order.email_subject)
  const [body, setBody] = useState(order.email_body)
  const [email, setEmail] = useState(order.supplier.email)
  const [busy, setBusy] = useState(false)
  // Antes de enviar se pide confirmación: un correo enviado a un proveedor no se puede deshacer
  const [confirming, setConfirming] = useState(false)
  const cleanEmail = email.trim()
  const isExample = cleanEmail.endsWith('.example')
  const looksWrong = cleanEmail !== '' && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(cleanEmail)

  const approve = async () => {
    setBusy(true)
    try {
      if (cleanEmail && cleanEmail !== order.supplier.email) await patch(`/suppliers/${order.supplier.id}/`, { email: cleanEmail })
      await patch(`/orders/${order.id}/`, { email_subject: subject, email_body: body })
      await post(`/orders/${order.id}/approve/`)
      toast(cleanEmail ? t('Correo enviado a {email}', { email: cleanEmail }) : t('Pedido marcado como hecho ({supplier} no tiene correo)', { supplier: order.supplier.name }))
      onChange()
    } catch (e) { toast(e.message, 'error') } finally { setBusy(false); setConfirming(false) }
  }
  const discard = async () => { await post(`/orders/${order.id}/discard/`); toast(t('Borrador descartado')); onChange() }

  return (
    <div className="card">
      <div className="card-head"><strong>{order.supplier.name}</strong><span className="mono">{t('{amount} aprox.', { amount: euros(order.total) })}</span></div>
      <div className="muted small">{order.written_by_ai ? t('Redactado por la IA') : t('Plantilla (IA apagada)')}</div>
      <div className="field">
        <label className="label" htmlFor={`mail-${order.id}`}>{t('Correo del proveedor')}</label>
        <input id={`mail-${order.id}`} type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="pedidos@proveedor.com" />
        {isExample && <span className="small bad-text">{t('Es un correo de ejemplo y rebotará. Pon uno real (puede ser el tuyo para probar).')}</span>}
        {looksWrong && <span className="small bad-text">{t('Este correo no parece válido. Revísalo.')}</span>}
        {!cleanEmail && <span className="muted small">{t('Sin correo no se envía nada: el pedido se marca como hecho (por si lo pides por teléfono).')}</span>}
      </div>
      <div className="lines">
        {order.lines.map((l) => <div key={l.id}><span>{l.units} × {l.product_name}</span><span className="mono">{t('+{n} usos', { n: l.uses_added })}</span></div>)}
      </div>
      <div className="field">
        <label className="label" htmlFor={`subj-${order.id}`}>{t('Asunto')}</label>
        <input id={`subj-${order.id}`} value={subject} onChange={(e) => setSubject(e.target.value)} />
      </div>
      <div className="field">
        <label className="label" htmlFor={`body-${order.id}`}>{t('Correo')}</label>
        <textarea id={`body-${order.id}`} value={body} onChange={(e) => setBody(e.target.value)} rows={9} />
      </div>
      {confirming ? (
        <div className="confirm-send" role="alertdialog" aria-labelledby={`confirm-${order.id}`}>
          <p id={`confirm-${order.id}`}>
            {cleanEmail
              ? plural(order.lines.length, 'Vas a enviar un correo de verdad a {email} pidiendo {n} producto por unos {amount}. Una vez enviado no se puede deshacer.', 'Vas a enviar un correo de verdad a {email} pidiendo {n} productos por unos {amount}. Una vez enviado no se puede deshacer.', { email: cleanEmail, amount: euros(order.total) })
              : t('{supplier} no tiene correo: el pedido se marcará como hecho sin enviar nada.', { supplier: order.supplier.name })}
          </p>
          <div className="actions">
            <button className="btn primary" disabled={busy} onClick={approve}>{busy ? t('Enviando…') : cleanEmail ? t('Sí, enviar el pedido') : t('Sí, marcar como hecho')}</button>
            <button className="btn ghost" disabled={busy} onClick={() => setConfirming(false)}>{t('No, volver a revisarlo')}</button>
          </div>
        </div>
      ) : (
        <div className="actions">
          <button className="btn primary" disabled={isExample || looksWrong} onClick={() => setConfirming(true)}>{cleanEmail ? t('Aprobar y enviar por correo') : t('Aprobar sin enviar correo')}</button>
          <button className="btn ghost" onClick={discard}>{t('Descartar')}</button>
        </div>
      )}
    </div>
  )
}

// Cada oferta se identifica por tienda + título + precio: una misma tienda puede tener varias versiones
const offerKey = (o) => `${o.store}|${o.title}|${o.price}`

function PriceComparison({ product, existing, onClose, onChosen }) {
  const toast = useToast()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [showUnverified, setShowUnverified] = useState(false)
  // Lo que ya está en la lista de compra para este producto: { tienda: clave de la oferta elegida }
  const [chosen, setChosen] = useState(() => Object.fromEntries(existing.map((item) => [item.store, offerKey(item)])))
  const [choosing, setChoosing] = useState(null)
  const [opening, setOpening] = useState(null)

  useEffect(() => {
    setData(null); setError('')
    api(`/products/${product.id}/prices/`).then(setData).catch((e) => setError(e.message))
  }, [product.id])

  // Se puede elegir cualquier oferta, no solo la más barata. De cada tienda va una sola a la lista:
  // si eliges otra de la misma tienda, sustituye a la anterior.
  const choose = async (offer) => {
    const key = offerKey(offer)
    const replacing = chosen[offer.store] && chosen[offer.store] !== key
    setChoosing(key)
    try {
      await post('/shopping-list/', {
        product: product.id, store: offer.store, title: offer.title, price: offer.price, link: offer.link, units: product.suggested_units || 1,
        page_token: offer.page_token,
      })
      setChosen((map) => ({ ...map, [offer.store]: key }))
      toast(t(replacing ? 'Cambiada la opción de {store} en la lista de compra' : 'Añadido a la lista de compra ({store})', { store: offer.store }))
      onChosen()
    } catch (e) { toast(e.message, 'error') } finally { setChoosing(null) }
  }

  // Abre la página del producto en la tienda. La pestaña se abre ya (si no, el navegador la bloquea)
  // con un aviso de carga, y cuando llega el enlace directo la llevamos allí; si no lo hay, a Google Shopping.
  const openStore = async (offer) => {
    const key = offerKey(offer)
    const tab = window.open('', '_blank')
    if (tab) {
      tab.document.title = t('Abriendo {store}…', { store: offer.store })
      tab.document.body.innerHTML = `<p style="font: 18px system-ui, sans-serif; color: #3F5C45; padding: 40px; text-align: center">${t('Buscando la página de {store}…', { store: offer.store.replace(/</g, '') })}</p>`
    }
    setOpening(key)
    let link = ''
    try {
      const params = new URLSearchParams({ token: offer.page_token, store: offer.store })
      link = (await api(`/offers/store-link/?${params}`)).link
    } catch { /* usamos el de Google */ }
    setOpening(null)
    if (!link) toast(t('{store} no da un enlace directo seguro: te abro la ficha de Google Shopping', { store: offer.store }))
    if (tab) tab.location.href = link || offer.link
  }

  const ourPrice = data ? Number(data.our_price) : 0
  // Diferencia de cada tienda con lo que pagamos ahora: negativa si es más barata
  const difference = (price) => Number(price) - ourPrice
  const savingPercent = data?.saving ? Math.round((Number(data.saving) / ourPrice) * 100) : 0
  const trusted = data ? data.offers.filter((o) => o.trusted) : []
  const unverified = data ? data.offers.filter((o) => !o.trusted) : []

  const row = (o, isCheapest) => {
    const key = offerKey(o)
    const diff = difference(o.price)
    return (
      <li key={key} className={`${isCheapest ? 'best' : ''} ${o.trusted ? '' : 'unverified'}`}>
        <span className="store-mark" aria-hidden="true">{o.store.trim()[0]?.toUpperCase()}</span>
        <span className="offer-text">
          <b>
            {o.store}
            {isCheapest && <span className="pill ok">{t('Más barato')}</span>}
            {!o.trusted && <span className="pill warn">{t('Sin verificar')}</span>}
          </b>
          <span className="muted small clamp">{o.title}</span>
        </span>
        <span className="offer-price">
          <b>{euros(o.price)}</b>
          <small className={diff < 0 ? 'ok-text' : 'muted'}>{diff < 0 ? `−${euros(-diff)}` : diff > 0 ? `+${euros(diff)}` : t('igual')}</small>
        </span>
        <span className="offer-actions">
          {(o.page_token || o.link) && <button className="btn ghost offer-link" disabled={opening === key} onClick={() => openStore(o)}>{opening === key ? t('Abriendo…') : t('Ver en la tienda')}</button>}
          {chosen[o.store] === key
            ? <span className="pill ok">{t('En la lista')} ✓</span>
            : <button className="btn primary offer-link" disabled={choosing === key} onClick={() => choose(o)}>{choosing === key ? t('Añadiendo…') : chosen[o.store] ? t('Cambiar a esta') : t('Elegir')}</button>}
        </span>
      </li>
    )
  }

  return (
    <div className="price-card" aria-live="polite">
      <div className="price-head">
        <div>
          <span className="muted small">{t('Comparar precios')}</span>
          <strong>{product.name}</strong>
        </div>
        <button className="price-close" onClick={onClose} aria-label={t('Cerrar')}>×</button>
      </div>

      {!data && !error && <p className="price-loading">{t('Buscando en tiendas online…')}</p>}
      {error && <p className="bad-text">{error}</p>}

      {data && (
        <>
          <div className="price-summary">
            <div className="price-box">
              <span>{t('Pagas ahora')}</span>
              <b>{euros(data.our_price)}</b>
              <small>{data.supplier}</small>
            </div>
            <div className={`price-box ${data.saving ? 'cheaper' : ''}`}>
              <span>{t('Lo más barato (tiendas de confianza)')}</span>
              <b>{data.cheapest ? euros(data.cheapest.price) : '—'}</b>
              <small>{data.cheapest ? data.cheapest.store : t('Sin ofertas')}</small>
            </div>
            <div className={`price-verdict ${data.saving ? 'save' : 'keep'}`}>
              {data.saving
                ? <><b>{t('Ahorras {amount}', { amount: euros(data.saving) })}</b><span>{t('un {n} % por unidad', { n: savingPercent })}</span></>
                : <><b>{t('Ya tienes buen precio')}</b><span>{trusted.length ? t('Nadie de confianza lo vende más barato') : t('No hay ofertas de confianza')}</span></>}
            </div>
          </div>

          {!data.offers.length && <p className="muted">{t('No hemos encontrado este mismo producto en tiendas online. Si su nombre no lleva la marca (por ejemplo «OPI GelColor…»), añádela para encontrarlo mejor.')}</p>}

          <ul className="offers">{trusted.map((o, i) => row(o, i === 0 && difference(o.price) < 0))}</ul>

          {unverified.length > 0 && (
            <div className="unverified-block">
              <button className="link-button" onClick={() => setShowUnverified((v) => !v)} aria-expanded={showUnverified}>
                {showUnverified ? plural(unverified.length, 'Ocultar {n} tienda sin verificar', 'Ocultar {n} tiendas sin verificar') : plural(unverified.length, 'Mostrar {n} tienda sin verificar', 'Mostrar {n} tiendas sin verificar')}
              </button>
              {showUnverified && (
                <>
                  <p className="muted small">{t('No están en nuestra lista de tiendas conocidas ni son la web oficial de la marca. Compra solo si la conoces.')}</p>
                  <ul className="offers">{unverified.map((o) => row(o, false))}</ul>
                </>
              )}
            </div>
          )}

          <p className="muted small price-foot">
            {t('Precios de Google Shopping (vía SerpApi), del mismo producto y tamaño. Pueden no incluir envío ni descuentos de profesional.')}
            {data.discarded > 0 && ` ${plural(data.discarded, 'Hemos dejado fuera {n} resultado de otros productos, tamaños o de segunda mano.', 'Hemos dejado fuera {n} resultados de otros productos, tamaños o de segunda mano.')}`}
          </p>
        </>
      )}
    </div>
  )
}

function ShoppingList({ groups, onChange }) {
  const toast = useToast()
  const [busyStore, setBusyStore] = useState(null)

  const changeUnits = async (item, units) => {
    if (units < 1) return
    try { await patch(`/shopping-list/${item.id}/`, { units }); onChange() } catch (e) { toast(e.message, 'error') }
  }
  const remove = async (item) => {
    await api(`/shopping-list/${item.id}/`, { method: 'DELETE' })
    onChange()
  }
  const order = async (group, boughtOnline) => {
    setBusyStore(group.store)
    try {
      await post('/shopping-list/order/', { store: group.store, bought_online: boughtOnline })
      toast(boughtOnline ? t('Apuntado como pedido en camino ({store})', { store: group.store }) : t('Borrador listo en «Pedidos por aprobar»: revísalo y envíalo cuando quieras'))
      onChange()
    } catch (e) { toast(e.message, 'error') } finally { setBusyStore(null) }
  }

  if (!groups.length) return null
  return (
    <section className="shopping">
      <h3 className="sub">{t('Lista de compra')}</h3>
      <p className="muted small">{t('Lo que has elegido en el comparador, agrupado por tienda.')}</p>
      <div className="shopping-groups">
        {groups.map((g) => (
          <div className="card shopping-group" key={g.store}>
            <div className="card-head">
              <strong>{g.store}</strong>
              <span className={`pill ${g.is_supplier ? 'acc' : g.trusted ? 'done' : 'warn'}`}>{g.is_supplier ? t('Tu proveedor') : g.trusted ? t('Tienda online') : t('Sin verificar')}</span>
            </div>
            <ul className="shopping-items">
              {g.items.map((item) => (
                <li key={item.id}>
                  <div className="shopping-top">
                    <span className="shopping-name">
                      <b>{item.product_name}</b>
                      {item.title && item.title !== item.product_name && <span className="muted small clamp">{t('En la tienda')}: {item.title}</span>}
                    </span>
                    <button className="price-close" onClick={() => remove(item)} aria-label={t('Quitar {name} de la lista', { name: item.product_name })}>×</button>
                  </div>
                  <div className="shopping-bottom">
                    <span className="muted small">{euros(item.price)} / {t('ud.')}</span>
                    <span className="stepper" aria-label={t('Unidades')}>
                      <button onClick={() => changeUnits(item, item.units - 1)} disabled={item.units <= 1} aria-label={t('Una menos')}>−</button>
                      <span>{item.units}</span>
                      <button onClick={() => changeUnits(item, item.units + 1)} aria-label={t('Una más')}>+</button>
                    </span>
                    <b className="shopping-total">{euros(item.total)}</b>
                    {!g.is_supplier && item.link && <a className="btn ghost offer-link" href={item.link} target="_blank" rel="noreferrer">{t('Comprar')}</a>}
                  </div>
                </li>
              ))}
            </ul>
            <div className="shopping-foot">
              <span>{t('Total')} <b>{euros(g.total)}</b></span>
              <div className="actions">
                {g.cart_link && (
                  <a className="btn primary" href={g.cart_link} target="_blank" rel="noreferrer">{t('Añadir todo al carrito de Amazon')}</a>
                )}
                {g.is_supplier && (
                  <button className="btn primary" disabled={busyStore === g.store} onClick={() => order(g, false)}>{t('Preparar pedido por correo')}</button>
                )}
                <button className={`btn ${g.is_supplier || g.cart_link ? 'ghost' : 'primary'}`} disabled={busyStore === g.store} onClick={() => order(g, true)}>
                  {t('Ya lo he comprado en su web')}
                </button>
              </div>
            </div>
            {!g.is_supplier && (
              <p className="muted small">
                {g.cart_link
                  ? t('Con «Añadir todo al carrito» se abre Amazon con todos estos productos ya en tu carrito.')
                  : t('Esta tienda no permite llenar el carrito desde fuera: pulsa «Comprar» en cada producto.')}{' '}
                {t('Cuando lo tengas, pulsa «Ya lo he comprado» y quedará como pedido en camino.')}
              </p>
            )}
          </div>
        ))}
      </div>
    </section>
  )
}

function NewProductForm({ onDone, onCancel }) {
  const toast = useToast()
  const [suppliers, setSuppliers] = useState([])
  const [services, setServices] = useState([])
  const [form, setForm] = useState({ name: '', supplier_id: '', new_supplier_name: '', unit_price: '', uses_per_unit: '1', units_in_stock: '0', min_units: '1', service_ids: [] })
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api('/suppliers/').then(setSuppliers)
    api('/services/').then((list) => setServices(list.filter((s) => s.active)))
  }, [])

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))
  const toggleService = (id) => setForm((f) => ({
    ...f, service_ids: f.service_ids.includes(id) ? f.service_ids.filter((x) => x !== id) : [...f.service_ids, id],
  }))
  const isNewSupplier = form.supplier_id === 'nuevo'

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      const product = await post('/products/', {
        name: form.name,
        supplier_id: isNewSupplier || !form.supplier_id ? null : form.supplier_id,
        new_supplier_name: isNewSupplier ? form.new_supplier_name : '',
        unit_price: form.unit_price.replace(',', '.') || '0',
        uses_per_unit: Number(form.uses_per_unit),
        units_in_stock: Number(form.units_in_stock),
        min_units: Number(form.min_units),
        service_ids: form.service_ids,
      })
      toast(t('{name} añadido', { name: product.name }))
      onDone()
    } catch (err) { toast(err.message, 'error') } finally { setBusy(false) }
  }

  return (
    <form className="card new-product" onSubmit={submit}>
      <h3>{t('Nuevo producto')}</h3>
      <div className="form-grid">
        <div className="field wide"><label className="label" htmlFor="np-name">{t('Nombre (con la marca, así el comparador lo encuentra)')}</label><input id="np-name" required value={form.name} onChange={set('name')} placeholder={t('Ej.: Starpil bandas de depilación (100 uds.)')} /></div>
        <div className="field">
          <label className="label" htmlFor="np-supplier">{t('Proveedor')}</label>
          <select id="np-supplier" required value={form.supplier_id} onChange={set('supplier_id')}>
            <option value="">{t('Elige…')}</option>
            {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
            <option value="nuevo">+ {t('Uno nuevo')}</option>
          </select>
        </div>
        {isNewSupplier && <div className="field"><label className="label" htmlFor="np-new-supplier">{t('Nombre del proveedor nuevo')}</label><input id="np-new-supplier" required value={form.new_supplier_name} onChange={set('new_supplier_name')} /></div>}
        <div className="field"><label className="label" htmlFor="np-price">{t('Precio por unidad (€)')}</label><input id="np-price" inputMode="decimal" required value={form.unit_price} onChange={set('unit_price')} placeholder="0,00" /></div>
        <div className="field"><label className="label" htmlFor="np-uses">{t('Usos que da cada unidad')}</label><input id="np-uses" type="number" min="1" required value={form.uses_per_unit} onChange={set('uses_per_unit')} /></div>
        <div className="field"><label className="label" htmlFor="np-stock">{t('Unidades que tienes ahora')}</label><input id="np-stock" type="number" min="0" required value={form.units_in_stock} onChange={set('units_in_stock')} /></div>
        <div className="field"><label className="label" htmlFor="np-min">{t('Avisar cuando queden menos de (uds.)')}</label><input id="np-min" type="number" min="0" required value={form.min_units} onChange={set('min_units')} /></div>
      </div>
      <fieldset className="service-picks">
        <legend className="label">{t('¿Qué tratamientos lo gastan? (un uso por cita)')}</legend>
        {[...new Set(services.map((s) => s.category_label))].map((category) => (
          <div key={category} className="service-group">
            <span className="muted small">{t(category)}</span>
            <div className="chips-wrap">
              {services.filter((s) => s.category_label === category).map((s) => (
                <button type="button" key={s.id} className="chip" aria-pressed={form.service_ids.includes(s.id)} onClick={() => toggleService(s.id)}>{s.display_name}</button>
              ))}
            </div>
          </div>
        ))}
      </fieldset>
      <div className="actions">
        <button className="btn primary" disabled={busy}>{t('Guardar producto')}</button>
        <button type="button" className="btn ghost" onClick={onCancel}>{t('Cancelar')}</button>
      </div>
    </form>
  )
}

function CountStock({ product, onDone }) {
  const toast = useToast()
  const [open, setOpen] = useState(false)
  const [units, setUnits] = useState('')
  if (!open) return <button className="link-button compare" onClick={() => { setUnits(String(Math.round((product.stock_uses / product.uses_per_unit) * 10) / 10).replace('.', lang === 'es' ? ',' : '.')); setOpen(true) }}>{t('Corregir stock')}</button>

  const save = async (e) => {
    e.preventDefault()
    const uses = Math.round(Number(units.replace(',', '.')) * product.uses_per_unit)
    if (Number.isNaN(uses) || uses < 0) { toast(t('Pon un número de unidades válido'), 'error'); return }
    try {
      await post(`/products/${product.id}/count/`, { uses_in_stock: uses })
      toast(t('Stock de {name} corregido', { name: product.name }))
      setOpen(false); onDone()
    } catch (err) { toast(err.message, 'error') }
  }
  return (
    <form className="count-stock" onSubmit={save}>
      <label className="small" htmlFor={`count-${product.id}`}>{t('Unidades que hay ahora')}</label>
      <input id={`count-${product.id}`} inputMode="decimal" value={units} onChange={(e) => setUnits(e.target.value)} autoFocus />
      <button className="btn primary offer-link">{t('Guardar')}</button>
      <button type="button" className="btn ghost offer-link" onClick={() => setOpen(false)}>{t('Cancelar')}</button>
    </form>
  )
}

export default function Productos({ onChange }) {
  const toast = useToast()
  const [rows, setRows] = useState([])
  const [orders, setOrders] = useState([])
  const [busy, setBusy] = useState(false)
  const [comparing, setComparing] = useState(null)
  const [addingProduct, setAddingProduct] = useState(false)

  const [shopping, setShopping] = useState([])

  const load = () => {
    api('/products/forecast/').then(setRows)
    api('/orders/?status=draft,sent').then(setOrders)
    api('/shopping-list/').then(setShopping)
    onChange()
  }
  useEffect(load, []) // eslint-disable-line react-hooks/exhaustive-deps

  const generate = async () => {
    setBusy(true)
    try {
      const drafts = await post('/orders/generate/')
      toast(drafts.length ? plural(drafts.length, '{n} pedido preparado para revisar', '{n} pedidos preparados para revisar') : t('No hace falta pedir nada ahora mismo'))
      load()
    } catch (e) { toast(e.message, 'error') } finally { setBusy(false) }
  }
  const receive = async (o) => { await post(`/orders/${o.id}/receive/`); toast(t('Stock actualizado')); load() }

  const toOrder = rows.filter((r) => r.status === 'order').length
  const drafts = orders.filter((o) => o.status === 'draft')
  const sent = orders.filter((o) => o.status === 'sent')

  return (
    <section>
      <div className="section-head">
        <div>
          <h2>{t('Productos')}</h2>
          <p className="muted">{t('Cada cita gasta producto. Aquí ves si te llega para las citas reservadas y, si no, la IA te prepara el correo al proveedor para que solo lo apruebes.')}</p>
        </div>
        <div className="actions">
          {!addingProduct && <button className="btn ghost" onClick={() => setAddingProduct(true)}>{t('Añadir producto')}</button>}
          <button className="btn primary" disabled={busy} onClick={generate}>
            {busy ? t('Preparando…') : toOrder ? plural(toOrder, 'Preparar pedido ({n} producto)', 'Preparar pedido ({n} productos)') : t('Revisar si hay que pedir')}
          </button>
        </div>
      </div>

      {addingProduct && <NewProductForm onDone={() => { setAddingProduct(false); load() }} onCancel={() => setAddingProduct(false)} />}

      <div className="tablewrap">
        <table className="stock-table">
          <thead><tr><th>{t('Producto')}</th><th className="num">{t('Quedan')}</th><th className="num">{t('Reservado')}</th><th className="num">{t('Tras reservas')}</th><th>{t('Nivel')}</th><th>{t('Previsión')}</th></tr></thead>
          <tbody>
            {rows.map((r) => {
              const [cls, label] = LEVEL[r.status]
              const pct = Math.max(0, Math.min(100, (r.after_bookings / (r.min_uses * 3)) * 100))
              return (
                <Fragment key={r.id}>
                <tr>
                  <td><strong>{r.name}</strong><div className="muted small">{t('{n} usos por unidad', { n: r.uses_per_unit })} · {r.supplier_name}</div><div className="product-links"><button className="link-button compare" aria-expanded={comparing?.id === r.id} onClick={() => setComparing(comparing?.id === r.id ? null : r)}>{comparing?.id === r.id ? t('Ocultar precios') : t('Comparar precios')}</button><CountStock product={r} onDone={load} /></div></td>
                  <td className="num" data-label={t('Quedan')}>{r.stock_uses}<div className="muted small">≈ {Math.round((r.stock_uses / r.uses_per_unit) * 10) / 10} {t('ud.')}</div></td>
                  <td className="num" data-label={t('Reservado')}>{r.reserved ? `−${r.reserved}` : 0}</td>
                  <td className="num" data-label={t('Tras reservas')}>{r.after_bookings}</td>
                  <td data-label={t('Nivel')}><span className={`pill ${cls}`}>{t(label)}</span><div className="bar"><i className={cls} style={{ width: `${pct}%` }} /></div></td>
                  <td className="small" data-label={t('Previsión')}>
                    {r.runs_out_for ? t('Falta para {client}, {when}', { client: r.runs_out_for.client, when: r.runs_out_for.when }) : r.after_bookings < r.min_uses ? t('Bajo el mínimo ({n})', { n: r.min_uses }) : t('Cubre todas las reservas')}
                    {r.suggested_units > 0 && <div className="muted">{t('Sugerido: {n} ud.', { n: r.suggested_units })}</div>}
                  </td>
                </tr>
                {/* Los precios se abren justo debajo del producto pulsado */}
                {comparing?.id === r.id && (
                  <tr className="price-row">
                    <td colSpan={6}><PriceComparison product={r} existing={shopping.flatMap((g) => g.items).filter((item) => item.product === r.id)} onClose={() => setComparing(null)} onChosen={() => api('/shopping-list/').then(setShopping)} /></td>
                  </tr>
                )}
                </Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      <ShoppingList groups={shopping} onChange={load} />

      <div className="grid2">
        <div>
          <h3 className="sub">{t('Pedidos por aprobar')}</h3>
          {!drafts.length && <p className="muted">{t('Nada que aprobar. Pulsa el botón de arriba para que la IA revise el stock.')}</p>}
          {drafts.map((o) => <DraftCard key={o.id} order={o} onChange={load} />)}
        </div>
        <div>
          <h3 className="sub">{t('Pedidos en camino')}</h3>
          {!sent.length && <p className="muted">{t('Ninguno.')}</p>}
          {sent.map((o) => (
            <div className="card" key={o.id}>
              <div className="card-head"><strong>{o.supplier.name}</strong><span className="pill acc">{t('En camino')}</span></div>
              <div className="lines">{o.lines.map((l) => <div key={l.id}><span>{l.units} × {l.product_name}</span><span className="mono">{t('+{n} usos', { n: l.uses_added })}</span></div>)}</div>
              <button className="btn" onClick={() => receive(o)}>{t('Marcar como recibido')}</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
