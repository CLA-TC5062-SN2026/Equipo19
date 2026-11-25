import { useState } from 'react'
import { Link, NavLink } from 'react-router'
import { ROLES } from '../lib/catalogos'
import Boton from './Boton'

/**
 * Barra de navegación de SGPIS con estado autenticado / no autenticado.
 *
 * No lee la sesión por sí misma: la recibe por props para que el estado viva en un solo lugar
 * (ProveedorSesion) y el componente sea fácil de probar.
 *
 * @param {object} props
 * @param {{nombre: string, rol: string} | null} props.usuario null = no autenticado.
 * @param {{etiqueta: string, ruta: string}[]} [props.enlaces]
 * @param {() => void} [props.onCerrarSesion]
 */
export default function Navbar({ usuario = null, enlaces = [], onCerrarSesion }) {
  const [menuAbierto, setMenuAbierto] = useState(false)

  return (
    <nav aria-label="Principal" className="bg-primario-700">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3 sm:px-6">
        <Link
          to="/"
          className="rounded text-lg font-bold text-white focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-white"
        >
          SGPIS <span className="font-normal text-blue-100">· Parque Industrial Seguro</span>
        </Link>

        {usuario && (
          <button
            type="button"
            className="rounded-md p-2 text-white hover:bg-primario-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white md:hidden"
            aria-expanded={menuAbierto}
            aria-controls="menu-principal"
            onClick={() => setMenuAbierto(!menuAbierto)}
          >
            <span className="sr-only">{menuAbierto ? 'Cerrar menú' : 'Abrir menú'}</span>
            <svg className="size-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              {menuAbierto ? (
                <path strokeLinecap="round" d="M6 6l12 12M6 18L18 6" />
              ) : (
                <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        )}

        {usuario && (
          <div
            id="menu-principal"
            className={`${menuAbierto ? 'flex' : 'hidden'} w-full flex-col gap-3 pb-2 md:flex md:w-auto md:flex-row md:items-center md:gap-6 md:pb-0`}
          >
            <ul className="flex flex-col gap-1 md:flex-row md:gap-1">
              {enlaces.map((enlace) => (
                <li key={enlace.ruta}>
                  <NavLink
                    to={enlace.ruta}
                    end
                    onClick={() => setMenuAbierto(false)}
                    className={({ isActive }) => `block rounded-md px-3 py-2 text-sm font-medium text-white
                      focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white
                      ${isActive ? 'bg-primario-800' : 'hover:bg-primario-800'}`}
                  >
                    {enlace.etiqueta}
                  </NavLink>
                </li>
              ))}
            </ul>
            <div className="flex flex-col gap-2 md:flex-row md:items-center md:gap-3">
              <span className="text-sm text-white">
                {usuario.nombre}
                <span className="ml-2 rounded-full bg-primario-800 px-2 py-0.5 text-xs font-medium text-white">
                  {ROLES[usuario.rol] ?? usuario.rol}
                </span>
              </span>
              <Boton variante="secundario" sobreOscuro onClick={onCerrarSesion}>
                Cerrar sesión
              </Boton>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
