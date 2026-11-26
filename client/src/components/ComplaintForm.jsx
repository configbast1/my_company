import { useState } from 'react'
import { api } from '../api'
import { useApi } from '../useApi'

const EMPTY = {
  full_name: '',
  email: '',
  phone: '',
  complaint_type: 'service',
  service: '',
  product_name: '',
  subject: '',
  description: '',
  resolution: 'fix',
  wants_callback: false,
  agree: false,
}

// Перевірка на стороні клієнта (ті самі правила, що й у Django ComplaintForm)
function validate(f) {
  const errors = {}
  if (!f.full_name.trim()) errors.full_name = "Вкажіть ім'я."
  if (!/^\S+@\S+\.\S+$/.test(f.email)) errors.email = 'Вкажіть коректний email.'
  if (f.complaint_type === 'service' && !f.service) errors.service = 'Оберіть послугу.'
  if (f.complaint_type === 'product' && !f.product_name.trim()) errors.product_name = 'Вкажіть назву товару.'
  if (!f.subject.trim()) errors.subject = 'Вкажіть тему.'
  if (f.description.trim().length < 20) errors.description = 'Мінімум 20 символів.'
  if (f.wants_callback && !f.phone.trim()) errors.phone = 'Потрібен телефон для дзвінка.'
  if (!f.agree) errors.agree = 'Потрібна згода на обробку даних.'
  return errors
}

export function ComplaintForm() {
  const services = useApi(api.services)
  const [form, setForm] = useState(EMPTY)
  const [errors, setErrors] = useState({})
  const [sending, setSending] = useState(false)
  const [result, setResult] = useState(null)

  const set = (name) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value
    setForm((f) => ({ ...f, [name]: value }))
    setErrors((errs) => ({ ...errs, [name]: undefined }))
  }

  async function submit(e) {
    e.preventDefault()
    setResult(null)
    const clientErrors = validate(form)
    setErrors(clientErrors)
    if (Object.keys(clientErrors).length) return

    setSending(true)
    try {
      const { ok, data } = await api.createComplaint(form)
      if (ok) {
        setResult({ type: 'success', text: data.message })
        setForm(EMPTY)
      } else {
        // помилки валідації від Django: { field: ["..."] }
        setErrors(Object.fromEntries(Object.entries(data.errors).map(([k, v]) => [k, v.join(' ')])))
        setResult({ type: 'error', text: 'Сервер повернув помилки, перевірте поля.' })
      }
    } catch (error) {
      setResult({ type: 'error', text: error.message })
    } finally {
      setSending(false)
    }
  }

  const Field = ({ name, label, children }) => (
    <label className={`field ${errors[name] ? 'field--error' : ''}`}>
      <span>{label}</span>
      {children}
      {errors[name] && <small>{errors[name]}</small>}
    </label>
  )

  return (
    <form className="form" onSubmit={submit} noValidate>
      {result && <div className={`alert alert--${result.type}`}>{result.text}</div>}

      <div className="form__row">
        {Field({ name: 'full_name', label: 'ПІБ *', children: <input value={form.full_name} onChange={set('full_name')} placeholder="Іван Петренко" /> })}
        {Field({ name: 'email', label: 'Email *', children: <input type="email" value={form.email} onChange={set('email')} placeholder="ivan@example.com" /> })}
      </div>
      {Field({ name: 'phone', label: 'Телефон', children: <input value={form.phone} onChange={set('phone')} placeholder="+38 (0__) ___-__-__" /> })}

      <div className="segmented">
        {[['service', 'Послуга'], ['product', 'Товар']].map(([value, label]) => (
          <button
            type="button"
            key={value}
            className={form.complaint_type === value ? 'active' : ''}
            onClick={() => setForm((f) => ({ ...f, complaint_type: value }))}
          >
            {label}
          </button>
        ))}
      </div>

      {form.complaint_type === 'service'
        ? Field({
            name: 'service',
            label: 'Послуга *',
            children: (
              <select value={form.service} onChange={set('service')}>
                <option value="">— оберіть послугу —</option>
                {(services.data ?? []).filter((s) => s.is_active).map((s) => (
                  <option key={s.id} value={s.id}>{s.title}</option>
                ))}
              </select>
            ),
          })
        : Field({ name: 'product_name', label: 'Назва товару *', children: <input value={form.product_name} onChange={set('product_name')} /> })}

      {Field({ name: 'subject', label: 'Тема *', children: <input value={form.subject} onChange={set('subject')} placeholder="Коротко про проблему" /> })}
      {Field({ name: 'description', label: 'Опис проблеми *', children: <textarea rows={4} value={form.description} onChange={set('description')} placeholder="Що сталося…" /> })}
      {Field({
        name: 'resolution',
        label: 'Бажане вирішення',
        children: (
          <select value={form.resolution} onChange={set('resolution')}>
            <option value="refund">Повернення коштів</option>
            <option value="replace">Заміна / повторне надання послуги</option>
            <option value="fix">Усунення недоліків</option>
            <option value="other">Інше</option>
          </select>
        ),
      })}

      <label className="check">
        <input type="checkbox" checked={form.wants_callback} onChange={set('wants_callback')} /> Передзвоніть мені
      </label>
      <label className={`check ${errors.agree ? 'check--error' : ''}`}>
        <input type="checkbox" checked={form.agree} onChange={set('agree')} /> Я погоджуюсь на обробку персональних даних *
      </label>
      {errors.agree && <small className="error">{errors.agree}</small>}

      <button className="submit" disabled={sending}>
        {sending ? 'Надсилаємо…' : 'Надіслати скаргу (POST)'}
      </button>
    </form>
  )
}
