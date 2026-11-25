import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router'
import Aviso from '../components/Aviso'
import BarraAvance from '../components/BarraAvance'
import Boton from '../components/Boton'
import CampoEntrada from '../components/CampoEntrada'
import CampoSelect from '../components/CampoSelect'
import Cargando from '../components/Cargando'
import Etiqueta from '../components/Etiqueta'
import Tarjeta from '../components/Tarjeta'
import { ESTADOS_CALIFICACION, ESTADOS_PARQUE, REGIONES, TIPOS_PI, ordenarPorEtiqueta } from '../lib/catalogos'
import { erroresPorCampo, mensajeDeError } from '../lib/errores'
import { fecha, porcentaje } from '../lib/formato'
import {
  actualizarParque,
  darDeBajaParque,
  listarAsignaciones,
  listarCriteriosParque,
  listarFases,
  listarGeneraciones,
  obtenerCumplimiento,
  obtenerParque,
} from '../services/parques'
import { useSesion } from '../sesion/contexto'

const valorDe = (resultado) => (resultado.status === 'fulfilled' ? resultado.value : null)

async function cargarExpediente(parqueId) {
  const p = await obtenerParque(parqueId)
  if (p.tipoRegistro !== 'activo') return { p, detalle: {} }
  // Cada sección se pide por separado: si el rol no puede ver una (403), las demás se muestran igual.
  const [cumplimiento, fases, criterios, asignaciones, generaciones] = await Promise.allSettled([
    obtenerCumplimiento(parqueId), listarFases(parqueId), listarCriteriosParque(parqueId),
    listarAsignaciones(parqueId), listarGeneraciones(),
  ])
  return {
    p,
    detalle: {
      cumplimiento: valorDe(cumplimiento),
      fases: valorDe(fases),
      criterios: valorDe(criterios)?.items ?? null,
      consultor: valorDe(asignaciones)?.find((a) => a.vigente)?.consultorNombre,
      generacion: valorDe(generaciones)?.find((g) => g.id === p.generacionId)?.nombre,
    },
  }
}

/** Expediente de un parque: datos, avance (RF-08), fases (RF-32), criterios con atraso (RF-09), edición y baja. */
export default function ParqueDetallePage() {
  const { parqueId } = useParams()
  const { usuario } = useSesion()
  const esCoordinacion = usuario.rol === 'coordinacion_ampip'
  const ubicacion = useLocation()
  const [mensaje, setMensaje] = useState(ubicacion.state?.mensaje ?? '')
  const [parque, setParque] = useState(null)
  const [detalle, setDetalle] = useState({})
  const [error, setError] = useState(null)
  const [modo, setModo] = useState('ver') // ver | editar | baja

  const [version, setVersion] = useState(0) // sube tras guardar para volver a pedir el expediente

  useEffect(() => {
    let vigente = true
    cargarExpediente(parqueId)
      .then(({ p, detalle: d }) => {
        if (!vigente) return
        setError(null)
        setParque(p)
        setDetalle(d)
      })
      .catch((e) => vigente && setError(e))
    return () => {
      vigente = false
    }
  }, [parqueId, version])

  const alGuardar = (texto) => {
    setModo('ver')
    setMensaje(texto)
    setVersion((v) => v + 1)
  }

  if (error) {
    return (
      <main id="contenido" className="mx-auto max-w-6xl px-4 py-8 sm:px-6">
        <Link to="/" className="text-sm text-primario-700 hover:underline">← Parques</Link>
        <div className="mt-4"><Aviso tipo="error">{mensajeDeError(error)}</Aviso></div>
      </main>
    )
  }
  if (!parque) return <main id="contenido" className="mx-auto max-w-6xl px-4 sm:px-6"><Cargando texto="Cargando expediente…" /></main>

  const activo = parque.estado === 'activo'
  return (
    <main id="contenido" className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link to="/" className="text-sm text-primario-700 hover:underline">← Parques</Link>
          <h1 className="mt-2 flex flex-wrap items-center gap-3 text-2xl font-bold text-gray-900">
            {parque.nombre}
            <Etiqueta tono={activo ? 'verde' : 'gris'}>{ESTADOS_PARQUE[parque.estado]}</Etiqueta>
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            {parque.desarrollador ?? 'Parque histórico'} · {REGIONES[parque.region]}
          </p>
        </div>
        {esCoordinacion && activo && modo === 'ver' && (
          <div className="flex gap-2">
            <Boton variante="secundario" onClick={() => { setMensaje(''); setModo('editar') }}>Editar datos</Boton>
            <Boton variante="peligro" onClick={() => { setMensaje(''); setModo('baja') }}>Dar de baja</Boton>
          </div>
        )}
      </div>

      <Aviso tipo="exito">{mensaje}</Aviso>

      {modo === 'editar' && <FormEdicion parque={parque} onCancelar={() => setModo('ver')} onGuardado={alGuardar} />}
      {modo === 'baja' && <FormBaja parque={parque} onCancelar={() => setModo('ver')} onGuardado={alGuardar} />}

      <Tarjeta titulo="Datos del parque">
        <dl className="grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
          <Dato termino="Tipo de PI" valor={TIPOS_PI[parque.tipoPI] ?? '—'} />
          <Dato termino="Generación" valor={detalle.generacion ?? '—'} />
          <Dato termino="Consultor asignado" valor={detalle.consultor ?? (parque.consultorAsignadoId ? 'Asignado' : 'Sin asignar')} />
          <Dato termino="Fecha de alta" valor={fecha(parque.fechaAlta)} />
          <Dato termino="Término del programa" valor={fecha(parque.fechaTerminoPrograma ?? null)} />
          <Dato
            termino="Próxima actualización anual"
            valor={<span className="flex items-center gap-2">{fecha(parque.fechaProximaActualizacion)}
              {parque.atrasadoActualizacion && <Etiqueta tono="ambar">Vencida</Etiqueta>}</span>}
          />
          {parque.tipoRegistro === 'historico' && <Dato termino="Último dictamen" valor={fecha(parque.fechaUltimoDictamen)} />}
          {parque.motivoBaja && <Dato termino="Motivo de la baja" valor={parque.motivoBaja} />}
        </dl>
      </Tarjeta>

      {parque.tipoRegistro === 'activo' && (
        <>
          <SeccionCumplimiento cumplimiento={detalle.cumplimiento} />
          <SeccionFases fases={detalle.fases} />
          <SeccionCriterios criterios={detalle.criterios} />
        </>
      )}
    </main>
  )
}

function Dato({ termino, valor }) {
  return (
    <div>
      <dt className="text-xs font-medium text-gray-600">{termino}</dt>
      <dd className="mt-0.5 text-sm text-gray-900">{valor}</dd>
    </div>
  )
}

function SeccionCumplimiento({ cumplimiento: c }) {
  if (c === undefined) return <Cargando />
  if (c === null) return null
  const t = c.total
  return (
    <Tarjeta titulo="Cumplimiento" pie="Los porcentajes se calculan sumando criterios de los 10 estándares, nunca promediando porcentajes (RF-08).">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <Cifra titulo="Obligatorios cumplidos" valor={porcentaje(t.porcentajeObligatorios)}
          detalle={`${t.obligatoriosCumplidos} de ${t.obligatoriosAplicables}`} />
        <Cifra titulo="Recomendados cumplidos" valor={porcentaje(t.porcentajeRecomendados)}
          detalle={`${t.recomendadosCumplidos} de ${t.recomendadosAplicables}`} />
        <Cifra titulo="Avance general" valor={porcentaje(t.porcentajeAvanceGeneral)}
          detalle={`${t.obligatoriosCumplidos + t.recomendadosCumplidos} de ${t.obligatoriosAplicables + t.recomendadosAplicables}`} />
      </div>
      <div className="mt-6 overflow-x-auto">
        <table className="w-full min-w-[520px] text-left text-sm">
          <caption className="sr-only">Cumplimiento por estándar</caption>
          <thead className="border-b border-gray-300 text-xs uppercase tracking-wide text-gray-700">
            <tr>
              <th scope="col" className="py-2 pr-4">Estándar</th>
              <th scope="col" className="py-2 pr-4">Obligatorios</th>
              <th scope="col" className="py-2 pr-4">Recomendados</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {c.porEstandar.filter((e) => !e.noAplica).map((e) => (
              <tr key={e.estandar}>
                <th scope="row" className="py-2 pr-4 font-medium">Estándar {e.estandar}</th>
                <td className="py-2 pr-4">
                  <div className="flex items-center gap-3">
                    <BarraAvance valor={e.porcentajeObligatorios} etiqueta={`Obligatorios del estándar ${e.estandar}`} />
                    <span className="text-xs text-gray-600">{e.obligatoriosCumplidos}/{e.obligatoriosAplicables}</span>
                  </div>
                </td>
                <td className="py-2 pr-4 text-gray-700">
                  {e.recomendadosAplicables ? `${e.recomendadosCumplidos}/${e.recomendadosAplicables}` : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Tarjeta>
  )
}

function Cifra({ titulo, valor, detalle }) {
  return (
    <div className="rounded-md bg-gray-50 p-4">
      <p className="text-xs font-medium text-gray-600">{titulo}</p>
      <p className="mt-1 text-3xl font-bold tabular-nums text-gray-900">{valor}</p>
      <p className="text-xs text-gray-600">{detalle} criterios</p>
    </div>
  )
}

const TONO_FASE = { completada: 'verde', en_proceso: 'azul', avanzada_por_excepcion: 'ambar', pendiente: 'gris' }
const TEXTO_FASE = { completada: 'Completada', en_proceso: 'En curso', avanzada_por_excepcion: 'Por excepción', pendiente: 'Pendiente' }

function SeccionFases({ fases }) {
  if (!fases) return null
  return (
    <Tarjeta titulo="Fases del programa">
      <ol className="grid grid-cols-1 gap-2 sm:grid-cols-3 lg:grid-cols-9">
        {fases.map((f) => (
          <li key={f.fase} aria-current={f.actual ? 'step' : undefined}
            className={`flex flex-col gap-1 rounded-md border p-2 ${f.actual ? 'border-primario-700 bg-blue-50' : 'border-gray-200'}`}>
            <span className="text-xs text-gray-600 tabular-nums">{f.orden}</span>
            <span className="text-xs font-medium leading-tight text-gray-900">{f.nombre}</span>
            <Etiqueta tono={TONO_FASE[f.estado]}>{TEXTO_FASE[f.estado]}</Etiqueta>
          </li>
        ))}
      </ol>
    </Tarjeta>
  )
}

const TONO_CALIFICACION = { cumplido: 'verde', no_cumplido: 'rojo', en_revision: 'azul', pendiente: 'gris' }

function SeccionCriterios({ criterios }) {
  const [soloPendientes, setSoloPendientes] = useState(true)
  if (!criterios) return null
  const visibles = criterios
    .filter((c) => !soloPendientes || c.estadoCalificacion !== 'cumplido')
    .sort((a, b) => Number(b.atrasado) - Number(a.atrasado) || a.clave.localeCompare(b.clave, 'es', { numeric: true }))
  return (
    <Tarjeta
      titulo={`Criterios aplicables (${criterios.length})`}
      acciones={
        <label className="flex items-center gap-2 text-sm text-gray-900">
          <input type="checkbox" className="size-4 accent-primario-700" checked={soloPendientes}
            onChange={(e) => setSoloPendientes(e.target.checked)} />
          Ocultar cumplidos
        </label>
      }
    >
      <div className="overflow-x-auto">
        <table className="w-full min-w-[640px] text-left text-sm">
          <caption className="sr-only">Criterios del parque con su estado</caption>
          <thead className="border-b border-gray-300 text-xs uppercase tracking-wide text-gray-700">
            <tr>
              <th scope="col" className="py-2 pr-3">Clave</th>
              <th scope="col" className="py-2 pr-3">Criterio</th>
              <th scope="col" className="py-2 pr-3">Tipo</th>
              <th scope="col" className="py-2 pr-3">Estado</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {visibles.map((c) => (
              <tr key={c.criterioId}>
                <td className="py-2 pr-3 tabular-nums text-gray-700">{c.clave}</td>
                <td className="py-2 pr-3">{c.texto}</td>
                <td className="py-2 pr-3">{c.marca === 'O' ? 'Obligatorio' : 'Recomendado'}</td>
                <td className="py-2 pr-3">
                  <div className="flex flex-wrap gap-1">
                    <Etiqueta tono={TONO_CALIFICACION[c.estadoCalificacion]}>{ESTADOS_CALIFICACION[c.estadoCalificacion]}</Etiqueta>
                    {c.atrasado && <Etiqueta tono="rojo">Atrasado</Etiqueta>}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Tarjeta>
  )
}

/** PATCH /parques/{id} con solo los campos que cambiaron (RF-30 para las fechas). */
function FormEdicion({ parque, onCancelar, onGuardado }) {
  const inicial = {
    nombre: parque.nombre,
    desarrollador: parque.desarrollador ?? '',
    region: parque.region,
    fechaTerminoPrograma: parque.fechaTerminoPrograma ?? '',
    fechaProximaActualizacion: parque.fechaProximaActualizacion ?? '',
  }
  const [datos, setDatos] = useState(inicial)
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)
  const [errores, setErrores] = useState({})
  const cambiar = (campo) => (e) => setDatos((d) => ({ ...d, [campo]: e.target.value }))

  async function enviar(evento) {
    evento.preventDefault()
    const cambios = {}
    for (const [campo, valor] of Object.entries(datos)) {
      if (valor !== inicial[campo]) cambios[campo] = typeof valor === 'string' ? valor.trim() || null : valor
    }
    if (!Object.keys(cambios).length) return onCancelar()
    if (cambios.nombre === null) return setErrores({ nombre: 'El nombre no puede quedar vacío.' })
    setEnviando(true)
    setError(null)
    try {
      await actualizarParque(parque.id, cambios)
      onGuardado('Se guardaron los cambios del parque.')
    } catch (e) {
      setError(e)
      setErrores(erroresPorCampo(e))
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Tarjeta titulo="Editar datos del parque">
      <form onSubmit={enviar} noValidate className="flex flex-col gap-4">
        <Aviso tipo="error">{error && mensajeDeError(error)}</Aviso>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <CampoEntrada id="e-nombre" etiqueta="Nombre" value={datos.nombre} onChange={cambiar('nombre')} error={errores.nombre} />
          <CampoEntrada id="e-desarrollador" etiqueta="Desarrollador" value={datos.desarrollador}
            onChange={cambiar('desarrollador')} error={errores.desarrollador} />
          <CampoSelect id="e-region" etiqueta="Región" opciones={ordenarPorEtiqueta(REGIONES)} value={datos.region}
            onChange={cambiar('region')} error={errores.region} />
          <CampoEntrada id="e-termino" etiqueta="Término del programa" tipo="date" value={datos.fechaTerminoPrograma}
            onChange={cambiar('fechaTerminoPrograma')} error={errores.fechaTerminoPrograma} />
          <CampoEntrada id="e-actualizacion" etiqueta="Próxima actualización anual" tipo="date"
            value={datos.fechaProximaActualizacion} onChange={cambiar('fechaProximaActualizacion')}
            error={errores.fechaProximaActualizacion}
            ayuda="Si la fecha ya pasó, el parque queda marcado con actualización vencida." />
        </div>
        <div className="flex justify-end gap-3">
          <Boton variante="secundario" onClick={onCancelar}>Cancelar</Boton>
          <Boton tipo="submit" cargando={enviando}>Guardar cambios</Boton>
        </div>
      </form>
    </Tarjeta>
  )
}

/**
 * Baja de parque (RF-29-AC-3). El motivo es obligatorio y lo valida el backend (422 motivo_requerido); el
 * parque sale del tablero pero su expediente se conserva y se puede consultar con el filtro "Dados de baja".
 */
function FormBaja({ parque, onCancelar, onGuardado }) {
  const [motivo, setMotivo] = useState('')
  const [enviando, setEnviando] = useState(false)
  const [error, setError] = useState(null)

  async function enviar(evento) {
    evento.preventDefault()
    setEnviando(true)
    setError(null)
    try {
      await darDeBajaParque(parque.id, motivo.trim() || null)
      onGuardado(`${parque.nombre} quedó dado de baja. Su expediente se conserva.`)
    } catch (e) {
      setError(e)
    } finally {
      setEnviando(false)
    }
  }

  const errorMotivo = error?.codigo === 'motivo_requerido' ? error.message : undefined
  return (
    <Tarjeta titulo="Dar de baja el parque">
      <form onSubmit={enviar} noValidate className="flex flex-col gap-4">
        <p className="text-sm text-gray-700">
          El parque deja de aparecer en el tablero y sus usuarios APPI pierden el acceso. El expediente y la
          bitácora se conservan.
        </p>
        {error && !errorMotivo && <Aviso tipo="error">{mensajeDeError(error)}</Aviso>}
        <div className="flex flex-col gap-1">
          <label htmlFor="motivo" className="text-sm font-medium text-gray-900">
            Motivo de la baja<span className="ml-1 text-red-700" aria-hidden="true">*</span>
          </label>
          <textarea id="motivo" rows={3} value={motivo} onChange={(e) => setMotivo(e.target.value)}
            aria-invalid={errorMotivo ? true : undefined} aria-describedby={errorMotivo ? 'motivo-error' : undefined}
            className={`w-full rounded-md border bg-white px-3 py-2 text-sm focus-visible:outline-2 focus-visible:outline-offset-1
              ${errorMotivo ? 'border-red-700 focus-visible:outline-red-700' : 'border-gray-500 focus-visible:outline-primario-700'}`} />
          {errorMotivo && <p id="motivo-error" role="alert" className="text-sm font-medium text-red-700">{errorMotivo}</p>}
        </div>
        <div className="flex justify-end gap-3">
          <Boton variante="secundario" onClick={onCancelar}>Cancelar</Boton>
          <Boton tipo="submit" variante="peligro" cargando={enviando}>Confirmar baja</Boton>
        </div>
      </form>
    </Tarjeta>
  )
}
