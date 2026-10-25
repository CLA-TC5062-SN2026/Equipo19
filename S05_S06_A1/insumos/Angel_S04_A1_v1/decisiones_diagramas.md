# Revisión de los diagramas del agente y decisiones de diseño

**Actividad:** S04_A1, Partes 2 y 3
**Alumno:** Ángel Sebastián Kociankowski Montelongo (A01379225)

Las propuestas del agente están sin editar en `evidencia_agente/` (`componentes_agente.puml`, `despliegue_agente.puml`, `clases_agente.puml`), con sus imágenes en `imagenes/agente/`. Los prompts están en `evidencia_agente/prompts.md`. Este documento explica qué cambié y por qué.

## 1. Diagramas de arquitectura (Parte 2)

La propuesta del agente estaba bien armada: separó API, worker, base de datos y los dos buckets, y amarró cada nota a un RNF. Hice estos cambios:

| # | Propuesta del agente | Cambio | Razón |
|---|---|---|---|
| A1 | El Administrador técnico usa la SPA con "herramientas técnicas de administración". | Su cuenta existe en la aplicación, pero no le da acceso a ningún parque ni evidencia. Las herramientas técnicas (desplegar, restaurar respaldos, revisar registros) se usan por SSH en el servidor. | El agente tomó la frase de RF-03-AC-3, que sí le da esas herramientas, pero el SRS no dice qué son. Decidí que son de infraestructura y no pantallas de la SPA: `openapi.yaml` no tiene ningún endpoint técnico, y cada pantalla de administración dentro de la aplicación sería una puerta más para un rol que no debe ver evidencias (RNF-02). Queda pendiente confirmar con AMPIP si espera alguna herramienta técnica dentro del sistema. |
| A2 | El monitoreo consulta `/api/salud`. | `GET /api/v1/salud`, agregado al contrato sin sesión y sin datos del programa. | La ruta no existía en el contrato y no tenía el prefijo de versión. Un diagrama no puede depender de un endpoint que el contrato no define. |
| A3 | Solo vista de contenedores (C4 nivel 2). | Agregué la vista de componentes de la API y del worker (C4 nivel 3) en el mismo archivo. | La actividad pide la estructura interna de los módulos. Esa vista es la que muestra el único punto de autorización, la regla de que un módulo no lee tablas de otro y dónde se escriben bitácora y outbox. |
| A4 | GitHub Actions despliega por SSH. | El Administrador técnico despliega con `docker compose pull && up -d`; el servidor solo descarga imágenes. | La Definition of Done de S03_A2 dejó CI/CD diferido. Dibujar un pipeline que no existe haría que el diagrama describiera un sistema distinto al real. |
| A5 | "2 vCPU, 4 GB RAM" como dato fijo. | Marcado como dimensionamiento inicial. | No hay prueba de carga que lo respalde; las cifras de RNF-06 y RNF-10 son del equipo, no del cliente. |
| A6 | Correo, monitoreo y GitHub sueltos alrededor del proveedor. | Agrupados como servicios externos fuera del proveedor, que no guardan evidencias. | RNF-05 habla de dónde se guardan los archivos. El diagrama tiene que dejar claro que ningún servicio externo los recibe. |
| A7 | Nota de RNF-13 sin matiz. | La nota dice que el respaldo en la misma región protege contra borrado o corrupción, no contra la caída de la región. | Es un riesgo aceptado por RNF-05 y conviene que quede escrito, no implícito. |

Mantuve del agente el Caddy como único punto expuesto, que sirve la SPA y la API en el mismo origen (sin CORS), el `REVOKE UPDATE, DELETE` sobre la bitácora y el worker con la misma imagen que la API.

## 2. Diagrama de clases del dominio (Parte 3)

### ¿Las entidades reflejan el dominio? ¿Las relaciones son correctas?

Casi todas las entidades del agente existen en el SRS, y en dos puntos modeló mejor que yo: separó un `Expediente` por parque y generación, que es lo que pide RF-31 (las generaciones que cursó cada parque), y armó el catálogo como composición VersiónCatálogo → Estándar → Subestándar → Criterio → MarcaPorTipo, con multiplicidades exactas (10 estándares, 4 marcas). Los dos se quedaron.

Encontré cuatro problemas de modelado y dos de alcance. Los cuatro primeros son las decisiones que documento.

### Decisión 1. Roles como atributo, no como herencia

**Propuesta del agente.** `Usuario` abstracto con seis subclases: `CoordinacionAMPIP`, `DirectorGeneralAMPIP`, `APPI`, `Consultor`, `GerenteCorporativo` y `AdministradorTecnico`. Cuatro de ellas sin atributos propios.

**Problema.**
- Una subclase sin atributos ni comportamiento propio no es un tipo distinto; es un valor. Que cuatro de seis estén vacías lo confirma.
- El rol cambia: el contrato permite cambiarlo con `PATCH /usuarios/{id}`. Con herencia, cambiar el rol obliga a cambiar la clase del objeto, que en el ORM significa borrar y recrear el registro y perder sus referencias en la bitácora.
- La distinción que sí importa no está en el usuario: un mismo consultor es asignado del parque A y de comité del parque B. Eso es una relación con el parque, no un tipo de usuario.
- La multiplicidad `APPI "1..3" -- "1" Parque` obligaba a que un parque recién dado de alta ya tuviera APPI, y RF-02 lo crea antes que a sus usuarios (RF-03).

**Decisión.** `Usuario` con atributo `rol: Rol`. "Consultor asignado" es `AsignacionConsultor` con vigencia (RF-10-AC-2 conserva el historial) y "consultor de comité" es la asociación desde `SesionComite` (RF-13). APPI de un parque queda como `Usuario "0..3" → "0..1" Parque`. La regla "nadie es APPI y consultor del mismo parque" (RF-03-AC-2) se valida en la asignación, igual que en el contrato.

### Decisión 2. Autoevaluación, calificación y evidencia son tres cosas distintas

**Propuesta del agente.** `Expediente *-- 1 Autoevaluacion *-- CalificacionCriterio *-- Evidencia`. La evidencia era parte de la calificación, y la calificación era parte de la autoevaluación.

**Problema.** Esa cadena mezcla dos actores y dos momentos del programa. La autoevaluación de diagnóstico (RF-04) es la respuesta de la APPI, por criterio, al inicio. La calificación (RF-27) la decide el consultor sobre la evidencia, durante todo el programa, y tiene su propia máquina de estados. Con el modelo del agente, la evidencia y la calificación de un criterio dependían de una `Autoevaluacion` única y obligatoria por expediente, que solo tenía fecha y una marca de revisada, sin la respuesta de la APPI por criterio. Además, `Evidencia` guardaba un solo archivo con un campo `version: int`. RF-05-AC-4 habla de subir "una nueva versión" de una evidencia observada; con un solo archivo, la versión que el consultor observó se pierde y no hay forma de comparar qué cambió.

**Decisión.**
- `RespuestaAutoevaluacion` por criterio, de la APPI, compuesta en el `Expediente`.
- `CriterioParque` con el estado de calificación, compuesto en el `Expediente`. Solo existe para criterios O o R del tipo de PI vigente, y lo modifican el consultor y las transiciones automáticas de RF-27.
- `Evidencia` compuesta en `CriterioParque`, con su estado, y `VersionEvidencia` compuesta en `Evidencia`, con archivo, tamaño en bytes y ruta en el bucket.

Así las dos máquinas de estado de RF-27 quedan en las dos clases que cambian de estado: `Evidencia` y `CriterioParque`.

### Decisión 3. Lo derivado se calcula; lo histórico se congela

**Propuesta del agente.** Booleanos y porcentajes guardados: `Parque.atrasado`, `CompromisoPlan.atrasado`, `RevisionAnalisisRiesgos.vigente`, `Distintivo.vigente`, `Expediente.cumplimientoObligatorios`, y además `Parque.tipoPI` junto a un `HistorialTipoPI`.

**Problema.** Cada uno de esos valores se puede calcular a partir de otros datos del modelo. Guardarlos crea dos fuentes de verdad que tarde o temprano se contradicen. El caso más delicado es `RevisionAnalisisRiesgos.vigente`: una revisión deja de estar vigente cuando aparece otra más nueva del mismo ciclo (RF-16). Con el booleano guardado, registrar la nueva sin apagar la anterior deja dos vigentes, y RF-17 desbloquearía calificaciones con la equivocada.

**Decisión.** Esos atributos quedan como derivados (prefijo `/` en UML): se calculan al leer. El tipo de PI vigente se deriva de la `ClasificacionTipoPI` abierta. La excepción, a propósito, son los porcentajes al cierre de `ClasificacionTipoPI`: RF-11-AC-2 exige conservar el 85 % que tenía el parque bajo su clasificación anterior. Esos números son una foto que se congela al cerrar la clasificación, así que se guardan.

### Decisión 4. El bloqueo de inicio de sesión no vive en el usuario

**Propuesta del agente.** `intentosFallidos` y `bloqueadoHasta` como atributos de `Usuario`.

**Problema.** El contrato de S04_A2 cuenta los intentos fallidos también para correos que no existen; si no lo hiciera, la respuesta 429 revelaría qué correos están registrados. Con el contador dentro de `Usuario`, eso es imposible.

**Decisión.** Clase `IntentoLogin` indexada por correo, sin asociación a `Usuario`. También uní `TokenRecuperacion` con la invitación de activación en `EnlaceUnSoloUso`, porque las dos tienen el mismo ciclo (vigencia, un solo uso, 410 al reutilizarse).

### Ajustes de alcance y multiplicidad

- **Quité `Auditoria` y sus subclases, y `Distintivo`.** Corresponden a RF-18, RF-19 y RF-22, de prioridad "Posterior", que tampoco están en el contrato de la API. La vigencia del distintivo se obtiene del `Dictamen` firmado (RD-08). Entran al modelo cuando entren al backlog.
- **`SesionComite` pasa de 0..1 a 0..\* por expediente.** Una sesión cerrada sin dictamen debe poder reabrirse. La regla "solo una abierta a la vez" es una restricción, no una multiplicidad.
- **El documento del análisis de riesgos es su propia clase**, no un atributo de texto de la revisión. Tiene reglas de visibilidad propias (RF-16-AC-2) y la APPI lo puede borrar sin borrar la revisión.
- **Multiplicidades que ajusté al cruzar con el contrato:** un parque histórico no tiene clasificación de tipo de PI ni desarrollador (RF-31-AC-2), y un parque recién dado de alta todavía no tiene consultor asignado. Por eso `ClasificacionTipoPI` y `AsignacionConsultor` son 0..\* y el desarrollador es 0..1.
- **Mantuve dos herencias del agente porque sí tienen atributos propios:** `ParqueHistorico` (fecha del último dictamen y de término, RF-31-AC-2) y `OpinionFinal` (la marca favorable, RF-12-AC-6).

## 3. Correspondencia con el contrato de la API (S04_A2)

Hice S04_A2 antes que esta actividad, así que revisé clase por clase que el contrato y el modelo coincidan. Ajusté los dos lados: las enumeraciones del diagrama usan los mismos valores que `openapi.yaml` (roles, fases, categoría de evidencia, región ISO 3166-2:MX, respuesta de autoevaluación), en mayúsculas en el diagrama y en snake_case en el contrato, y al contrato le agregué `GET /salud` y una convención sobre el expediente vigente.

| Clase | En la API |
|---|---|
| Usuario | `/usuarios`; rol como enum `Rol` |
| Sesion | `/sesiones`, `/sesiones/actual` |
| EnlaceUnSoloUso | `/invitaciones/{token}`, `/recuperaciones-contrasena/{token}` |
| IntentoLogin | Interna; se manifiesta como 429 en `POST /sesiones` |
| VersionCatalogo, Estandar, Subestandar, Criterio, MarcaPorTipo | `/versiones-catalogo`, `/criterios/{criterioId}` |
| Generacion | `/generaciones` |
| Desarrollador | Campo de texto `desarrollador` en `Parque` y `Usuario` |
| Parque, ParqueHistorico | `/parques`, con el discriminador `tipoRegistro` (activo o histórico) |
| ClasificacionTipoPI | `/parques/{parqueId}/tipos-pi` |
| Expediente | Aplanado en `Parque` (generación, fase, fechas del programa); anteriores en `/parques/{parqueId}/historial` |
| ActualizacionAnual | `/parques/{parqueId}/actualizaciones-anuales` |
| AsignacionConsultor | `/parques/{parqueId}/asignaciones-consultor` |
| RespuestaAutoevaluacion | `/parques/{parqueId}/autoevaluaciones/{criterioId}` |
| CriterioParque | `/parques/{parqueId}/criterios` |
| Evidencia, VersionEvidencia, Observacion | `/evidencias/{evidenciaId}`, `/versiones`, `/observaciones` |
| RenglonPlanTrabajo | `/parques/{parqueId}/plan-trabajo` |
| RevisionAnalisisRiesgos, DocumentoAnalisisRiesgos | `/revisiones-analisis-riesgos`, `/documento-analisis-riesgos` |
| OpinionCumplimiento (intermedia, final) | `/opiniones-cumplimiento`, con el campo `tipo` |
| SesionComite | `/sesiones-comite` |
| Dictamen | `/dictamenes` |
| RegistroBitacora, MensajeCorreo | Internas; sin endpoint en esta versión |

Dos diferencias quedan abiertas a propósito:
- **Desarrollador** es una clase en el dominio y un texto en la API. RF-23 filtra los parques del gerente corporativo por su desarrollador, y comparar por nombre es frágil. Si el gerente corporativo entra al alcance de un sprint, el contrato debe exponer `desarrolladorId`.
- **La bitácora no tiene endpoint de consulta.** El SRS de equipo agregó una bitácora consultable entre sus RF-32 a RF-39; entra con una versión menor del contrato cuando el backlog la traiga.
