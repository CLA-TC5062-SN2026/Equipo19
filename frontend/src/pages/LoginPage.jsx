import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router'
import Aviso from '../components/Aviso'
import Boton from '../components/Boton'
import CampoEntrada from '../components/CampoEntrada'
import { mensajeDeError } from '../lib/errores'
import { useSesion } from '../sesion/contexto'

/** Inicio de sesión (RF-26). Los mensajes de 401 y 429 vienen del backend tal como los fija el SRS. */
export default function LoginPage() {
  const { usuario, iniciar, aviso } = useSesion()
  const navegar = useNavigate()
  const destino = useLocation().state?.desde ?? '/'
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)

  if (usuario) return <Navigate to={destino} replace />

  async function enviar(evento) {
    evento.preventDefault()
    setEnviando(true)
    setError(null)
    try {
      await iniciar(correo.trim(), contrasena)
      navegar(destino, { replace: true })
    } catch (e) {
      setError(e)
      setContrasena('')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main id="contenido" className="mx-auto flex max-w-md flex-col gap-6 px-4 py-12">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Iniciar sesión</h1>
        <p className="mt-1 text-sm text-gray-600">
          Expediente del Programa Parque Industrial Seguro de AMPIP.
        </p>
      </div>

      <Aviso tipo="info">{aviso}</Aviso>
      <Aviso tipo="error">{error && mensajeDeError(error)}</Aviso>

      <form onSubmit={enviar} className="flex flex-col gap-4 rounded-lg border border-gray-300 bg-white p-6 shadow-sm" noValidate>
        <CampoEntrada
          id="correo"
          etiqueta="Correo"
          tipo="email"
          autoComplete="username"
          requerido
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
        />
        <CampoEntrada
          id="contrasena"
          etiqueta="Contraseña"
          tipo="password"
          autoComplete="current-password"
          requerido
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
        />
        <Boton tipo="submit" cargando={enviando} anchoCompleto disabled={!correo || !contrasena}>
          {enviando ? 'Verificando…' : 'Entrar'}
        </Boton>
      </form>
      <p className="text-xs text-gray-600">
        Después de 5 intentos fallidos la cuenta se bloquea 15 minutos. La sesión se cierra tras 60 minutos sin uso.
      </p>
    </main>
  )
}
