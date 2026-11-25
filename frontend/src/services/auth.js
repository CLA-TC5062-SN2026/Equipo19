// Autenticación contra el backend (tag "Autenticación" de openapi_equipo.yaml, RF-26).
import { api, establecerToken } from './api'

/** @returns {Promise<{token: string, expiraEn: string, usuario: object}>} */
export async function iniciarSesion(correo, contrasena) {
  const datos = await api('/auth/login', { metodo: 'POST', cuerpo: { correo, contrasena } })
  establecerToken(datos.token)
  return datos
}

/** Sesión vigente del token guardado (usuario, inicio y última actividad). */
export function obtenerSesionActual() {
  return api('/auth/me')
}

export async function cerrarSesion() {
  try {
    await api('/auth/logout', { metodo: 'POST' })
  } finally {
    establecerToken(null)
  }
}
