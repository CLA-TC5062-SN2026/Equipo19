import { BrowserRouter, Outlet, Route, Routes, useNavigate } from 'react-router'
import Navbar from './components/Navbar'
import RutaProtegida from './components/RutaProtegida'
import DemoComponentes from './pages/DemoComponentes'
import LoginPage from './pages/LoginPage'
import NoEncontradoPage from './pages/NoEncontradoPage'
import ParqueDetallePage from './pages/ParqueDetallePage'
import ParqueNuevoPage from './pages/ParqueNuevoPage'
import ParquesPage from './pages/ParquesPage'
import ProveedorSesion from './sesion/ProveedorSesion'
import { useSesion } from './sesion/contexto'

const ENLACES = [{ etiqueta: 'Parques', ruta: '/' }]

function Marco() {
  const { usuario, cerrar } = useSesion()
  const navegar = useNavigate()
  return (
    <>
      <a
        href="#contenido"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-10 focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-semibold focus:text-primario-700 focus:outline-2 focus:outline-primario-700"
      >
        Saltar al contenido
      </a>
      <Navbar
        usuario={usuario}
        enlaces={ENLACES}
        onCerrarSesion={async () => {
          await cerrar()
          navegar('/login')
        }}
      />
      <Outlet />
    </>
  )
}

export default function App() {
  return (
    <ProveedorSesion>
      <BrowserRouter>
        <Routes>
          <Route element={<Marco />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/componentes" element={<DemoComponentes />} />
            <Route element={<RutaProtegida />}>
              <Route path="/" element={<ParquesPage />} />
              <Route path="/parques/nuevo" element={<ParqueNuevoPage />} />
              <Route path="/parques/:parqueId" element={<ParqueDetallePage />} />
            </Route>
            <Route path="*" element={<NoEncontradoPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ProveedorSesion>
  )
}
