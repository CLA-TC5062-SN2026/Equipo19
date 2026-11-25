// Parques y su expediente (RF-02, RF-07, RF-08, RF-09, RF-10, RF-29, RF-30, RF-32).
import { api } from './api'

export const listarParques = (filtros = {}) =>
  api('/parques', { consulta: { tamanoPagina: 100, ...filtros } })

export const obtenerParque = (id) => api(`/parques/${id}`)

export const crearParque = (datos) =>
  api('/parques', { metodo: 'POST', cuerpo: { tipoRegistro: 'activo', ...datos } })

export const actualizarParque = (id, cambios) =>
  api(`/parques/${id}`, { metodo: 'PATCH', cuerpo: cambios })

export const darDeBajaParque = (id, motivo) =>
  api(`/parques/${id}`, { metodo: 'PATCH', cuerpo: { estado: 'inactivo', motivo } })

export const obtenerCumplimiento = (id) => api(`/parques/${id}/cumplimiento`)

export const listarFases = (id) => api(`/parques/${id}/fases`)

export const listarCriteriosParque = (id) =>
  api(`/parques/${id}/criterios`, { consulta: { tamanoPagina: 100 } })

export const listarAsignaciones = (id) => api(`/parques/${id}/asignaciones-consultor`)

export const listarGeneraciones = () => api('/generaciones')
