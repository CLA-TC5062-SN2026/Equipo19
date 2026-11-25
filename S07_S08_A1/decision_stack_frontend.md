# Decisión de stack de frontend

**Proyecto:** SGPIS, Sistema de Gestión del Programa Parque Industrial Seguro (AMPIP). Equipo 19, TC5062
**Actividad:** S07-S08-A1, Generación de Componentes Frontend (Parte 0)
**Fecha:** 5 de noviembre de 2026
**Insumos:** `S03_A1/SRS_equipo.md` v2.0, `S04_A1/decision_arquitectonica.md` (ADR-001), `S04_A2/openapi.yaml` (contrato del API)

---

## 1. Stack elegido

| Capa | Elección | Versión |
|---|---|---|
| Framework / librería de UI | **React** (SPA, con JavaScript + JSX) | 19.x |
| Herramienta de construcción / servidor de desarrollo | **Vite** | 7.x |
| Enfoque de estilos | **Tailwind CSS** (plugin `@tailwindcss/vite`) | 4.x |
| Manejo de estado | **Estado local de React + Context API** para la sesión (token JWT, usuario y rol). Sin librería adicional. | — |
| Variable de entorno del API | `VITE_API_URL` (valor de desarrollo: `http://localhost:8000/api/v1`) | — |

## 2. Propuestas de los integrantes y alternativas consideradas

Cada integrante propuso un stack de partida; el agente de IA se usó para comparar las dos opciones que quedaron en disputa (React + Vite contra Vue 3 + Vite) con los criterios de la sección 3.

| Alternativa | Quién la propuso / origen | Por qué se descartó |
|---|---|---|
| **Vue 3 + Vite + Pinia** | Propuesta de un integrante por su curva de aprendizaje suave y la buena documentación en español | Es la alternativa más cercana y no pierde por mérito técnico: para un CRUD con formularios y tablas, Vue rinde igual. Se descartó porque **ADR-001 ya documenta "una SPA en React consume una API REST"** y los diagramas C4 de S04-A1 lo reflejan; cambiarlo obligaría a reabrir una decisión arquitectónica aceptada sin que ningún RNF lo pida. Además la experiencia agregada del equipo es mayor en React, y Pinia sería una dependencia extra que el tamaño del estado (sesión + formularios) no justifica. |
| **Next.js (React con SSR/SSG)** | Considerada al evaluar si el dashboard de avance (RF-32) se beneficiaría de render en servidor | SGPIS es una aplicación interna con **cero páginas públicas**: todo va detrás de `Authorization: Bearer <token>` (ver convenciones de `openapi.yaml`), así que SEO y SSG no aportan nada. El SSR complica justo lo que nos importa: el manejo del token en cliente y el despliegue (necesitaría un proceso Node en producción, cuando el despliegue previsto en `diagrama_despliegue.puml` es una SPA estática servida junto al API). |
| **Angular** | Propuesta inicial de un integrante por traer "todo incluido" (router, HTTP, formularios, DI) | El costo de arranque es el más alto de las opciones (módulos/standalone, RxJS, inyección de dependencias) y nadie en el equipo lo ha usado más allá de tutoriales. Con 8.5 h/semana por persona y 22 RF de MVP pendientes (restricción de capacidad documentada en ADR-001), las horas de aprendizaje de Angular salen de horas de RF. |
| **Svelte + Vite** | Evaluada brevemente por su simplicidad y tamaño de bundle | Nadie del equipo la ha usado; el ecosistema de ejemplos para el patrón concreto que necesitamos (interceptor de 401, rutas protegidas por rol) es mucho menor que el de React, y el tamaño de bundle no es un RNF del proyecto (RNF-10 pide consultas en ≤ 3 s, que depende del API, no del framework). |
| **JavaScript vanilla + Fetch API** | Descartada en la discusión inicial | Con 6 roles, rutas protegidas y ~15 pantallas del MVP, mantener el DOM a mano multiplica el código de sincronización de estado. Es la opción con más riesgo de deuda para un equipo de 3. |
| **TypeScript en lugar de JavaScript** | Considerada porque el contrato `openapi.yaml` permitiría generar tipos | Aporta valor real (tipos generados del contrato), pero agrega fricción diaria a dos integrantes que no lo han usado. Decisión consciente de capacidad: JS + JSDoc en los servicios; si en S09 las pruebas revelan errores de forma de datos, se reevalúa. |
| **Bootstrap / CSS Modules / CSS puro** (estilos) | Bootstrap propuesto por familiaridad de un integrante | Bootstrap trae componentes ya diseñados pero impone su apariencia y agrega una capa de clases + su JS propio; los componentes de esta actividad (botón, input, card, navbar) son justo lo que Bootstrap daría hecho, y el objetivo del curso es construirlos. CSS Modules/CSS puro no se descartan del todo (Tailwind los permite en convivencia), pero como enfoque principal dispersan las decisiones de diseño (espaciado, colores, breakpoints) que Tailwind centraliza en tokens. |
| **Redux / Zustand** (estado) | Evaluadas al discutir dónde vive la sesión | El estado global real de SGPIS es pequeño: token + usuario + rol (y quizá el parque activo). Todo lo demás es estado de servidor que se vuelve a pedir al API. Redux/Zustand agregan concepto y boilerplate para un estado que un `AuthContext` de ~60 líneas cubre. Si el estado de servidor se vuelve doloroso (caché, refetch), la mejora natural sería TanStack Query, no Redux. |

## 3. Justificación en términos del proyecto

**Coherencia con la arquitectura ya aceptada.** ADR-001 (S04-A1) fijó "monolito modular… una SPA en React consume una API REST (FastAPI)" y los diagramas C4 de contenedores ya dibujan ese contenedor. Esta actividad ejecuta esa decisión en vez de contradecirla; el costo de cambiar de framework ahora sería rehacer documentación arquitectónica aceptada sin beneficio medible.

**Integración con el backend (API REST + JWT).** El contrato `openapi.yaml` define `Authorization: Bearer <token>` con sesiones revocables en servidor y expiración por 60 min de inactividad (RF-26). Eso dicta tres piezas de frontend que React + Context cubren con patrones muy documentados: un cliente HTTP único en `services/` que inyecta el header y traduce `application/problem+json` (RFC 9457), un `AuthContext` que guarda token/usuario/rol, y un redirect global a login cuando cualquier respuesta es 401 (sesión revocada o vencida). Ningún framework hace esto "mejor"; React lo hace con lo que el equipo ya sabe.

**Características del equipo.** Tres integrantes, 8.5 h/semana, Sprint 1 ya consumió parte del presupuesto de horas (ADR-001). React es la tecnología con más experiencia acumulada del equipo y la que usamos en la actividad 0 de esta semana, así que el costo de arranque es el mínimo de todas las opciones. Vite da el servidor de desarrollo con recarga instantánea y el build estático que pide el despliegue previsto.

**Complejidad real del UI.** El MVP es un sistema de gestión: formularios con validación (alta de parques y usuarios, autoevaluación), tablas con estados (checklist de criterios O/R/NA, evidencias enviada/observada/aceptada), carga de archivos de hasta 100 MB con progreso (RNF-07/RNF-18) y un dashboard de fases (RF-32). No hay animación compleja ni documentos colaborativos: es exactamente el terreno de React + Tailwind. Tailwind además deja los criterios de accesibilidad (contraste 4.5:1, foco visible) como decisiones explícitas de tokens y clases `focus-visible:*`, que la Parte 3 de esta actividad audita.

**Qué nos haría reconsiderar.** Si el equipo creciera o el estado de servidor se complicara: TanStack Query para caché de API. Si los errores de integración por formas de datos se repitieran en S09: migrar `services/` a TypeScript generando tipos desde `openapi.yaml`. Ninguno de los dos cambios tocaría la elección de React + Vite + Tailwind.
