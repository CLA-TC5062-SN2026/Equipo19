import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router'
import Aviso from '../components/Aviso'
import Boton from '../components/Boton'
import CampoEntrada from '../components/CampoEntrada'
import CampoSelect from '../components/CampoSelect'
import { REGIONES, TIPOS_PI, ordenarPorEtiqueta } from '../lib/catalogos'
import { erroresPorCampo, mensajeDeError } from '../lib/errores'
import { crearParque, listarGeneraciones } from '../services/parques'

const VACIO = { nombre: '', desarrollador: '', tipoPI: '', region: '', generacionId: '' }

/**
 * Alta de parque (RF-02, RF-28). Solo Coordinación AMPIP llega aquí desde el tablero; si otro rol entra por URL,
 * el backend responde 403 y se muestra el aviso. Tipo de PI, región y generación los valida el backend con los
 * mensajes del SRS (RF-02-AC-2, AC-3 y RF-28-AC-3).
 */
export default function ParqueNuevoPage() {
  const navegar = useNavigate()
  const [datos, setDatos] = useState(VACIO)
  const [generaciones, setGeneraciones] = useState([])
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)
  const [errores, setErrores] = useState({})

  useEffect(() => {
    listarGeneraciones().then(setGeneraciones).catch(setError)
  }, [])

  const cambiar = (campo) => (e) => {
    setDatos((d) => ({ ...d, [campo]: e.target.value }))
    setErrores((x) => ({ ...x, [campo]: undefined }))
  }

  async function enviar(evento) {
    evento.preventDefault()
    const propios = {}
    if (!datos.nombre.trim()) propios.nombre = 'Escribe el nombre del parque.'
    if (!datos.desarrollador.trim()) propios.desarrollador = 'Escribe el nombre del desarrollador.'
    setErrores(propios)
    setError(null)
    if (Object.keys(propios).length) return

    setEnviando(true)
    try {
      const cuerpo = { ...datos, nombre: datos.nombre.trim(), desarrollador: datos.desarrollador.trim() }
      // Campos vacíos se mandan como null para que el backend responda con su mensaje de validación.
      for (const campo of ['tipoPI', 'region', 'generacionId']) if (!cuerpo[campo]) cuerpo[campo] = null
      const parque = await crearParque(cuerpo)
      navegar(`/parques/${parque.id}`, { state: { mensaje: `Se dio de alta ${parque.nombre}.` } })
    } catch (e) {
      setError(e)
      setErrores(erroresPorCampo(e))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main id="contenido" className="mx-auto flex max-w-2xl flex-col gap-6 px-4 py-8 sm:px-6">
      <div>
        <Link to="/" className="text-sm text-primario-700 hover:underline">← Parques</Link>
        <h1 className="mt-2 text-2xl font-bold text-gray-900">Dar de alta parque</h1>
        <p className="mt-1 text-sm text-gray-600">
          El parque entra en la fase de Diagnóstico con los criterios que aplican a su tipo de PI.
        </p>
      </div>

      <Aviso tipo="error">{error && mensajeDeError(error)}</Aviso>

      <form onSubmit={enviar} noValidate className="flex flex-col gap-4 rounded-lg border border-gray-300 bg-white p-6 shadow-sm">
        <CampoEntrada id="nombre" etiqueta="Nombre del parque" requerido maxLength={200}
          value={datos.nombre} onChange={cambiar('nombre')} error={errores.nombre} />
        <CampoEntrada id="desarrollador" etiqueta="Desarrollador" requerido maxLength={200}
          ayuda="Si el desarrollador no existe, se registra con este nombre."
          value={datos.desarrollador} onChange={cambiar('desarrollador')} error={errores.desarrollador} />
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoSelect id="tipoPI" etiqueta="Tipo de PI" requerido vacio="Selecciona…"
            opciones={Object.entries(TIPOS_PI)} value={datos.tipoPI} onChange={cambiar('tipoPI')} error={errores.tipoPI} />
          <CampoSelect id="region" etiqueta="Región (estado)" requerido vacio="Selecciona…"
            opciones={ordenarPorEtiqueta(REGIONES)} value={datos.region} onChange={cambiar('region')} error={errores.region} />
        </div>
        <CampoSelect id="generacionId" etiqueta="Generación" requerido vacio="Selecciona…"
          opciones={generaciones.map((g) => [g.id, `${g.nombre} (catálogo ${g.versionCatalogoNombre})`])}
          value={datos.generacionId} onChange={cambiar('generacionId')} error={errores.generacionId} />
        <div className="flex flex-wrap justify-end gap-3 pt-2">
          <Link to="/" className="inline-flex min-h-11 items-center rounded-md border border-gray-500 bg-white px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-100">
            Cancelar
          </Link>
          <Boton tipo="submit" cargando={enviando}>Dar de alta</Boton>
        </div>
      </form>
    </main>
  )
}
