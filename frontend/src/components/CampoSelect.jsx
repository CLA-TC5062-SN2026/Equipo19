/**
 * Lista de opciones con etiqueta y error asociado (mismo patrón de accesibilidad que CampoEntrada).
 * @param {{id: string, etiqueta: string, opciones: [string, string][], error?: string, requerido?: boolean,
 *          vacio?: string}} props  `opciones` es [valor, texto]; `vacio` agrega una opción sin valor al inicio.
 */
export default function CampoSelect({ id, etiqueta, opciones, error, requerido = false, vacio, ...resto }) {
  const idError = `${id}-error`
  return (
    <div className="flex w-full flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium text-gray-900">
        {etiqueta}
        {requerido && <span className="ml-1 text-red-700" aria-hidden="true">*</span>}
      </label>
      <select
        id={id}
        required={requerido}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? idError : undefined}
        className={`min-h-11 w-full rounded-md border bg-white px-3 py-2 text-sm text-gray-900
          focus-visible:outline-2 focus-visible:outline-offset-1
          ${error ? 'border-red-700 focus-visible:outline-red-700' : 'border-gray-500 focus-visible:outline-primario-700'}`}
        {...resto}
      >
        {vacio !== undefined && <option value="">{vacio}</option>}
        {opciones.map(([valor, texto]) => (
          <option key={valor} value={valor}>{texto}</option>
        ))}
      </select>
      {error && <p id={idError} className="text-sm font-medium text-red-700">{error}</p>}
    </div>
  )
}
