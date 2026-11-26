import { api } from '../api'
import { useApi } from '../useApi'
import { Status } from './Status'

const STATUS_COLOR = { planned: 'badge--gray', in_progress: 'badge--blue', done: 'badge--green' }

export function Projects() {
  const { loading, error, data, reload } = useApi(api.projects)
  if (!data) return <Status loading={loading} error={error} onRetry={reload} />

  return (
    <div className="grid">
      {data.map((p) => (
        <article key={p.id} className="card">
          <div className="card__top">
            <h3>{p.name}</h3>
            <span className={`badge ${STATUS_COLOR[p.status]}`}>{p.status_display}</span>
          </div>
          <p>
            <b>Клієнт:</b> {p.client}
          </p>
          <p>
            <b>Старт:</b> {new Date(p.start_date).toLocaleDateString('uk-UA')}
          </p>
          <div className="tags">
            {p.services.map((s) => (
              <span key={s} className="tag">{s}</span>
            ))}
          </div>
        </article>
      ))}
    </div>
  )
}
