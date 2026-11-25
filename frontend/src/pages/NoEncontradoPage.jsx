import { Link } from 'react-router'

export default function NoEncontradoPage() {
  return (
    <main id="contenido" className="mx-auto max-w-md px-4 py-16 text-center">
      <h1 className="text-2xl font-bold text-gray-900">Página no encontrada</h1>
      <p className="mt-2 text-sm text-gray-600">La dirección no corresponde a ninguna pantalla de SGPIS.</p>
      <Link to="/" className="mt-6 inline-block font-semibold text-primario-700 hover:underline">Ir a parques</Link>
    </main>
  )
}
