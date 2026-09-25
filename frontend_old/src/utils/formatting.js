export const formatNumber = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return 'Not available'
  }

  return Number(value).toLocaleString()
}

export const formatPercent = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return 'Not available'
  }

  return `${Number(value).toFixed(1)}%`
}

export const safeText = (value, fallback = 'Not available') => {
  if (value === null || value === undefined || value === '') {
    return fallback
  }

  return value
}

export const getDifficultyColor = (difficulty) => {
  switch ((difficulty || '').toLowerCase()) {
    case 'easy':
      return '#22c55e'
    case 'medium':
      return '#f59e0b'
    case 'hard':
      return '#ef4444'
    default:
      return '#64748b'
  }
}
