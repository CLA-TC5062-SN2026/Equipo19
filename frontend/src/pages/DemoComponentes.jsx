import { useState } from 'react'
import Boton from '../components/Boton'
import CampoEntrada from '../components/CampoEntrada'
import Tarjeta from '../components/Tarjeta'

/**
 * Página de demostración de la actividad S07-S08-A1: ejercita los cuatro
 * componentes esenciales con sus variantes y estados. Se sustituirá por las
 * pantallas reales del MVP (login, expediente, checklist) en las siguientes semanas.
 */
export default function DemoComponentes({ usuario, onSimularSesion }) {
  const [correo, setCorreo] = useState('')
  const [errorCorreo, setErrorCorreo] = useState('')
  const [enviando, setEnviando] = useState(false)

  function validarCorreo(valor) {
    if (!valor) return 'El correo es obligatorio.'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor)) {
      return 'Escribe un correo válido, por ejemplo nombre@parque.mx.'
    }
    return ''
  }

  function manejarEnvio(evento) {
    evento.preventDefault()
    const error = validarCorreo(correo)
    setErrorCorreo(error)
    if (error) return
    // Simula una llamada al API para mostrar el estado de carga del botón.
    setEnviando(true)
    setTimeout(() => {
      setEnviando(false)
      onSimularSesion()
    }, 1200)
  }

  return (
    <main id="contenido" className="mx-auto flex max-w-5xl flex-col gap-6 px-4 py-8 sm:px-6">
      <h1 className="text-2xl font-bold text-gray-900">
        Componentes esenciales de SGPIS
      </h1>
      <p className="max-w-prose text-sm text-gray-600">
        Demostración de los cuatro componentes base (botón, campo de entrada,
        tarjeta y barra de navegación) sobre los que se construirán las
        pantallas del MVP. La barra de arriba cambia según haya o no sesión.
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        <Tarjeta
          titulo="Botón"
          pie="Variantes primario y secundario; el estado de carga bloquea el click y lo anuncia con aria-busy."
        >
          <div className="flex flex-wrap items-center gap-3">
            <Boton variante="primario">Guardar</Boton>
            <Boton variante="secundario">Cancelar</Boton>
            <Boton variante="primario" cargando>
              Guardando…
            </Boton>
            <Boton variante="secundario" disabled>
              Deshabilitado
            </Boton>
          </div>
        </Tarjeta>

        <Tarjeta
          titulo="Campo de entrada"
          pie="La validación se muestra al enviar; el error queda asociado al campo con aria-describedby."
        >
          <form className="flex flex-col gap-4" onSubmit={manejarEnvio} noValidate>
            <CampoEntrada
              id="correo"
              etiqueta="Correo electrónico"
              tipo="email"
              requerido
              ayuda="El correo con el que Coordinación AMPIP dio de alta tu cuenta."
              placeholder="nombre@parque.mx"
              value={correo}
              onChange={(e) => setCorreo(e.target.value)}
              error={errorCorreo}
            />
            <Boton tipo="submit" variante="primario" cargando={enviando} anchoCompleto>
              {usuario ? 'Sesión simulada activa' : 'Simular inicio de sesión'}
            </Boton>
          </form>
        </Tarjeta>
      </div>

      <Tarjeta
        titulo="Parque Industrial El Bajío"
        acciones={<Boton variante="secundario">Ver expediente</Boton>}
        pie="Última actividad: carga de evidencia del criterio 2.8.1, hace 2 días."
      >
        <dl className="grid gap-x-8 gap-y-2 sm:grid-cols-3">
          <div>
            <dt className="font-medium text-gray-600">Tipo de PI</dt>
            <dd>Operación cerrado</dd>
          </div>
          <div>
            <dt className="font-medium text-gray-600">Fase</dt>
            <dd>Plan de trabajo</dd>
          </div>
          <div>
            <dt className="font-medium text-gray-600">Cumplimiento</dt>
            <dd>62 % de criterios obligatorios</dd>
          </div>
        </dl>
      </Tarjeta>
    </main>
  )
}
