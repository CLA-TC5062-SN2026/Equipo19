import { useId } from 'react'

/**
 * Contenedor genérico para información estructurada (expediente, criterios, resúmenes).
 *
 * @param {object} props
 * @param {string} [props.titulo] Encabezado de la tarjeta; se asocia con aria-labelledby.
 * @param {React.ReactNode} [props.acciones] Botones o enlaces alineados al encabezado.
 * @param {React.ReactNode} [props.pie] Contenido secundario separado por un borde.
 */
export default function Tarjeta({ titulo, acciones, pie, children }) {
  const idTitulo = useId()

  return (
    <section
      aria-labelledby={titulo ? idTitulo : undefined}
      className="w-full rounded-lg border border-gray-300 bg-superficie shadow-sm"
    >
      {(titulo || acciones) && (
        <header className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-200 px-4 py-3 sm:px-6">
          {titulo && (
            <h2 id={idTitulo} className="text-base font-semibold text-gray-900">
              {titulo}
            </h2>
          )}
          {acciones && <div className="flex items-center gap-2">{acciones}</div>}
        </header>
      )}
      <div className="px-4 py-4 text-sm text-gray-900 sm:px-6">{children}</div>
      {pie && (
        <footer className="border-t border-gray-200 px-4 py-3 text-sm text-gray-600 sm:px-6">
          {pie}
        </footer>
      )}
    </section>
  )
}
