/**
 * Campo de entrada con etiqueta y validación visual.
 *
 * El mensaje de error se asocia al input con aria-describedby y aria-invalid,
 * para que un lector de pantalla lo anuncie junto con el campo (WCAG 3.3.1).
 *
 * @param {object} props
 * @param {string} props.id Obligatorio: asocia label e input.
 * @param {string} props.etiqueta Texto visible del label.
 * @param {string} [props.tipo]
 * @param {string} [props.error] Mensaje de validación; su presencia marca el campo como inválido.
 * @param {string} [props.ayuda] Texto de apoyo bajo el campo (formato esperado, etc.).
 * @param {boolean} [props.requerido]
 */
export default function CampoEntrada({
  id,
  etiqueta,
  tipo = 'text',
  error,
  ayuda,
  requerido = false,
  ...resto
}) {
  const idError = `${id}-error`
  const idAyuda = `${id}-ayuda`
  const describedBy =
    [error && idError, ayuda && idAyuda].filter(Boolean).join(' ') || undefined

  return (
    <div className="flex w-full flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-gray-900">
        {etiqueta}
        {requerido && (
          <span className="ml-1 text-red-700" aria-hidden="true">*</span>
        )}
      </label>
      <input
        id={id}
        type={tipo}
        required={requerido}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
        className={`min-h-11 w-full rounded-md border bg-white px-3 py-2 text-sm text-gray-900
          placeholder:text-gray-600
          focus-visible:outline-2 focus-visible:outline-offset-1
          ${
            error
              ? 'border-red-700 focus-visible:outline-red-700'
              : 'border-gray-500 focus-visible:outline-primario-700'
          }`}
        {...resto}
      />
      {ayuda && (
        <p id={idAyuda} className="text-sm text-gray-600">
          {ayuda}
        </p>
      )}
      {error && (
        <p id={idError} className="text-sm font-medium text-red-700">
          {error}
        </p>
      )}
    </div>
  )
}
