import { api } from '../api'
import { useApi } from '../useApi'
import { Status } from './Status'

const money = (value) => value.toLocaleString('uk-UA', { maximumFractionDigits: 0 })

export function Services() {
  const { loading, error, data, reload } = useApi(api.services)
  if (!data) return <Status loading={loading} error={error} onRetry={reload} />

  return (
    <div className="grid">
      {data.map((s) => (
        <article key={s.id} className="card">
          <div className="card__top">
            <h3>{s.title}</h3>
            <span className={`badge ${s.is_active ? 'badge--green' : 'badge--gray'}`}>
              {s.is_active ? 'активна' : 'неактивна'}
            </span>
          </div>
          <p>{s.description}</p>
          <p className="price">від {money(s.price_from)} грн</p>
        </article>
      ))}
    </div>
  )
}
