import { useEffect, useMemo, useState } from 'react'
import { Link, useLocation } from 'react-router'
import Aviso from '../components/Aviso'
import BarraAvance from '../components/BarraAvance'
import Cargando from '../components/Cargando'
import CampoSelect from '../components/CampoSelect'
import Etiqueta from '../components/Etiqueta'
import { ESTADOS_PARQUE, FASES, ORDEN_FASE, REGIONES, TIPOS_PI, ordenarPorEtiqueta } from '../lib/catalogos'
import { mensajeDeError } from '../lib/errores'
import { listarCriteriosParque, listarGeneraciones, listarParques, obtenerCumplimiento } from '../services/parques'
import { useSesion } from '../sesion/contexto'

/** Indicadores por parque que no vienen en el listado: cumplimiento (RF-08) y criterios atrasados (RF-09). */
async function indicadores(parque) {
  if (parque.tipoRegistro !== 'activo' || parque.estado !== 'activo') return {}
  const [cumplimiento, criterios] = await Promise.allSettled([
    obtenerCumplimiento(parque.id),
    listarCriteriosParque(parque.id),
  ])
  return {
    obligatorios: cumplimiento.status === 'fulfilled' ? cumplimiento.value.total.porcentajeObligatorios : undefined,
    // El gerente corporativo no ve el detalle de criterios (403, decisión P-01): se muestra "—".
    atrasados:
      criterios.status === 'fulfilled' ? criterios.value.items.filter((c) => c.atrasado).length : undefined,
  }
}

/**
 * Tablero de la generación (RF-07, RF-32): todos los parques que el rol puede ver, con su fase,
 * su cumplimiento de obligatorios y sus atrasos. El backend filtra por rol (RNF-01).
 */
export default function ParquesPage() {
  const { usuario } = useSesion()
  const esCoordinacion = usuario.rol === 'coordinacion_ampip'
  const mensajeFlash = useLocation().state?.mensaje
  const [filtros, setFiltros] = useState({ generacionId: '', region: '', estado: '', atrasado: '' })
  const [generaciones, setGeneraciones] = useState([])
  const [parques, setParques] = useState(null)
  const [extra, setExtra] = useState({})
  const [error, setError] = useState(null)

  useEffect(() => {
    listarGeneraciones().then(setGeneraciones).catch(() => setGeneraciones([]))
  }, [])

  useEffect(() => {
    let vigente = true // descarta respuestas de un filtro anterior
    listarParques(filtros)
      .then(async (pagina) => {
        if (!vigente) return
        setError(null)
        setParques(pagina.items)
        const pares = await Promise.all(pagina.items.map(async (p) => [p.id, await indicadores(p)]))
        if (vigente) setExtra(Object.fromEntries(pares))
      })
      .catch((e) => {
        if (!vigente) return
        setError(e)
        setParques([])
      })
    return () => {
      vigente = false
    }
  }, [filtros])

  const nombreGeneracion = useMemo(
    () => Object.fromEntries(generaciones.map((g) => [g.id, g.nombre])),
    [generaciones],
  )

  const resumen = useMemo(() => {
    const activos = (parques ?? []).filter((p) => p.estado === 'activo')
    return {
      activos: activos.length,
      conAtraso: activos.filter((p) => (extra[p.id]?.atrasados ?? 0) > 0).length,
      actualizacionVencida: activos.filter((p) => p.atrasadoActualizacion).length,
      bajoMeta: activos.filter((p) => extra[p.id]?.obligatorios !== undefined && extra[p.id].obligatorios < 50).length,
    }
  }, [parques, extra])

  const cambiar = (campo) => (e) => {
    setParques(null) // muestra "Cargando" mientras llega la página filtrada
    setFiltros((f) => ({ ...f, [campo]: e.target.value }))
  }

  return (
    <main id="contenido" className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Parques del programa</h1>
          <p className="mt-1 text-sm text-gray-600">
            Fase, cumplimiento de criterios obligatorios y atrasos de cada parque.
          </p>
        </div>
        {esCoordinacion && (
          <Link
            to="/parques/nuevo"
            className="inline-flex min-h-11 items-center rounded-md bg-primario-700 px-4 py-2 text-sm font-semibold text-white hover:bg-primario-800 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primario-700"
          >
            Dar de alta parque
          </Link>
        )}
      </div>

      <Aviso tipo="exito">{mensajeFlash}</Aviso>

      <section aria-label="Resumen" className="grid grid-cols-2 gap-3 md:grid-cols-4">
        <Indicador titulo="Parques activos" valor={resumen.activos} />
        <Indicador titulo="Con criterios atrasados" valor={resumen.conAtraso} alerta />
        <Indicador titulo="Actualización anual vencida" valor={resumen.actualizacionVencida} alerta />
        <Indicador titulo="Obligatorios por debajo de 50 %" valor={resumen.bajoMeta} alerta />
      </section>

      <form className="grid grid-cols-1 gap-3 rounded-lg border border-gray-300 bg-white p-4 sm:grid-cols-2 lg:grid-cols-4" aria-label="Filtros">
        <CampoSelect id="f-generacion" etiqueta="Generación" vacio="Todas" value={filtros.generacionId}
          onChange={cambiar('generacionId')} opciones={generaciones.map((g) => [g.id, g.nombre])} />
        <CampoSelect id="f-region" etiqueta="Región" vacio="Todas" value={filtros.region}
          onChange={cambiar('region')} opciones={ordenarPorEtiqueta(REGIONES)} />
        <CampoSelect id="f-estado" etiqueta="Estado" vacio="Activos" value={filtros.estado}
          onChange={cambiar('estado')} opciones={[['inactivo', 'Dados de baja'], ['historico', 'Históricos']]} />
        <CampoSelect id="f-atrasado" etiqueta="Actualización anual" vacio="Todas" value={filtros.atrasado}
          onChange={cambiar('atrasado')} opciones={[['true', 'Vencida'], ['false', 'Al día']]} />
      </form>

      <Aviso tipo="error">{error && mensajeDeError(error)}</Aviso>

      {parques === null ? (
        <Cargando texto="Cargando parques…" />
      ) : parques.length === 0 ? (
        !error && <p className="rounded-lg border border-dashed border-gray-400 p-8 text-center text-sm text-gray-600">
          No hay parques con estos filtros.
        </p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-gray-300 bg-white shadow-sm">
          <table className="w-full min-w-[900px] text-left text-sm">
            <caption className="sr-only">Parques con su fase, cumplimiento y atrasos</caption>
            <thead className="border-b border-gray-300 bg-gray-50 text-xs uppercase tracking-wide text-gray-700">
              <tr>
                <th scope="col" className="px-4 py-3">Parque</th>
                <th scope="col" className="px-4 py-3">Región</th>
                <th scope="col" className="px-4 py-3">Generación</th>
                <th scope="col" className="px-4 py-3">Fase</th>
                <th scope="col" className="px-4 py-3">Obligatorios cumplidos</th>
                <th scope="col" className="px-4 py-3">Atrasos</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {parques.map((p) => (
                <FilaParque key={p.id} parque={p} extra={extra[p.id]} generacion={nombreGeneracion[p.generacionId]} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  )
}

function Indicador({ titulo, valor, alerta = false }) {
  return (
    <div className="rounded-lg border border-gray-300 bg-white p-4 shadow-sm">
      <p className="text-xs font-medium text-gray-600">{titulo}</p>
      <p className={`mt-1 text-2xl font-bold tabular-nums ${alerta && valor > 0 ? 'text-red-700' : 'text-gray-900'}`}>
        {valor}
      </p>
    </div>
  )
}

function FilaParque({ parque: p, extra = {}, generacion }) {
  return (
    <tr className="hover:bg-gray-50">
      <td className="px-4 py-3">
        <Link to={`/parques/${p.id}`} className="font-semibold text-primario-700 underline-offset-2 hover:underline focus-visible:outline-2 focus-visible:outline-primario-700">
          {p.nombre}
        </Link>
        <div className="text-xs text-gray-600">
          {p.desarrollador ?? 'Sin desarrollador'}{p.tipoPI && ` · ${TIPOS_PI[p.tipoPI]}`}
        </div>
      </td>
      <td className="px-4 py-3">{REGIONES[p.region]}</td>
      <td className="px-4 py-3">{generacion ?? '—'}</td>
      <td className="px-4 py-3">
        {p.estado !== 'activo' ? (
          <Etiqueta tono="gris">{ESTADOS_PARQUE[p.estado]}</Etiqueta>
        ) : p.fase ? (
          <span>
            <span className="text-gray-600 tabular-nums">{ORDEN_FASE[p.fase]}/9</span> {FASES[p.fase]}
          </span>
        ) : '—'}
      </td>
      <td className="px-4 py-3">
        {extra.obligatorios === undefined ? <span className="text-gray-600">—</span> : (
          <BarraAvance valor={extra.obligatorios} etiqueta={`Obligatorios cumplidos de ${p.nombre}`} />
        )}
      </td>
      <td className="px-4 py-3">
        <div className="flex flex-wrap gap-1">
          {extra.atrasados > 0 && (
            <Etiqueta tono="rojo">{extra.atrasados} {extra.atrasados === 1 ? 'criterio atrasado' : 'criterios atrasados'}</Etiqueta>
          )}
          {p.atrasadoActualizacion && <Etiqueta tono="ambar">Actualización anual vencida</Etiqueta>}
          {p.estado === 'activo' && !extra.atrasados && !p.atrasadoActualizacion && extra.atrasados !== undefined && (
            <Etiqueta tono="verde">Al día</Etiqueta>
          )}
        </div>
      </td>
    </tr>
  )
}
