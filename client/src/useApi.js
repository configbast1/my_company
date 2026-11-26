import { useEffect, useState } from 'react'

const LOADING = { loading: true, error: null, data: null }

// Завантажує дані з API при першому показі компонента; reload() - повторити запит.
export function useApi(loader) {
  const [state, setState] = useState(LOADING)
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    let cancelled = false // компонент закрили до відповіді - результат ігноруємо
    loader()
      .then(({ ok, status, data }) => {
        if (!ok) throw new Error(`Сервер відповів з кодом ${status}`)
        if (!cancelled) setState({ loading: false, error: null, data })
      })
      .catch((error) => {
        if (!cancelled) setState({ loading: false, error: error.message, data: null })
      })
    return () => {
      cancelled = true
    }
  }, [loader, attempt])

  const reload = () => {
    setState(LOADING)
    setAttempt((n) => n + 1)
  }

  return { ...state, reload }
}
