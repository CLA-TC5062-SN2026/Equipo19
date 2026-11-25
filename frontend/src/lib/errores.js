// Traduce un ErrorApi a lo que ve el usuario: un mensaje general y, si aplica, errores por campo.

const POR_CODIGO = {
  sin_conexion: 'No hay conexión con el servidor de SGPIS. Revisa tu red o intenta en unos minutos.',
  sin_permiso: 'Tu rol no tiene permiso para esta operación.',
  no_encontrado: 'El registro que buscas no existe o ya no está disponible para tu cuenta.',
  error_interno: 'Ocurrió un error en el servidor. Intenta de nuevo; si se repite, avisa a soporte.',
}

/** Mensaje para un aviso general. El backend ya manda mensajes en español para los errores de negocio. */
export function mensajeDeError(error) {
  if (!error) return ''
  if (error.codigo && POR_CODIGO[error.codigo]) return POR_CODIGO[error.codigo]
  if (error.estatus === 403) return POR_CODIGO.sin_permiso
  return error.message || 'Ocurrió un error inesperado.'
}

// Códigos de validación del backend que corresponden a un campo del formulario.
const CAMPO_POR_CODIGO = {
  tipo_pi_invalido: 'tipoPI',
  region_invalida: 'region',
  generacion_requerida: 'generacionId',
  generacion_no_existe: 'generacionId',
  motivo_requerido: 'motivo',
}

/**
 * Errores por campo a partir del código y de `detalles` (campo: "activo.nombre" -> "nombre").
 * @returns {Record<string, string>}
 */
export function erroresPorCampo(error) {
  const campos = {}
  if (!error || ![409, 422].includes(error.estatus)) return campos
  const principal = CAMPO_POR_CODIGO[error.codigo]
  if (principal) campos[principal] = error.message
  for (const d of error.detalles ?? []) {
    const campo = d.campo.split('.').pop()
    if (!campos[campo]) campos[campo] = 'Revisa este dato.'
  }
  return campos
}
