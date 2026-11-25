// Etiquetas en español de los valores cerrados del contrato (enums de openapi_equipo.yaml).

export const REGIONES = {
  'MX-AGU': 'Aguascalientes', 'MX-BCN': 'Baja California', 'MX-BCS': 'Baja California Sur',
  'MX-CAM': 'Campeche', 'MX-CHP': 'Chiapas', 'MX-CHH': 'Chihuahua', 'MX-CMX': 'Ciudad de México',
  'MX-COA': 'Coahuila', 'MX-COL': 'Colima', 'MX-DUR': 'Durango', 'MX-GUA': 'Guanajuato', 'MX-GRO': 'Guerrero',
  'MX-HID': 'Hidalgo', 'MX-JAL': 'Jalisco', 'MX-MEX': 'Estado de México', 'MX-MIC': 'Michoacán',
  'MX-MOR': 'Morelos', 'MX-NAY': 'Nayarit', 'MX-NLE': 'Nuevo León', 'MX-OAX': 'Oaxaca', 'MX-PUE': 'Puebla',
  'MX-QUE': 'Querétaro', 'MX-ROO': 'Quintana Roo', 'MX-SLP': 'San Luis Potosí', 'MX-SIN': 'Sinaloa',
  'MX-SON': 'Sonora', 'MX-TAB': 'Tabasco', 'MX-TAM': 'Tamaulipas', 'MX-TLA': 'Tlaxcala', 'MX-VER': 'Veracruz',
  'MX-YUC': 'Yucatán', 'MX-ZAC': 'Zacatecas',
}

export const TIPOS_PI = {
  construccion_abierto: 'Construcción · abierto',
  construccion_cerrado: 'Construcción · cerrado',
  operacion_abierto: 'Operación · abierto',
  operacion_cerrado: 'Operación · cerrado',
}

export const ROLES = {
  coordinacion_ampip: 'Coordinación AMPIP',
  director_general_ampip: 'Dirección General AMPIP',
  appi: 'APPI',
  consultor: 'Consultor',
  gerente_corporativo: 'Gerente corporativo',
  administrador_tecnico: 'Administración técnica',
}

export const FASES = {
  diagnostico: 'Diagnóstico',
  plan_trabajo: 'Plan de trabajo',
  politica_seguridad: 'Política de seguridad',
  analisis_riesgos: 'Análisis de riesgos',
  implementacion_estandares: 'Implementación de estándares',
  opinion_intermedia_emitida: 'Opinión intermedia',
  opinion_final_emitida: 'Opinión final',
  evaluacion_desempeno: 'Evaluación de desempeño',
  dictamen: 'Dictamen',
}
export const ORDEN_FASE = Object.fromEntries(Object.keys(FASES).map((f, i) => [f, i + 1]))

export const ESTADOS_PARQUE = { activo: 'Activo', inactivo: 'Dado de baja', historico: 'Histórico' }

export const ESTADOS_CALIFICACION = {
  pendiente: 'Pendiente',
  en_revision: 'En revisión',
  cumplido: 'Cumplido',
  no_cumplido: 'No cumplido',
}

export const ordenarPorEtiqueta = (mapa) =>
  Object.entries(mapa).sort(([, a], [, b]) => a.localeCompare(b, 'es'))
