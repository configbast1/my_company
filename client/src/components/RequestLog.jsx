import { useEffect, useState } from 'react'
import { onRequest } from '../api'

// Журнал: показує на екрані кожен запит, який клієнт відправив на Django
export function RequestLog() {
  const [items, setItems] = useState([])

  useEffect(() => onRequest((entry) => setItems((list) => [entry, ...list].slice(0, 8))), [])

  return (
    <aside className="log">
      <h4>Запити до Django</h4>
      {items.length === 0 && <p className="log__empty">Ще немає запитів</p>}
      <ul>
        {items.map((r) => (
          <li key={r.id}>
            <span className={`log__method log__method--${r.method.toLowerCase()}`}>{r.method}</span>
            <code>{r.url.replace(/^https?:\/\//, '')}</code>
            <span className={`log__status ${r.status === 'ERR' || r.status >= 400 ? 'log__status--bad' : ''}`}>
              {r.status}
            </span>
            <span className="log__ms">{r.ms} мс</span>
          </li>
        ))}
      </ul>
    </aside>
  )
}
