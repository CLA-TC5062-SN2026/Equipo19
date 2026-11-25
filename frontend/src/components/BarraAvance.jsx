/** Barra de porcentaje con el valor en texto (el color nunca es la única señal). */
export default function BarraAvance({ valor, etiqueta }) {
  if (valor === null || valor === undefined) return <span className="text-gray-600">N/A</span>
  const color = valor >= 80 ? 'bg-green-700' : valor >= 50 ? 'bg-amber-500' : 'bg-red-700'
  return (
    <div className="flex items-center gap-2">
      <div
        className="h-2 w-24 overflow-hidden rounded-full bg-gray-200"
        role="progressbar"
        aria-valuenow={Math.round(valor)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={etiqueta}
      >
        <div className={`h-full ${color}`} style={{ width: `${Math.min(100, valor)}%` }} />
      </div>
      <span className="w-12 shrink-0 text-right tabular-nums">{Math.round(valor)} %</span>
    </div>
  )
}
