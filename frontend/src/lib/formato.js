const FECHA = new Intl.DateTimeFormat('es-MX', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' })

/** "2027-06-30" -> "30 jun 2027". Las fechas del contrato son `date` sin zona: se formatean en UTC. */
export function fecha(valor) {
  if (!valor) return '—'
  return FECHA.format(new Date(valor.length === 10 ? `${valor}T00:00:00Z` : valor))
}

/** 86.96 -> "87 %"; null (no aplica) -> "N/A". */
export function porcentaje(valor) {
  if (valor === null || valor === undefined) return 'N/A'
  return `${Math.round(valor)} %`
}
