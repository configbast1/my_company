// Спільні стани завантаження / помилки для списків
export function Status({ loading, error, onRetry }) {
  if (loading) return <p className="status">Завантаження…</p>
  if (error)
    return (
      <div className="status status--error">
        <p>⚠️ {error}</p>
        <button onClick={onRetry}>Спробувати ще раз</button>
      </div>
    )
  return null
}
