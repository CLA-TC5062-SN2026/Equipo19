# Diferencias de diseño y consolidación del equipo

**Equipo:** 19 (Ángel Kociankowski, Leonardo Cossío, Erick Ramírez)
**Actividad:** S05-S06-A1, Parte 0
**Resultado:** `openapi_equipo.yaml` v2.0.0, `diagrama_clases_equipo.puml`, `arquitectura_equipo.md`
**Script que aplica los cambios al contrato:** `consolidacion/consolidar_openapi.py` (cada bloque cita la decisión D-xx que aplica)

## 1. Insumos y alcance de esta versión

| Artefacto individual (S04) | Ángel | Leonardo | Erick |
|---|---|---|---|
| `openapi.yaml` (S04_A2) | Recibido: 75 operaciones, contra `SRS_final.md` v1.4 | Pendiente | Pendiente |
| Diagrama de clases (S04_A1) | Recibido | Pendiente | Pendiente |
| Diagrama de componentes (S04_A1) | Recibido | Pendiente | Pendiente |

Esta versión consolida el diseño de Ángel contra el `SRS_equipo.md` v2.0, que ya contiene lo que Leonardo y Erick aportaron como requerimientos en S03-A1. Los S04 individuales de Leonardo y Erick no estaban en el repositorio al cerrar esta versión. Cuando se suban a `S05_S06_A1/insumos/`, se corre el análisis de diferencias del agente sobre los tres contratos y los tres diagramas, y la sección 6 registra lo que cambie. No llenamos sus columnas con aportes que no podemos verificar.

La consolidación tuvo entonces dos frentes:

1. Diseño contra SRS de equipo. El contrato de Ángel se escribió contra su SRS individual (31 RF, 110 AC). El SRS de equipo tiene 39 RF y 150 AC. Comparamos los IDs de criterio de aceptación del contrato con los del SRS de equipo: 30 criterios sin endpoint, ningún ID huérfano.
2. Diseño contra decisiones del curso y del Sprint 1: ruta base, nombre del esquema de seguridad y espacio `/auth`, que el curso fija para S05-S06-A2 y que la tarea T-10 del Sprint 1 ya usaba.

## 2. Qué aportó cada integrante a los tres artefactos

| Integrante | OpenAPI | Clases | Arquitectura |
|---|---|---|---|
| Ángel | Contrato base completo: convenciones REST, semántica 400/409/422, paginación, formato `Error`, sesión validada en servidor, 75 operaciones con trazabilidad a AC. | Modelo base: usuario con atributo `rol`, expediente por parque y generación, separación entre estado de evidencia y estado de calificación, bloqueo por correo en `IntentoLogin`. | ADR-001: monolito modular en capas + worker; C4 niveles 2 y 3; despliegue. |
| Leonardo | Vía SRS de equipo: fases con cierre y excepción (RF-32 → D-10), Evaluación de Desempeño con folio (RF-33 → D-11), bitácora consultable con eventos mínimos (RF-35 → D-13), tres cifras de cumplimiento (C-11 → D-07), versiones de catálogo en solo lectura (C-14 → D-09). | `CatalogoFase` y `FaseExpediente`; `EvaluacionDesempeno`; campos de `RegistroBitacora`. | Sin cambio de estilo. Sus RNF-16 y RNF-17 de rendimiento quedan como metas de la vista de cartera. |
| Erick | Vía SRS de equipo: evidencia vinculada a varios criterios con estado por vínculo (C-19 → D-05), eliminación lógica y carga múltiple (RF-05-AC-8 a AC-10 → D-05), contacto principal (RF-34 → D-12), recomendaciones (RF-36 → D-14), motivo en cambio de tipo de PI (C-04 → D-08). | `VinculoEvidencia`, `Recomendacion`, contacto principal en `Parque`, `motivo` en `ClasificacionTipoPI`. | Sin cambio de estilo. |

## 3. Contrato OpenAPI

### 3.1 Consenso

Las 75 operaciones del contrato de Ángel cubren los 31 RF que el SRS de equipo conservó con el mismo ID (diferencias_SRS.md, sección 1: ningún ID cambió de significado). Se conservaron sin cambio de ruta ni de método, salvo las de autenticación (D-01) y las de evidencias (D-05).

### 3.2 Gaps: criterios del SRS de equipo sin endpoint

| Criterios | Origen | Resolución |
|---|---|---|
| RF-01-AC-5 | C-14 | D-09 |
| RF-05-AC-5 a AC-10 | Leonardo (AC-5, AC-6), Erick (AC-7 a AC-9), Ángel (AC-10) | D-05 |
| RF-06-AC-6, AC-7 | C-05 | D-06 |
| RF-08-AC-4, AC-5 | C-11 | D-07 |
| RF-11-AC-5, AC-6 | C-04 | D-08 |
| RF-32-AC-1 a AC-5 | Leonardo y Erick | D-10 |
| RF-33-AC-1 a AC-3 | Leonardo | D-11 |
| RF-34-AC-1 a AC-3 | Erick | D-12 |
| RF-35-AC-1 a AC-4 | Leonardo y Erick | D-13 |
| RF-36-AC-1, AC-2 | Erick | D-14 |

### 3.3 Conflictos y resoluciones

| ID | Tema | Diseño individual | Problema | Resolución en `openapi_equipo.yaml` |
|---|---|---|---|---|
| D-01 | Autenticación | `POST /sesiones` (201), `GET` y `DELETE /sesiones/actual`, `PATCH /invitaciones/{token}`; base `/api/v1`; esquema `bearerAuth` | El curso pide `/api/auth/register`, `/api/auth/login`, `/api/auth/me` y `securitySchemes: BearerAuth`. T-10 del Sprint 1 ya decía `POST /auth/logout`. | Base `/api`. `POST /auth/register`, `POST /auth/login` (200), `GET /auth/me`, `POST /auth/logout`. Esquema `BearerAuth`. Se conserva la sesión en servidor validada en cada solicitud y se agrega `exp` absoluto con `JWT_EXPIRATION`. Aceptamos la forma RPC solo dentro de `/auth`; el resto del contrato sigue con sustantivos. |
| D-02 | Registro abierto | Alta de cuentas solo por Coordinación AMPIP (RF-03) | Un `register` público dejaría a cualquiera crear una cuenta, y el SRS no lo permite. | `POST /auth/register` exige el token de la invitación que genera `POST /usuarios`. Fija la contraseña (bcrypt) y activa la cuenta; responde 201 sin contraseña. Reemplaza a `PATCH /invitaciones/{token}`. |
| D-05 | Evidencia y criterio | Una evidencia pertenece a un criterio y lleva el estado | C-19 pide un archivo vinculado a varios criterios, cada vínculo con su estado. Con el estado en el archivo, aceptarlo para 3.1 lo aceptaría para 3.4. | Una sola ruta de escritura, `POST /parques/{parqueId}/evidencias`, con `archivos[]` y `criterioIds[]`; responde `{creadas, rechazadas}` (RF-05-AC-8). El estado pasa al vínculo: `PATCH /evidencias/{id}/vinculos/{criterioId}` acepta y `POST /evidencias/{id}/observaciones` recibe `criterioId`. `DELETE /evidencias/{id}` hace baja lógica y responde 409 si hay un vínculo aceptado. Se retiran `POST /parques/{p}/criterios/{c}/evidencias` y `PATCH /evidencias/{id}`. |
| D-06 | Límite de archivo | 100 MB fijo en el contrato | C-05 lo hizo configurable. | `GET` y `PATCH /configuracion`; 413 con el límite vigente en el mensaje. También guarda la vigencia del distintivo (C-10). |
| D-07 | Cifras de cumplimiento | Obligatorios y avance general | C-11 agrega recomendados y fija el cálculo por suma de criterios. | `porcentajeRecomendados` en `CifrasCumplimiento`. |
| D-08 | Cambio de tipo de PI | Sin motivo | C-04 lo exige. | `motivo` obligatorio en `CambioTipoPI`; `motivo` y `cambiadoPor` en el historial. |
| D-09 | Versiones de catálogo | `vigente` booleano | C-14: las anteriores quedan en solo lectura. | `estado: activa / solo_lectura`; `PATCH /criterios/{id}` responde 409 sobre una versión en solo lectura. |
| D-10 | Fases | Solo `fase` en `Parque` | RF-32 pide estado por fase, cierre por Coordinación y avance por excepción con motivo. | `GET /parques/{p}/fases`, `POST /parques/{p}/fases/{fase}/cierre` (la ruta que cita RF-32-AC-3), `POST /parques/{p}/avances-fase`. |
| D-11 | Evaluación de Desempeño | No existía | RF-33. | `GET` y `POST /parques/{p}/evaluaciones-desempeno` con folio `ED-AAAA-NNNN`. |
| D-12 | Usuarios APPI | Hasta 3 por parque, sin contacto principal | RF-34. | `GET /parques/{p}/usuarios` y `PUT /parques/{p}/contacto-principal`; `contactoPrincipalId` en `Parque`. |
| D-13 | Bitácora | Solo se escribía | RF-35 pide consulta con filtros, solo para Coordinación. | `GET /bitacora` con filtros por parque, usuario, acción y fechas. Sigue sin operación de escritura. |
| D-14 | Recomendaciones | No existían | RF-36: no cambian estados y no son observaciones. | `GET` y `POST /parques/{p}/criterios/{c}/recomendaciones`. |

Resultado: 62 rutas, 88 operaciones, 110 schemas. Los 150 criterios del SRS de equipo, menos los de RF con prioridad "Posterior", tienen al menos una operación; ningún `x-acceptance-criteria` cita un ID que no exista. `openapi-spec-validator` lo valida y Redocly deja 3 advertencias, las mismas que tenía el contrato individual (licencia, servidor en localhost, `/salud` sin respuesta 4xx).

## 4. Diagrama de clases

### 4.1 Consenso

Se conserva la estructura del diagrama de S04_A1: catálogo en cuatro niveles con marca por tipo de PI, parque con historial de clasificación, expediente por parque y generación, criterio del parque con estado de calificación, plan de trabajo, análisis de riesgos, Opiniones, comité y dictamen.

### 4.2 Cambios

| ID | Clase | Antes | Ahora | Motivo |
|---|---|---|---|---|
| D-05 | `Evidencia`, `VinculoEvidencia`, `Observacion` | `CriterioParque` *-- `Evidencia {estado}`; `Observacion` colgaba de la evidencia | `Expediente` *-- `Evidencia`; `Evidencia` *-- `VinculoEvidencia {estado}` --> `CriterioParque`; `Observacion` cuelga del vínculo y guarda la versión observada | C-19, RF-05-AC-6 y AC-7 |
| D-05 | `Evidencia` | Sin baja | `eliminadaEn`, eliminada por | RF-05-AC-9 |
| D-06 | `Configuracion` | No existía | Un registro con límite y vigencia | C-05, C-10 |
| D-08 | `ClasificacionTipoPI` | Sin motivo | `motivo`, cambiado por | C-04 |
| D-09 | `VersionCatalogo` | `activa: boolean` | `estado {activa, solo_lectura}` | C-14 |
| D-10 | `CatalogoFase`, `FaseExpediente` | `fase` como enumeración en `Expediente` | Secuencia como datos; nueve `FaseExpediente` por expediente con estado, fechas y motivo | C-15, RF-32 |
| D-11 | `EvaluacionDesempeno` | No existía | Folio, fecha, versión de catálogo, resultado | RF-33 |
| D-12 | `Usuario`/`Parque` | APPI 0..3 por parque | APPI 0..*; `Parque` --> contacto principal 0..1 | RF-34 |
| D-13 | `RegistroBitacora` | Fecha, acción, resultado | Más rol, parque, tipo e id de recurso, detalle | RF-35 |
| D-14 | `Recomendacion` | No existía | Cuelga de `CriterioParque` | RF-36 |
| D-15 | `Sesion`, `EnlaceUnSoloUso` | Token en claro; sin expiración absoluta | `tokenHash`; `expiraEn` en ambos | Seguridad: una fuga de la base no debe entregar invitaciones usables |

### 4.3 Coherencia con el contrato

Revisamos que cada atributo de las clases que el contrato expone tenga su campo en un schema, con el mismo nombre en camelCase:

| Clase | Schema | Diferencias aceptadas |
|---|---|---|
| `Usuario` | `Usuario` | `contrasenaHash` nunca sale en una respuesta. |
| `Parque` + `Expediente` vigente | `Parque` | El schema aplana datos del expediente vigente (fase, fechas del programa, generación), como dice la convención del contrato. |
| `Evidencia` + `VersionEvidencia` vigente | `Evidencia` | `nombreArchivo`, `tipoMime` y `tamanoBytes` vienen de la versión vigente; `rutaObjeto` es interna. |
| `VinculoEvidencia` | `VinculoEvidencia` | `claveCriterio` y `estadoCriterio` se leen de `CriterioParque` para que la SPA no haga otra llamada. |
| `FaseExpediente` + `CatalogoFase` | `FaseExpediente` | `actual` es derivado. |
| `Configuracion`, `EvaluacionDesempeno`, `Recomendacion`, `RegistroBitacora`, `ClasificacionTipoPI` | Mismo nombre | Ninguna. |

## 5. Arquitectura

| ID | Tema | Diseño individual | Resolución en `arquitectura_equipo.md` |
|---|---|---|---|
| D-16 | Tamaño del equipo | ADR-001 suponía un desarrollador | Se mantiene el estilo; la regla de fronteras entre módulos se revisa en cada PR. |
| D-17 | Ruta y autenticación | `/api/v1`, `bearerAuth` | `/api`, `BearerAuth`, `exp` absoluto más sesión en servidor (D-01). |
| D-18 | Entorno local | Solo producción descrita | `docker compose` con PostgreSQL 16 y la API; el esquema se crea con `esquema_bd.sql`. Worker y Mailpit entran con correo y plazos. |

## 6. Integración de los diseños de Leonardo y Erick

Sin registrar todavía. Cuando lleguen sus S04, aquí van las tablas de consenso, gaps y conflictos que entregue el agente sobre los tres contratos y los tres diagramas, con la resolución del equipo para cada conflicto.
