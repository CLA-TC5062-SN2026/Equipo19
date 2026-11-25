const TONOS = {
  gris: 'bg-gray-100 text-gray-800 ring-gray-300',
  rojo: 'bg-red-50 text-red-800 ring-red-300',
  verde: 'bg-green-50 text-green-800 ring-green-300',
  ambar: 'bg-amber-50 text-amber-900 ring-amber-300',
  azul: 'bg-blue-50 text-primario-800 ring-blue-300',
}

export default function Etiqueta({ tono = 'gris', children }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${TONOS[tono]}`}>
      {children}
    </span>
  )
}
