# Revisión de seguridad: autenticación y protección de rutas

**Equipo:** 19
**Actividad:** S05-S06-A2
**Código del agente sin editar:** commits "v0 del módulo de autenticación generado por el agente" y "v0 de la protección de rutas generado por el agente" en `backend/`. Prompts en `evidencia_agente/prompts.md`.
**Pruebas:** `backend/tests/test_auth.py` y `backend/tests/test_permisos.py` (las demás pruebas del backend corren autenticadas).

## 1. Módulo de autenticación

### 1.1 Qué pidió el contrato

`openapi_equipo.yaml` ya traía el diseño desde S05-S06-A1: `POST /auth/register`, `POST /auth/login`, `GET /auth/me`, `POST /auth/logout` y el esquema `BearerAuth`. Ese esquema pide algo más que un JWT sin estado. El token lleva `sub`, `sid`, `iat` y `exp`, y en cada solicitud el servidor revisa además que la sesión `sid` exista, no esté revocada y tenga menos de 60 minutos sin actividad. Es la única forma de cumplir RF-26-AC-5 (cerrar sesión invalida el token) y RF-26-AC-6 (expira por inactividad); lo decidimos desde el Sprint 1.

El registro no es abierto. RF-03 reserva el alta de cuentas a Coordinación AMPIP, así que `POST /auth/register` recibe el token de la invitación que genera `POST /usuarios` y con eso fija la contraseña y activa la cuenta (decisión D-02 de `diferencias_diseno.md`).

### 1.2 Revisión con las preguntas de la actividad

| Pregunta | Qué encontramos en el código del agente | Prueba |
|---|---|---|
| ¿El JWT tiene expiración explícita? | Sí. `exp` sale de `JWT_EXPIRATION` (segundos, entre 60 y 86,400) y `jwt.decode` exige los cuatro claims. Sin la variable, el login responde 500 en lugar de emitir tokens sin vencimiento. La sesión tiene además su propio `expira_en` y la ventana de inactividad de 60 minutos. | `test_RF_26_AC_1_login_entrega_jwt_con_expiracion_explicita` comprueba `exp - iat = JWT_EXPIRATION`; `test_token_expirado_401`; `test_RF_26_AC_6_inactividad_de_60_minutos_401`. |
| ¿`/register` devuelve la contraseña? | No. La respuesta usa el schema `Usuario`, que no tiene campo de contraseña ni de hash. En la base solo queda el hash bcrypt (costo 12). | `test_RF_03_AC_1_register_activa_cuenta_y_no_devuelve_contrasena` busca la contraseña, la palabra "contrasena" y "hash" en el cuerpo, y revisa que lo guardado empiece con `$2`. |
| ¿El middleware rechaza firma inválida o token vencido? | Sí. El algoritmo está fijo en HS256, así que un token con `alg: none` o firmado con otra llave se rechaza. Un token con firma válida pero sesión revocada, vencida o inactiva también da 401. | `test_token_con_firma_invalida_401` cubre un carácter cambiado en la firma, otra llave y `alg: none`; `test_token_expirado_401`; `test_RF_26_AC_5_logout_invalida_token`. |
| ¿El secret está en código duro o en variable de entorno? | En variable de entorno, sin valor por omisión, con mínimo de 32 bytes. Encontramos el hueco S-01, que se describe abajo. | `test_secreto_no_esta_en_el_codigo` recorre `app/`; `test_secreto_de_ejemplo_rechazado`. |

### 1.3 Hallazgos y correcciones

| ID | Hallazgo | Riesgo | Corrección |
|---|---|---|---|
| S-01 | `.env.example` trae `JWT_SECRET=cambiar_por_un_secreto_aleatorio_de_al_menos_32_bytes`. Ese texto mide más de 32 bytes, así que la validación de longitud lo aceptaba. | Quien copie `.env.example` a `.env` sin editarlo firma tokens con un secreto que está publicado en el repositorio; cualquiera podría fabricar un token válido para cualquier `sub`. El riesgo baja porque además se exige una sesión `sid` real, pero el secreto deja de proteger algo. | `seguridad.py` rechaza los valores de ejemplo conocidos y responde 500, igual que si faltara la variable. |

### 1.4 Lo que el agente resolvió bien y conservamos

- Tiempo de respuesta parejo en el login. Cuando el correo no existe o la cuenta no está activa, igual se hace una comparación bcrypt contra un hash de relleno, para que el tiempo no revele qué cuentas existen. El mensaje es el mismo en los tres casos.
- El contador de intentos corre para correos que no existen y se busca en minúsculas, así que el bloqueo de RF-26-AC-3 no se brinca cambiando mayúsculas (esto ya lo protegía la corrección R-09 del esquema).
- Registro sin carreras. El enlace de invitación se lee con `FOR UPDATE`; dos registros simultáneos con el mismo token se serializan y el segundo recibe 410. Token inexistente, usado o vencido responden igual.
- Límite de 72 bytes de bcrypt. Una contraseña más larga se rechaza con 422 en lugar de truncarse en silencio.
- `HTTPBearer(auto_error=False)`. La versión por omisión de FastAPI responde 403 cuando falta el encabezado; con esta opción el 401 lo decide nuestro código, con `WWW-Authenticate: Bearer`.
- Rol y estado se leen de la base en cada solicitud. Una baja (RF-29) revoca las sesiones y además el usuario inactivo no pasa la validación, aunque su token siga sin vencer (`test_usuario_dado_de_baja_pierde_acceso_inmediato`).

### 1.5 Riesgos aceptados

- Bloqueo como denegación de servicio. Cinco intentos fallidos bloquean una cuenta 15 minutos aunque los haga otra persona. Es lo que pide RF-26-AC-3; lo anotamos para revisarlo con AMPIP si se vuelve un problema.
- Sin límite global de intentos por IP. El bloqueo es por correo. Un límite por IP corresponde al proxy de producción (Caddy) y no a esta actividad.

## 2. Protección de rutas

### 2.1 Qué rutas quedaron protegidas

El contrato pone `security: [BearerAuth: []]` en todo y lo quita con `security: []` en cinco operaciones: `GET /salud`, `POST /auth/login`, `POST /auth/register` y las dos de recuperación de contraseña (`POST /recuperaciones-contrasena` y `POST /restablecimientos-contrasena`, que desde la Parte 0 recibe el token en el cuerpo, D-20). Las tres primeras están implementadas y siguen públicas; la recuperación de contraseña todavía no se implementa. Todo lo demás que está implementado exige token: las 46 operaciones CRUD de S05-S06-A1, más `GET /auth/me` y `POST /auth/logout`.

Cada router protegido se monta en `main.py` con la dependencia `permisos.autorizar`. Esa dependencia primero valida el token y la sesión (401 si falla) y luego busca la ruta en el mapa `PERMISOS` de `app/permisos.py` (403 si el perfil no aparece). El mapa es la única fuente de permisos. Al arrancar, `verificar_mapa` compara las rutas con el mapa y la API no levanta si una ruta protegida no tiene entrada o si una entrada no corresponde a ninguna ruta.

Los perfiles son de dos tipos. Los globales dependen solo del rol. Los relativos a un parque combinan el rol con una relación vigente que se lee de la base en cada solicitud: la APPI con su `parque_id`, el consultor con su asignación vigente o una sesión de comité abierta, el gerente con el desarrollador del parque. Por eso una reasignación (RF-10-AC-2) o una baja (RF-29) quitan el acceso en la solicitud siguiente, sin esperar a que venza el token. Un parque dado de baja ya no da acceso por relación a nadie. El Administrador técnico no aparece en el mapa, así que recibe 403 en todas las rutas de negocio (RF-03-AC-3, RNF-02).

Este es el mapa completo, generado desde `PERMISOS`:

| Método | Ruta (bajo `/api`) | Quién puede |
|---|---|---|
| GET | `/versiones-catalogo` | Coordinación |
| POST | `/versiones-catalogo` | Coordinación |
| GET | `/versiones-catalogo/{versionId}` | Coordinación |
| GET | `/criterios/{criterioId}` | Coordinación, Director General, APPI (cualquiera), Consultor (cualquiera) |
| PATCH | `/criterios/{criterioId}` | Coordinación |
| GET | `/generaciones` | Coordinación, Director General, APPI (cualquiera), Consultor (cualquiera), Gerente corporativo (cualquiera) |
| POST | `/generaciones` | Coordinación |
| GET | `/generaciones/{generacionId}` | Coordinación, Director General, APPI (cualquiera), Consultor (cualquiera), Gerente corporativo (cualquiera) |
| GET | `/parques` | Coordinación, Director General, APPI (cualquiera), Consultor (cualquiera), Gerente corporativo (cualquiera) |
| POST | `/parques` | Coordinación |
| GET | `/parques/{parqueId}` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta), Gerente del desarrollador |
| PATCH | `/parques/{parqueId}` | Coordinación |
| PUT | `/parques/{parqueId}/tipo-pi` | Coordinación |
| GET | `/parques/{parqueId}/tipos-pi` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| POST | `/parques/{parqueId}/actualizaciones-anuales` | Coordinación |
| GET | `/parques/{parqueId}/actualizaciones-anuales/{actualizacionId}` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| GET | `/parques/{parqueId}/historial` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| GET | `/usuarios` | Coordinación |
| POST | `/usuarios` | Coordinación |
| GET | `/usuarios/{usuarioId}` | Coordinación, El propio usuario |
| PATCH | `/usuarios/{usuarioId}` | Coordinación |
| GET | `/parques/{parqueId}/usuarios` | Coordinación |
| PUT | `/parques/{parqueId}/contacto-principal` | Coordinación |
| GET | `/parques/{parqueId}/asignaciones-consultor` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| POST | `/parques/{parqueId}/asignaciones-consultor` | Coordinación |
| GET | `/parques/{parqueId}/asignaciones-consultor/{asignacionId}` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| GET | `/parques/{parqueId}/criterios` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| GET | `/parques/{parqueId}/criterios/{criterioId}` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| GET | `/parques/{parqueId}/autoevaluaciones` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| GET | `/parques/{parqueId}/autoevaluaciones/{criterioId}` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| PUT | `/parques/{parqueId}/autoevaluaciones/{criterioId}` | APPI del parque |
| GET | `/parques/{parqueId}/cumplimiento` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta), Gerente del desarrollador |
| GET | `/parques/{parqueId}/plan-trabajo` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| POST | `/parques/{parqueId}/plan-trabajo` | Consultor asignado |
| GET | `/parques/{parqueId}/plan-trabajo/{renglonId}` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta) |
| PATCH | `/parques/{parqueId}/plan-trabajo/{renglonId}` | Consultor asignado |
| DELETE | `/parques/{parqueId}/plan-trabajo/{renglonId}` | Consultor asignado |
| GET | `/parques/{parqueId}/revisiones-analisis-riesgos` | APPI del parque, Consultor asignado |
| POST | `/parques/{parqueId}/revisiones-analisis-riesgos` | Consultor asignado |
| GET | `/parques/{parqueId}/revisiones-analisis-riesgos/{revisionId}` | APPI del parque, Consultor asignado |
| GET | `/parques/{parqueId}/fases` | Coordinación, Director General, APPI del parque, Consultor asignado, Consultor de comité (sesión abierta), Gerente del desarrollador |
| POST | `/parques/{parqueId}/fases/{fase}/cierre` | Coordinación |
| POST | `/parques/{parqueId}/avances-fase` | Coordinación |
| GET | `/configuracion` | Coordinación |
| PATCH | `/configuracion` | Coordinación |
| GET | `/bitacora` | Coordinación |

Además del mapa hay dos reglas que dependen del dato. `GET /parques` devuelve solo los parques que el usuario puede ver (todos para Coordinación y Director General). En `GET /criterios/{criterioId}`, la APPI y el consultor solo ven criterios O o R de sus parques y sin la columna de marcas por tipo de PI (RF-25, RD-05).

Cada 403 queda en la bitácora con acción `acceso_denegado`, resultado "denegado", usuario, rol, parque y la ruta (RF-35-AC-2).

### 2.2 Hallazgos y correcciones

| ID | Hallazgo en el código del agente | Riesgo | Corrección | Prueba |
|---|---|---|---|---|
| P-01 | El gerente corporativo leía todo el expediente de los parques de su desarrollador: criterios, autoevaluaciones con comentarios, plan de trabajo con responsables, asignaciones e historial. | El SRS le da una vista de solo lectura del avance (2.3, RF-23). Los comentarios de autoevaluación y el plan describen huecos de seguridad del parque, que es justo lo que RNF-02 cuida. | El gerente queda con la ficha del parque, el cumplimiento y las fases. El resto del expediente usa el grupo `LECTURA_DETALLE`, que no lo incluye. | `test_P_01_gerente_solo_ve_el_avance_de_sus_parques` |
| P-02 | Con todo protegido, crear un usuario exige una sesión de Coordinación, y no había manera de crear la primera. El agente lo señaló y dejó la semilla dependiendo de una cuenta que nadie podía crear. | Sin primera cuenta, el sistema no se puede poner en marcha. Crearla con un INSERT a mano en producción dejaría una contraseña en el historial de la terminal. | Comando `python -m app.alta_inicial`: corre en el servidor, crea la cuenta de Coordinación en "pendiente de activación" con su invitación y muestra el token una vez. La contraseña la fija la persona con `POST /auth/register`, igual que cualquier otra cuenta. Queda en la bitácora. La semilla de desarrollo (`app/semilla.py`) sí crea su cuenta de Coordinación directo en la base, con la contraseña de `.env`; es solo para entornos locales y no sustituye a este comando. | `test_P_02_alta_inicial_de_coordinacion` |

### 2.3 Decisiones del agente que aceptamos

- El Director General lee lo mismo que Coordinación y no escribe nada. Su única acción en el sistema es firmar el dictamen (RF-14), que todavía no está implementada.
- El consultor de comité lee el expediente solo mientras su sesión de comité está abierta (RF-13), y nunca escribe.
- `GET /usuarios/{usuarioId}`: Coordinación, o el propio usuario que consulta su registro.
- Las revisiones del análisis de riesgos solo las ven la APPI y el consultor asignado (RF-16-AC-1). Coordinación recibe 403 aunque la revisión no traiga el documento, porque el resumen ("12 riesgos, 4 altos") ya expone al parque.

### 2.4 Pendiente para el equipo

El consultor asignado registra el plan de trabajo y tiene que elegir como responsable a un usuario APPI del parque (RF-09-AC-1), pero el contrato dice que `GET /parques/{parqueId}/usuarios` es solo de Coordinación. Con el contrato como está, el consultor no tiene de dónde sacar el id del responsable. Proponemos abrir esa ruta al consultor asignado, limitada a los usuarios APPI de su parque. Como cambia el contrato, va en un PR que revisan los tres.

### 2.5 Pruebas manuales desde la terminal

`pruebas_terminal.sh` corre los cuatro casos de la actividad con `curl` contra la API levantada con la semilla de demostración, y dos casos más: aislamiento entre parques y registro en bitácora. La salida completa está en `pruebas_terminal_salida.txt`; los tokens aparecen como `<token>`.

| Caso | Petición | Esperado | Obtenido |
|---|---|---|---|
| Sin token | `POST /api/parques` sin `Authorization` | 401 | 401 `sesion_invalida` |
| Token inválido | Mismo POST con el último carácter del token cambiado | 401 | 401 `sesion_invalida` |
| Rol incorrecto | Mismo POST con el token de la APPI de demostración | 403 | 403 `sin_permiso` |
| Token válido y rol correcto | Mismo POST con el token de Coordinación | 201 | 201, parque creado |
| Aislamiento (RNF-01) | `GET /api/parques/{otro}` con el token de la APPI | 403 | 403 `sin_permiso` |
| Bitácora (RF-35-AC-2) | `GET /api/bitacora?accion=acceso_denegado` con Coordinación | Los dos 403 registrados | 200, dos registros "denegado" con usuario, rol y ruta |

Las mismas reglas están automatizadas en `test_permisos.py`. Una prueba recorre las 48 rutas protegidas y exige 401 sin token y con token alterado. Otras cubren el 403 por rol, el aislamiento entre parques, la pérdida de acceso al reasignar consultor, la autoevaluación solo para la APPI, las revisiones de análisis de riesgos ocultas a Coordinación, la bitácora solo para Coordinación y el registro del 403. La suite completa del backend tiene 82 pruebas y todas pasan.

## 3. Video

`pruebas_auth.mp4` sigue la colección `postman/SGPIS_S05_S06_A2.postman_collection.json` en el orden de la actividad: `POST /auth/register` (201), `POST /auth/login` (200 con el JWT), `GET /auth/me` (200), `POST /parques` con token (201), el mismo POST sin token (401) y con el token de la APPI (403). La corrida de la colección con Newman, con 9 aserciones aprobadas, está en `postman/corrida_newman_A2.txt`.
