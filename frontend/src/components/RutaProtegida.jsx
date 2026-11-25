import { Navigate, Outlet, useLocation } from 'react-router'
import { useSesion } from '../sesion/contexto'
import Cargando from './Cargando'

/** Deja pasar solo con sesión; si no, manda al login y recuerda a dónde iba el usuario. */
export default function RutaProtegida() {
  const { usuario, verificando } = useSesion()
  const ubicacion = useLocation()
  if (verificando) return <Cargando texto="Verificando tu sesión…" />
  if (!usuario) return <Navigate to="/login" replace state={{ desde: ubicacion.pathname }} />
  return <Outlet />
}
