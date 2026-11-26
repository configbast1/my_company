import { useState } from 'react'
import { api } from '../api'
import { useApi } from '../useApi'
import { Status } from './Status'

export function Employees() {
  const { loading, error, data, reload } = useApi(api.employees)
  const [query, setQuery] = useState('')
  if (!data) return <Status loading={loading} error={error} onRetry={reload} />

  const q = query.trim().toLowerCase()
  const shown = data.filter((e) =>
    [e.full_name, e.position, e.department ?? ''].some((v) => v.toLowerCase().includes(q)),
  )

  return (
    <>
      <input
        className="search"
        placeholder="Пошук за ім'ям, посадою або відділом…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <table className="table">
        <thead>
          <tr>
            <th>ПІБ</th>
            <th>Посада</th>
            <th>Відділ</th>
            <th>Email</th>
            <th>Прийнято</th>
          </tr>
        </thead>
        <tbody>
          {shown.map((e) => (
            <tr key={e.id}>
              <td>{e.full_name}</td>
              <td>{e.position}</td>
              <td>{e.department ?? '—'}</td>
              <td>{e.email}</td>
              <td>{new Date(e.hire_date).toLocaleDateString('uk-UA')}</td>
            </tr>
          ))}
          {shown.length === 0 && (
            <tr>
              <td colSpan={5} className="empty">Нікого не знайдено</td>
            </tr>
          )}
        </tbody>
      </table>
    </>
  )
}
