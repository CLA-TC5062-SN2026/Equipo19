# Revisión de los componentes generados por el agente

**Proyecto:** SGPIS. Equipo 19, TC5062
**Actividad:** S07-S08-A1, Parte 2
**Componentes:** `frontend/src/components/Boton.jsx`, `CampoEntrada.jsx`, `Tarjeta.jsx`, `Navbar.jsx`, más `frontend/src/services/api.js` y `auth.js`
**Herramienta:** Claude Code

El agente generó una primera versión de los cuatro componentes a partir de `decision_stack_frontend.md` y del contrato `openapi.yaml`. Esta es la lista de lo que cambiamos de esa propuesta y por qué; lo que no aparece aquí se aceptó como venía.

## Cambios transversales

**1. Props y nombres de archivo en español.** La propuesta venía con la convención típica de React en inglés (`variant`, `loading`, `label`, `error`, `Button.jsx`). La cambiamos a `variante`, `cargando`, `etiqueta` y `Boton.jsx`/`CampoEntrada.jsx`/`Tarjeta.jsx` porque todo el vocabulario del proyecto ya está en español (el SRS, el contrato OpenAPI usa `pagina`/`por_pagina`/`datos`, los mensajes de error del backend vienen en español por contrato). Mantener dos idiomas mezclados en el código nos ha costado errores de dedo en actividades anteriores; `Navbar` se quedó así porque es el término que usa la propia actividad. Los atributos del DOM (`disabled`, `type`, `aria-*`) siguen en inglés porque son del estándar, no nuestros.

**2. Sin librería de iconos.** La propuesta importaba `lucide-react` para el spinner del botón y el icono de hamburguesa. Son dos iconos en todo el proyecto: los sustituimos por SVG inline y evitamos una dependencia que habría que auditar y actualizar. Si el MVP llega a necesitar más de ~5 iconos, reconsideramos.

**3. Área táctil mínima.** Agregamos `min-h-11` (44 px) a botones e inputs, que la propuesta no traía. Los usuarios APPI son gerentes de seguridad que van a usar el sistema también desde el celular en campo (el SRS descarta la app nativa, no el navegador móvil), y 44 px es la recomendación de WCAG 2.5.5 para objetivos táctiles.

## Botón (`Boton.jsx`)

**4. El texto no desaparece durante la carga.** La versión del agente reemplazaba `children` por el spinner mientras `cargando` era verdadero. Eso hace que el botón cambie de ancho (salto de layout) y que se pierda el contexto de qué se está haciendo. Lo cambiamos a spinner + texto visible, con `aria-busy` para tecnologías de asistencia, y `disabled` mientras carga para que no se pueda enviar dos veces el mismo formulario — relevante porque el backend responde 409 a duplicados y es mejor no provocarlos.

**5. `tipo` con valor por defecto `"button"`.** La propuesta no fijaba `type`, y un `<button>` sin `type` dentro de un `<form>` es `submit`: cualquier botón "Cancelar" dentro de un formulario lo habría enviado. Default explícito `tipo="button"` y `tipo="submit"` solo donde se pide.

## Campo de entrada (`CampoEntrada.jsx`)

**6. Componente controlado, sin estado interno.** La versión generada guardaba su propio `useState` del valor y validaba en cada tecla. Lo volvimos controlado (`value`/`onChange` vienen del formulario) y la validación se dispara al enviar, no al teclear: el dueño del estado es la pantalla, que es quien conoce las reglas (y las reglas reales van a venir del contrato: 422 con `application/problem+json`). Validar en cada tecla además regaña al usuario antes de que termine de escribir.

**7. `id` obligatorio en lugar de generado.** El agente generaba un id aleatorio por render. Lo hicimos prop obligatoria: el label se asocia con `htmlFor`, y los mensajes de error y ayuda se asocian con `aria-describedby` usando ids derivados (`{id}-error`, `{id}-ayuda`), que así quedan estables y legibles al depurar.

## Tarjeta (`Tarjeta.jsx`)

**8. `section` con `aria-labelledby` en lugar de `div` con `h3` fijo.** La propuesta usaba un `div` con un `<h3>` de nivel fijo. Usamos `<section>` etiquetada por su título (con `useId`) y dejamos el título como `h2`; cuando tengamos páginas con jerarquías más profundas evaluaremos hacer el nivel configurable. Agregamos los slots `acciones` (botones en el encabezado) y `pie`, porque las tarjetas reales del MVP (criterio del checklist, evidencia) llevan acciones y metadatos, no solo cuerpo.

## Barra de navegación (`Navbar.jsx`)

**9. La sesión llega por props, no de un contexto inventado.** La propuesta creaba y leía un `AuthContext` dentro del propio componente. Ese contexto aún no existe (llega con el login real, RF-26) y un componente que lee contexto es más difícil de probar y de mostrar en esta demo. `Navbar` recibe `usuario` (`null` = no autenticado) y los callbacks; cuando exista `AuthContext`, quien lo consuma será `App`, no la barra.

**10. Menú móvil accesible.** Al botón de hamburguesa (que venía solo con el icono) le agregamos nombre accesible (`sr-only`), `aria-expanded` y `aria-controls`; a los enlaces, `aria-current="page"` para el activo en lugar de solo el color de fondo. El detalle está en `accesibilidad.md`.

## Servicios (`services/api.js`, `services/auth.js`)

**11. `fetch` nativo en lugar de axios.** La propuesta traía axios con interceptores. Lo que necesitamos del interceptor son ~10 líneas (inyectar `Authorization`, traducir `problem+json`, avisar del 401) y `fetch` ya está en el navegador; una dependencia menos. El 401 dispara un evento (`sgpis:sesion-expirada`) en vez de hacer `window.location = '/login'` dentro del servicio, para que la decisión de a dónde ir viva en la app y el servicio sea usable en pruebas.

**12. Errores comparables por `type`.** Hicimos que `ErrorApi` exponga `tipo` (el campo `type` del `problem+json`) porque el contrato dice explícitamente que las pruebas comparan `type` y no el texto del mensaje. La propuesta solo exponía `message`.

## Lo que aceptamos sin cambios

La estructura general de carpetas (`components/`, `pages/`, `services/`), el uso de Tailwind con tokens en `@theme` (`index.css`), el patrón de variantes como diccionario de clases en `Boton.jsx` y la página de demo para ejercitar los estados. La propuesta del agente en esos puntos coincidía con lo que habríamos hecho a mano.
