import { createContext, useContext } from 'react'

export const SesionContext = createContext(null)

/** @returns {{usuario: object | null, verificando: boolean, iniciar: Function, cerrar: Function, aviso: string}} */
export function useSesion() {
  const valor = useContext(SesionContext)
  if (!valor) throw new Error('useSesion debe usarse dentro de <ProveedorSesion>')
  return valor
}
