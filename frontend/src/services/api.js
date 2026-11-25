// Cliente HTTP único del frontend. Toda llamada al backend pasa por aquí: agrega el token de sesión y convierte
// cualquier falla (respuesta de error del API o red caída) en un ErrorApi con el formato del contrato:
// { codigo, mensaje, detalles? } (schema Error de openapi_equipo.yaml).

const URL_BASE = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api').replace(/\/$/, '')
const LLAVE_TOKEN = 'sgpis.token'

// El token se guarda en sessionStorage para sobrevivir a una recarga de la pestaña; se borra al cerrar el
// navegador. Algunos navegadores bloquean el almacenamiento: entonces solo vive en memoria.
let token = leerToken()

function leerToken() {
  try {
    return sessionStorage.getItem(LLAVE_TOKEN)
  } catch {
    return null
  }
}

export function establecerToken(nuevo) {
  token = nuevo
  try {
    if (nuevo) sessionStorage.setItem(LLAVE_TOKEN, nuevo)
    else sessionStorage.removeItem(LLAVE_TOKEN)
  } catch {
    /* sin almacenamiento: el token queda solo en memoria */
  }
}

export function hayToken() {
  return Boolean(token)
}

export class ErrorApi extends Error {
  /**
   * @param {number} estatus Código HTTP; 0 si no hubo respuesta (servidor apagado o sin red).
   * @param {{codigo?: string, mensaje?: string, detalles?: {campo: string, problema: string}[]}} cuerpo
   */
  constructor(estatus, cuerpo = {}) {
    super(cuerpo.mensaje ?? `Error ${estatus}`)
    this.estatus = estatus
    this.codigo = cuerpo.codigo ?? null
    this.detalles = cuerpo.detalles ?? []
  }
}

/**
 * @param {string} ruta Ruta relativa al API, por ejemplo "/parques".
 * @param {{metodo?: string, cuerpo?: object, consulta?: Record<string, string | number | boolean | undefined>}} [opciones]
 */
export async function api(ruta, { metodo = 'GET', cuerpo, consulta } = {}) {
  const url = new URL(URL_BASE + ruta)
  for (const [k, v] of Object.entries(consulta ?? {})) {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, String(v))
  }
  const encabezados = {}
  if (token) encabezados.Authorization = `Bearer ${token}`
  if (cuerpo !== undefined) encabezados['Content-Type'] = 'application/json'

  let respuesta
  try {
    respuesta = await fetch(url, {
      method: metodo,
      headers: encabezados,
      body: cuerpo !== undefined ? JSON.stringify(cuerpo) : undefined,
    })
  } catch {
    throw new ErrorApi(0, {
      codigo: 'sin_conexion',
      mensaje: 'No hay conexión con el servidor de SGPIS. Revisa tu red o intenta en unos minutos.',
    })
  }

  if (respuesta.status === 401 && token) {
    // Sesión revocada, vencida o 60 min sin actividad (RF-26-AC-6): la app regresa al login.
    establecerToken(null)
    window.dispatchEvent(new CustomEvent('sgpis:sesion-expirada'))
  }

  if (!respuesta.ok) {
    const cuerpoError = await respuesta.json().catch(() => ({}))
    throw new ErrorApi(respuesta.status, cuerpoError)
  }
  if (respuesta.status === 204) return null
  return respuesta.json()
}
