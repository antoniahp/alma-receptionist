import { useEffect, useState } from 'react'
import { api, download, post } from '../api.js'
import { useToast } from '../components/Toast.jsx'
import { euros, isoDate, localDate, monthNames, shortMonthNames } from '../format.js'
import { plural, t } from '../i18n/index.js'

const EXPENSE_TYPES = [
  ['alquiler', 'Alquiler'],
  ['suministros', 'Luz, agua e internet'],
  ['autonomo', 'Autónomo e impuestos'],
  ['material', 'Material y mobiliario'],
  ['publicidad', 'Publicidad'],
  ['otros', 'Otros'],
]

// "2026-10-01" -> fecha local sin líos de zona horaria
const parseMonth = (value) => { const [y, m] = value.split('-').map(Number); return new Date(y, m - 1, 1) }
const monthParam = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
const monthName = (d) => `${monthNames[d.getMonth()]} ${d.getFullYear()}`
const addMonths = (d, n) => new Date(d.getFullYear(), d.getMonth() + n, 1)
// "2026-10-05" -> "05/10/2026" (sin pasar por Date, que podría cambiar el día por la zona horaria)
const dayLabel = (iso) => iso.split('-').reverse().join('/')

/** Barras de ingresos y gastos de los últimos meses. Pulsar un mes lo abre. */
function MonthsChart({ history, selected, onSelect }) {
  const [hover, setHover] = useState(null)
  const max = Math.max(1, ...history.flatMap((m) => [Number(m.income), Number(m.spending)]))
  const height = (value) => `${Math.max(Number(value) > 0 ? 2 : 0, (Number(value) / max) * 100)}%`

  return (
    <figure className="months-chart">
      <figcaption className="chart-legend">
        <span><i className="swatch income" />{t('Ingresos')}</span>
        <span><i className="swatch spending" />{t('Gastos')}</span>
      </figcaption>
      <div className="chart-plot">
        {history.map((m) => {
          const month = parseMonth(m.month)
          const isSelected = m.month.slice(0, 7) === monthParam(selected)
          return (
            <button
              key={m.month}
              className={`chart-month ${isSelected ? 'selected' : ''}`}
              onClick={() => onSelect(month)}
              onMouseEnter={() => setHover(m)}
              onMouseLeave={() => setHover(null)}
              onFocus={() => setHover(m)}
              onBlur={() => setHover(null)}
              aria-label={t('{month}: ingresos {income}, gastos {spending}', { month: monthName(month), income: euros(m.income), spending: euros(m.spending) })}
            >
              <span className="chart-bars">
                <i className="bar-income" style={{ height: height(m.income) }} />
                <i className="bar-spending" style={{ height: height(m.spending) }} />
              </span>
              <span className="chart-label">{shortMonthNames[month.getMonth()]}</span>
              {hover === m && (
                <span className="chart-tip" role="tooltip">
                  <b>{monthName(month)}</b>
                  <span><i className="swatch income" />{t('Ingresos')} {euros(m.income)}</span>
                  <span><i className="swatch spending" />{t('Gastos')} {euros(m.spending)}</span>
                  <span>{t('Beneficio')} <b>{euros(m.profit)}</b></span>
                </span>
              )}
            </button>
          )
        })}
      </div>
    </figure>
  )
}

function ExpenseForm({ month, onAdded }) {
  const toast = useToast()
  const today = new Date()
  const sameMonth = today.getFullYear() === month.getFullYear() && today.getMonth() === month.getMonth()
  const [form, setForm] = useState({ concept: '', category: 'otros', amount: '', date: isoDate(sameMonth ? today : month) })
  const [busy, setBusy] = useState(false)

  useEffect(() => { setForm((f) => ({ ...f, date: isoDate(sameMonth ? today : month) })) }, [month]) // eslint-disable-line react-hooks/exhaustive-deps

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))
  const submit = async (e) => {
    e.preventDefault()
    setBusy(true)
    try {
      await post('/expenses/', { ...form, amount: form.amount.replace(',', '.') })
      toast(t('Gasto apuntado: {concept}', { concept: form.concept }))
      setForm((f) => ({ ...f, concept: '', amount: '' }))
      onAdded()
    } catch (err) { toast(err.message, 'error') } finally { setBusy(false) }
  }

  return (
    <form className="expense-form" onSubmit={submit}>
      <div className="field"><label className="label" htmlFor="ex-concept">{t('Concepto')}</label><input id="ex-concept" required value={form.concept} onChange={set('concept')} placeholder={t('Ej.: recibo de la luz')} /></div>
      <div className="field"><label className="label" htmlFor="ex-type">{t('Tipo')}</label>
        <select id="ex-type" value={form.category} onChange={set('category')}>{EXPENSE_TYPES.map(([v, l]) => <option key={v} value={v}>{t(l)}</option>)}</select>
      </div>
      <div className="field"><label className="label" htmlFor="ex-amount">{t('Importe (€)')}</label><input id="ex-amount" required inputMode="decimal" value={form.amount} onChange={set('amount')} placeholder="0,00" /></div>
      <div className="field"><label className="label" htmlFor="ex-date">{t('Fecha')}</label><input id="ex-date" type="date" required value={form.date} onChange={set('date')} /></div>
      <button className="btn primary" disabled={busy}>{t('Apuntar gasto')}</button>
    </form>
  )
}

export default function Cuentas() {
  const toast = useToast()
  const [month, setMonth] = useState(() => { const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), 1) })
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  const load = () => {
    setError('')
    api(`/finances/?month=${monthParam(month)}`).then(setData).catch((e) => setError(e.message))
  }
  useEffect(load, [month]) // eslint-disable-line react-hooks/exhaustive-deps

  const exportMonth = async () => {
    try {
      await download(`/finances/export/?month=${monthParam(month)}`, `cuentas-${monthParam(month)}.csv`)
      toast(t('Descargado: se abre con Excel o Numbers'))
    } catch (e) { toast(e.message, 'error') }
  }

  const removeExpense = async (expense) => {
    await api(`/expenses/${expense.id}/`, { method: 'DELETE' })
    toast(t('Gasto borrado: {concept}', { concept: expense.concept }))
    load()
  }

  const isFuture = addMonths(month, 1) > new Date()
  const profit = data ? Number(data.profit) : 0
  // Si se cobran las citas que ya están reservadas este mes
  const projected = data ? profit + Number(data.expected_income) : 0
  const topIncome = data ? Math.max(1, ...data.income_by_category.map((c) => Number(c.amount))) : 1

  return (
    <section>
      <div className="section-head">
        <div>
          <h2>{t('Cuentas')}</h2>
          <p className="muted">{t('Ingresos de las citas y bonos cobrados, y gastos: pedidos de productos y lo que apuntes tú (alquiler, luz…).')}</p>
        </div>
        <div className="head-actions">
          <div className="month-nav">
            <button className="btn ghost" onClick={() => setMonth(addMonths(month, -1))} aria-label={t('Mes anterior')}>‹</button>
            <b>{monthName(month)}</b>
            <button className="btn ghost" onClick={() => setMonth(addMonths(month, 1))} disabled={isFuture} aria-label={t('Mes siguiente')}>›</button>
          </div>
          <button className="btn" onClick={exportMonth} title={t('Todos los ingresos y gastos del mes, para la gestoría')}>{t('Descargar para la gestoría')}</button>
        </div>
      </div>

      {error && <p className="bad-text">{error}</p>}
      {!data && !error && <p className="muted">{t('Cargando…')}</p>}

      {data && (
        <>
          <div className="metrics money">
            <div className="metric">
              <span className="label">{t('Ingresos')}</span>
              <b className="income-text">{euros(data.income)}</b>
              <small className="muted">{plural(data.appointments_completed, '{n} cita completada', '{n} citas completadas')}</small>
              {Number(data.expected_income) > 0 && <small className="muted">{t('+ {amount} en citas reservadas', { amount: euros(data.expected_income) })}</small>}
            </div>
            <div className="metric">
              <span className="label">{t('Gastos')}</span>
              <b className="spending-text">{euros(data.spending)}</b>
              <small className="muted">{t('Productos {products} · otros {other}', { products: euros(data.product_spending), other: euros(data.other_spending) })}</small>
            </div>
            <div className={`metric profit ${profit >= 0 ? 'positive' : 'negative'}`}>
              <span className="label">{profit >= 0 ? t('Beneficio') : t('Pérdida')}</span>
              <b>{profit < 0 ? '−' : ''}{euros(Math.abs(profit))}</b>
              <small className="muted">{profit >= 0 ? t('Lo que queda tras los gastos') : t('De momento se ha gastado más de lo ingresado')}</small>
              {Number(data.expected_income) > 0 && (
                <small className="muted">{t('Contando las citas reservadas, el mes acabaría en')} <b>{projected < 0 ? '−' : ''}{euros(Math.abs(projected))}</b></small>
              )}
            </div>
          </div>

          <h3 className="sub">{t('Últimos 6 meses')}</h3>
          <MonthsChart history={data.history} selected={month} onSelect={setMonth} />
          <details className="chart-table">
            <summary>{t('Ver como tabla')}</summary>
            <table>
              <thead><tr><th>{t('Mes')}</th><th className="num">{t('Ingresos')}</th><th className="num">{t('Gastos')}</th><th className="num">{t('Beneficio')}</th></tr></thead>
              <tbody>
                {data.history.map((m) => (
                  <tr key={m.month}><td>{monthName(parseMonth(m.month))}</td><td className="num">{euros(m.income)}</td><td className="num">{euros(m.spending)}</td><td className="num">{euros(m.profit)}</td></tr>
                ))}
              </tbody>
            </table>
          </details>

          <div className="grid2">
            <div>
              <h3 className="sub">{t('De dónde vienen los ingresos')}</h3>
              {!data.income_by_category.length && <p className="muted">{t('Este mes aún no hay citas completadas ni bonos vendidos.')}</p>}
              <ul className="breakdown">
                {data.income_by_category.map((c) => (
                  <li key={c.label}>
                    <span className="breakdown-head"><b>{t(c.label)}</b><span>{euros(c.amount)}</span></span>
                    <span className="breakdown-bar"><i style={{ width: `${(Number(c.amount) / topIncome) * 100}%` }} /></span>
                    <small className="muted">{c.label === 'Bonos' ? plural(c.count, '{n} bono vendido', '{n} bonos vendidos') : plural(c.count, '{n} cita', '{n} citas')}</small>
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="sub">{t('En qué se va el dinero')}</h3>
              <ul className="spend-list">
                {data.orders.map((o) => (
                  <li key={o.id}>
                    <span><b>{t('Pedido a {supplier}', { supplier: o.supplier })}</b><small className="muted">{t('Productos')} · {localDate(o.sent_at)}</small></span>
                    <span className="spend-amount">{euros(o.total)}</span>
                    <span />
                  </li>
                ))}
                {data.expenses.map((e) => (
                  <li key={e.id}>
                    <span><b>{e.concept}</b><small className="muted">{t(e.category_label)} · {dayLabel(e.date)}</small></span>
                    <span className="spend-amount">{euros(e.amount)}</span>
                    <button className="price-close" onClick={() => removeExpense(e)} aria-label={t('Borrar {concept}', { concept: e.concept })}>×</button>
                  </li>
                ))}
                {!data.orders.length && !data.expenses.length && <li className="muted">{t('Sin gastos este mes.')}</li>}
              </ul>
              <h3 className="sub">{t('Apuntar un gasto')}</h3>
              <ExpenseForm month={month} onAdded={load} />
            </div>
          </div>
        </>
      )}
    </section>
  )
}
