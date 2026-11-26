// Усі запити до локального Django-сервера проходять через цей модуль.
export const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

// Слухачі журналу запитів (компонент RequestLog показує кожен запит на екрані)
const listeners = new Set()
export function onRequest(listener) {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

async function request(method, path, body) {
  const url = `${API_URL}${path}`
  const started = performance.now()
  const entry = { id: crypto.randomUUID(), method, url, time: new Date() }

  try {
    const response = await fetch(url, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    })
    const data = await response.json()
    listeners.forEach((l) => l({ ...entry, status: response.status, ms: Math.round(performance.now() - started) }))
    return { ok: response.ok, status: response.status, data }
  } catch (error) {
    // сервер не запущено або CORS заблокував запит
    listeners.forEach((l) => l({ ...entry, status: 'ERR', ms: Math.round(performance.now() - started) }))
    throw new Error(`Не вдалося з'єднатися з ${url}. Чи запущено Django-сервер?`, { cause: error })
  }
}

export const api = {
  company: () => request('GET', '/company/'),
  services: () => request('GET', '/services/'),
  employees: () => request('GET', '/employees/'),
  projects: () => request('GET', '/projects/'),
  createComplaint: (data) => request('POST', '/complaints/', data),
}
