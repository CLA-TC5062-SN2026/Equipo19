import { useCallback, useEffect, useMemo, useState } from 'react'
import { hayToken } from '../services/api'
import { cerrarSesion, iniciarSesion, obtenerSesionActual } from '../services/auth'
import { SesionContext } from './contexto'

/**
 * Estado de sesión de toda la app (decisión de S07-S08-A1: Context API, sin librería de estado).
 * Al cargar, si hay un token guardado lo valida con GET /auth/me; si el backend responde 401 en cualquier
 * momento, api.js emite "sgpis:sesion-expirada" y aquí se limpia el usuario.
 */
export default function ProveedorSesion({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [verificando, setVerificando] = useState(hayToken())
  const [aviso, setAviso] = useState('')

  useEffect(() => {
    if (!hayToken()) return
    obtenerSesionActual()
      .then((s) => setUsuario(s.usuario))
      .catch(() => setUsuario(null))
      .finally(() => setVerificando(false))
  }, [])

  useEffect(() => {
    const alExpirar = () => {
      setUsuario(null)
      setAviso('Tu sesión terminó por inactividad o fue cerrada. Inicia sesión de nuevo.')
    }
    window.addEventListener('sgpis:sesion-expirada', alExpirar)
    return () => window.removeEventListener('sgpis:sesion-expirada', alExpirar)
  }, [])

  const iniciar = useCallback(async (correo, contrasena) => {
    const datos = await iniciarSesion(correo, contrasena)
    setAviso('')
    setUsuario(datos.usuario)
    return datos.usuario
  }, [])

  const cerrar = useCallback(async () => {
    await cerrarSesion().catch(() => {})
    setUsuario(null)
  }, [])

  const valor = useMemo(
    () => ({ usuario, verificando, iniciar, cerrar, aviso }),
    [usuario, verificando, iniciar, cerrar, aviso],
  )
  return <SesionContext.Provider value={valor}>{children}</SesionContext.Provider>
}
