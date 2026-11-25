const VARIANTES = {
  primario:
    'bg-primario-700 text-white hover:bg-primario-800 active:bg-primario-800',
  secundario:
    'border border-gray-500 bg-white text-gray-900 hover:bg-gray-100 active:bg-gray-200',
  peligro: 'bg-red-700 text-white hover:bg-red-800 active:bg-red-800',
}

/**
 * Botón de SGPIS.
 *
 * @param {object} props
 * @param {'primario' | 'secundario' | 'peligro'} [props.variante]
 * @param {boolean} [props.cargando] Muestra un spinner, anuncia aria-busy y bloquea el click.
 * @param {'button' | 'submit' | 'reset'} [props.tipo]
 * @param {boolean} [props.anchoCompleto] Ocupa todo el ancho disponible (útil en móvil).
 * @param {boolean} [props.sobreOscuro] Anillo de foco blanco, para botones sobre la barra azul (WCAG 2.4.7).
 */
export default function Boton({
  variante = 'primario',
  cargando = false,
  tipo = 'button',
  anchoCompleto = false,
  sobreOscuro = false,
  disabled = false,
  children,
  ...resto
}) {
  return (
    <button
      type={tipo}
      disabled={disabled || cargando}
      aria-busy={cargando || undefined}
      className={`inline-flex min-h-11 items-center justify-center gap-2 rounded-md px-4 py-2 text-sm font-semibold
        transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 ${sobreOscuro ? 'focus-visible:outline-white' : 'focus-visible:outline-primario-700'}
        disabled:cursor-not-allowed disabled:opacity-60
        ${VARIANTES[variante]} ${anchoCompleto ? 'w-full' : ''}`}
      {...resto}
    >
      {cargando && (
        <svg
          className="size-4 animate-spin"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-90" fill="currentColor" d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z" />
        </svg>
      )}
      {children}
    </button>
  )
}
