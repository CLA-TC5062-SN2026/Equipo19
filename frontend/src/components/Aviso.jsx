const ESTILOS = {
  error: 'border-red-700 bg-red-50 text-red-800',
  exito: 'border-green-700 bg-green-50 text-green-800',
  info: 'border-primario-700 bg-blue-50 text-primario-800',
}

/** Mensaje en línea. Los errores usan role="alert" para que el lector de pantalla los anuncie al aparecer. */
export default function Aviso({ tipo = 'info', children }) {
  if (!children) return null
  return (
    <div
      role={tipo === 'error' ? 'alert' : 'status'}
      className={`rounded-md border-l-4 px-4 py-3 text-sm ${ESTILOS[tipo]}`}
    >
      {children}
    </div>
  )
}
