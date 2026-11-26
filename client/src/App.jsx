import { useState } from 'react'
import { api, API_URL } from './api'
import { useApi } from './useApi'
import { Services } from './components/Services'
import { Employees } from './components/Employees'
import { Projects } from './components/Projects'
import { ComplaintForm } from './components/ComplaintForm'
import { RequestLog } from './components/RequestLog'

const TABS = [
  { id: 'services', title: '🛠️ Послуги', endpoint: 'GET /services/', Component: Services },
  { id: 'team', title: '👥 Команда', endpoint: 'GET /employees/', Component: Employees },
  { id: 'projects', title: '📁 Проєкти', endpoint: 'GET /projects/', Component: Projects },
  { id: 'complaint', title: '⚠️ Скарга', endpoint: 'POST /complaints/', Component: ComplaintForm },
]

export default function App() {
  const company = useApi(api.company)
  const [tab, setTab] = useState(TABS[0].id)
  const current = TABS.find((t) => t.id === tab)

  const online = !company.loading && !company.error

  return (
    <div className="app">
      <header className="header">
        <div className="wrap header__row">
          <div className="logo">
            {company.data?.name ?? 'ТехноСвіт'}
            <span>{company.data?.slogan ?? 'React-клієнт'}</span>
          </div>
          <div className={`server ${online ? 'server--on' : company.loading ? '' : 'server--off'}`}>
            <i /> Django API: {company.loading ? 'підключення…' : online ? 'на звʼязку' : 'недоступний'}
            <code>{API_URL}</code>
          </div>
        </div>
        <nav className="wrap tabs">
          {TABS.map((t) => (
            <button key={t.id} className={t.id === tab ? 'active' : ''} onClick={() => setTab(t.id)}>
              {t.title}
            </button>
          ))}
        </nav>
      </header>

      <main className="wrap layout">
        <section>
          <div className="section-head">
            <h1>{current.title.replace(/^\S+\s/, '')}</h1>
            <code className="endpoint">{current.endpoint}</code>
          </div>
          <current.Component key={current.id} />
        </section>
        <RequestLog />
      </main>

      <footer className="footer">
        React-клієнт сайту «Моя компанія» · дані з Django ({company.data?.email ?? '—'})
      </footer>
    </div>
  )
}
