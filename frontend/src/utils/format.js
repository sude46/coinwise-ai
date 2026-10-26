export function formatAmount(amount, type = 'neutral') {
  const num = Number(amount) || 0
  const sign = num >= 0 ? (type === 'income' ? '+' : '') : '-'
  const abs = Math.abs(num).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
  return `${sign}¥${abs}`
}

function normalizeDate(dateStr) {
  if (!dateStr) return ''
  return /[Z+\-]\d{2}:\d{2}$/.test(dateStr) || dateStr.endsWith('Z')
    ? dateStr : dateStr + 'Z'
}

export function formatDate(dateStr) {
  if (!dateStr) return ''
  const d = new Date(normalizeDate(dateStr))
  return `${d.getMonth() + 1}月${d.getDate()}日`
}

export function formatDateTime(dateStr) {
  if (!dateStr) return ''
  const d = new Date(normalizeDate(dateStr))
  return `${d.getMonth() + 1}月${d.getDate()}日 ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

export function formatYearMonth(date = new Date()) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  return `${y}-${m}`
}

export function getCurrentYearMonth() {
  return formatYearMonth(new Date())
}
