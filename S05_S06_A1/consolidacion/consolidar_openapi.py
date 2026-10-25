"""Genera openapi_equipo.yaml a partir del openapi.yaml de S04_A2 (base) y de las resoluciones de consolidación.

Uso: python consolidar_openapi.py <openapi_base.yaml> <salida.yaml>
Cada bloque de cambios cita la resolución de diferencias_diseno.md que lo origina (D-xx).
"""
import io
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

AQUI = Path(__file__).parent
yaml = YAML()
yaml.preserve_quotes = True
yaml.width = 120
yaml.indent(mapping=2, sequence=4, offset=2)


def cargar(p):
    if isinstance(p, io.StringIO):
        return yaml.load(p)
    with open(p, encoding="utf-8") as f:
        return yaml.load(f)


def flow(lista):
    s = CommentedSeq(lista)
    s.fa.set_flow_style()
    return s


def agregar_ac(op, *ids):
    acs = list(op.get("x-acceptance-criteria", []))
    for i in ids:
        if i not in acs:
            acs.append(i)
    acs.sort(key=lambda a: (int(a[3:5]), int(a.split("-")[-1])))
    op["x-acceptance-criteria"] = flow(acs)


base, salida = sys.argv[1], sys.argv[2]
d = cargar(base)
paths = d["paths"]
S = d["components"]["schemas"]
nuevos_paths = cargar(AQUI / "fragmentos_paths.yaml")
nuevos_schemas = cargar(AQUI / "fragmentos_schemas.yaml")

# --- D-01: base /api, esquema BearerAuth y espacio /auth (curso + T-10 del Sprint 1) ---
d["servers"][0]["url"] = "http://localhost:8000/api"
d["security"] = CommentedSeq([CommentedMap([("BearerAuth", flow([]))])])
esq = d["components"]["securitySchemes"]
bearer = esq.pop("bearerAuth")
bearer["description"] = (
    "JWT firmado (HS256) que emite `POST /auth/login`, con los claims `sub` (usuario), `sid` (sesión), `iat` y `exp`.\n"
    "`exp` sale de la variable de entorno `JWT_EXPIRATION` y `JWT_SECRET` firma el token; ninguno está en código.\n"
    "En CADA solicitud el servidor valida firma y `exp`, y además que la sesión `sid` exista, no esté revocada y\n"
    "tenga menos de 60 minutos sin actividad; si pasa, actualiza la última actividad. Si no pasa, responde 401.\n"
    "El rol y las asignaciones a parques se leen de la base, nunca de claims del token: cerrar sesión (RF-26-AC-5),\n"
    "la inactividad (RF-26-AC-6), la reasignación de consultor (RF-10-AC-2) y las bajas (RF-29) retiran el acceso\n"
    "de inmediato.\n"
)
esq["BearerAuth"] = bearer
for p in ["/sesiones", "/sesiones/actual", "/invitaciones/{token}"]:
    del paths[p]

# --- D-03: evidencia vinculada a varios criterios; estado por vínculo (C-19, RF-05-AC-5 a AC-10) ---
del paths["/parques/{parqueId}/criterios/{criterioId}/evidencias"]["post"]
paths["/parques/{parqueId}/criterios/{criterioId}/evidencias"]["get"]["description"] = (
    "Evidencias vinculadas al criterio, cada una con el estado de su vínculo con este criterio. No incluye las\n"
    "eliminadas salvo que se pida `incluirEliminadas=true` (historial, RF-05-AC-9).\n"
)
paths["/parques/{parqueId}/evidencias"]["post"] = nuevos_paths["/parques/{parqueId}/evidencias"]["post"]
ev = paths["/evidencias/{evidenciaId}"]
del ev["patch"]
agregar_ac(ev["get"], "RF-05-AC-6")
ev["get"]["description"] = (
    "Devuelve metadatos, vínculos con su estado, versiones (la vigente marcada) y observaciones de la evidencia, sin\n"
    "el contenido del archivo (RF-05-AC-6).\n"
)
ev["delete"] = cargar(io.StringIO("""
tags: [Evidencias]
operationId: eliminarEvidencia
summary: Eliminar una evidencia subida por error
description: |
  La APPI elimina una evidencia cuyos vínculos siguen todos en "enviada" u "observada". La baja es lógica: deja de
  contar para los criterios, queda en el historial marcada como eliminada con usuario y fecha, y se registra en la
  bitácora. Los criterios que se quedan sin evidencias vigentes regresan a "pendiente".

  Errores:
  - 409 `evidencia_aceptada`: "Una evidencia aceptada no se puede eliminar; suba una versión nueva si el documento
    cambió".
x-acceptance-criteria: [RF-05-AC-9, RF-05-AC-10]
responses:
  '204':
    description: Evidencia eliminada (baja lógica).
  '401':
    $ref: '#/components/responses/Unauthorized'
  '403':
    $ref: '#/components/responses/Forbidden'
  '404':
    $ref: '#/components/responses/NotFound'
  '409':
    $ref: '#/components/responses/Conflict'
  '500':
    $ref: '#/components/responses/InternalError'
"""))
ver = paths["/evidencias/{evidenciaId}/versiones"]["post"]
ver["description"] = (
    "La APPI sube una versión nueva de la evidencia. Cada vínculo \"observado\" vuelve a \"enviada\" y cada criterio\n"
    "vinculado que estaba \"cumplido\" o \"no cumplido\" pasa a \"en revisión\". Los vínculos \"aceptados\" conservan su\n"
    "estado. Aplican las mismas validaciones de tamaño (límite configurado) y formato que en la carga inicial.\n"
)
obs = paths["/evidencias/{evidenciaId}/observaciones"]["post"]
obs["description"] = (
    "El consultor asignado observa la evidencia para un criterio (`criterioId`). Solo ese vínculo pasa a \"observada\";\n"
    "se notifica al contacto principal de la APPI (RF-34) y el criterio permanece \"en revisión\".\n"
)
agregar_ac(obs, "RF-05-AC-7")
paths["/evidencias/{evidenciaId}/vinculos/{criterioId}"] = nuevos_paths["/evidencias/{evidenciaId}/vinculos/{criterioId}"]
for k in ["Evidencia", "EvidenciaCreate", "Observacion", "ObservacionCreate", "SesionCreada"]:
    S[k] = nuevos_schemas[k]
for k in ["EvidenciaUpdate", "InvitacionUpdate"]:
    del S[k]
S["EstadoEvidencia"]["description"] = "Alias histórico de EstadoVinculo para el filtro `estado` de los listados."

# --- D-04: límite de archivo configurable (C-05, RF-06-AC-6/AC-7) y vigencia del distintivo (C-10) ---
paths["/configuracion"] = nuevos_paths["/configuracion"]
d["components"]["responses"]["PayloadTooLarge"]["description"] = "El archivo supera el límite configurado de tamaño."

# --- D-05: tres cifras de cumplimiento (C-11, RF-08-AC-4/AC-5) ---
cif = S["CifrasCumplimiento"]
cif["required"].append("porcentajeRecomendados")
cif["properties"]["porcentajeRecomendados"] = cargar(io.StringIO(
    "type: number\nformat: float\nnullable: true\nexample: 60.0\n"
    "description: Criterios R cumplidos entre R aplicables; nulo si no hay R aplicables.\n"))
cif["description"] = "Los globales se calculan sumando criterios de los 10 estándares, nunca promediando porcentajes."
agregar_ac(paths["/parques/{parqueId}/cumplimiento"]["get"], "RF-08-AC-4", "RF-08-AC-5")

# --- D-06: motivo obligatorio en cambio de tipo de PI (C-04, RF-11-AC-5/AC-6) ---
S["CambioTipoPI"]["required"].append("motivo")
S["CambioTipoPI"]["properties"]["motivo"] = cargar(io.StringIO("type: string\nminLength: 1\n"))
cls = S["ClasificacionTipoPI"]["properties"]
cls["motivo"] = cargar(io.StringIO("type: string\nnullable: true\n"))
cls["cambiadoPor"] = cargar(io.StringIO("type: string\nformat: uuid\nnullable: true\n"))
tp = paths["/parques/{parqueId}/tipo-pi"]["put"]
agregar_ac(tp, "RF-11-AC-5", "RF-11-AC-6")
tp["description"] = str(tp["description"]) + (
    "\nSin `motivo` responde 422 `motivo_requerido`: \"Indique el motivo del cambio de tipo de PI\". Las evidencias de\n"
    "criterios que pasan a NA se conservan con su estado e historial y dejan de contar en el cálculo (RF-11-AC-6).\n")

# --- D-07: versiones anteriores del catálogo en solo lectura (C-14, RF-01-AC-5) ---
vc = S["VersionCatalogo"]
vc["required"].append("estado")
vc["properties"]["estado"] = cargar(io.StringIO(
    "type: string\nenum: [activa, solo_lectura]\n"
    "description: Una versión queda en solo lectura cuando una generación nueva activa otra versión.\n"))
agregar_ac(paths["/generaciones"]["post"], "RF-01-AC-5")
agregar_ac(paths["/versiones-catalogo/{versionId}"]["get"], "RF-01-AC-5")
pc = paths["/criterios/{criterioId}"]["patch"]
agregar_ac(pc, "RF-01-AC-5")
if "409" not in pc["responses"]:
    pc["responses"]["409"] = CommentedMap([("$ref", "#/components/responses/Conflict")])

# --- D-08 a D-12: RF nuevos del SRS de equipo (RF-32 a RF-36) ---
for p in ["/parques/{parqueId}/fases", "/parques/{parqueId}/fases/{fase}/cierre", "/parques/{parqueId}/avances-fase",
          "/parques/{parqueId}/evaluaciones-desempeno", "/parques/{parqueId}/usuarios",
          "/parques/{parqueId}/contacto-principal", "/bitacora",
          "/parques/{parqueId}/criterios/{criterioId}/recomendaciones"]:
    paths[p] = nuevos_paths[p]
paths["/auth/register"] = nuevos_paths["/auth/register"]
paths["/auth/login"] = nuevos_paths["/auth/login"]
paths["/auth/me"] = nuevos_paths["/auth/me"]
paths["/auth/logout"] = nuevos_paths["/auth/logout"]
d["components"]["parameters"]["FasePath"] = cargar(io.StringIO(
    "name: fase\nin: path\nrequired: true\nschema:\n  $ref: '#/components/schemas/Fase'\n"))
par = S["Parque"]["properties"]
par["contactoPrincipalId"] = cargar(io.StringIO(
    "type: string\nformat: uuid\nnullable: true\ndescription: Nulo si el parque no tiene contacto principal (RF-34-AC-3).\n"))
for k, v in nuevos_schemas.items():
    if k not in S:
        S[k] = v

# --- Corrección encontrada al probar el backend (revision_sql.md, C-03): en OpenAPI 3.0 un enum con
# nullable: true necesita null en la lista; sin él, los validadores rechazan el nulo. ---
for k in ["TipoPINulable", "FaseNulable"]:
    if None not in S[k]["enum"]:
        S[k]["enum"].append(None)

# ======================================================================================================
# Parte 0 con los S04 de Leonardo y Erick (diferencias_diseno.md, sección 6). Conflictos citados con el ID
# del análisis del agente (evidencia_agente/analisis_diferencias_agente.md).
# ======================================================================================================

# --- D-17 (K-11): el dictamen pertenece al expediente, no a la sesión de comité. RF-14-AC-8 pide aceptar un
# "no otorgar" justo cuando RF-15 impide abrir la sesión. ---
dic = S["Dictamen"]
dic["description"] = (
    "Un dictamen por expediente (parque y generación). `sesionComiteId` es la sesión de comité abierta cuando se\n"
    "capturó o se editó por última vez; es nulo si no había ninguna, como en el \"no otorgar\" de RF-14-AC-8.\n")
dic["properties"]["sesionComiteId"] = cargar(io.StringIO(
    "type: string\nformat: uuid\nnullable: true\n"
    "description: Nulo si el dictamen se capturó sin sesión de comité abierta.\n"))
pd = paths["/parques/{parqueId}/dictamenes"]["post"]
pd["description"] = cargar(io.StringIO("""|
  Coordinación AMPIP o el consultor de comité capturan el dictamen del expediente vigente (`otorgar` o
  `no_otorgar`) con su motivo. Queda en "borrador", visible para Coordinación AMPIP, el Director General y, si hay
  sesión de comité abierta, su consultor de comité, sin contar todavía como dictamen oficial.

  - `otorgar` se valida una sola vez, en la captura, contra las tres condiciones de RD-09 (y de nuevo si un PATCH
    cambia el tipo a `otorgar`).
  - `no_otorgar` no exige ninguna condición (RF-14-AC-8) y se puede capturar aunque RF-15 impida abrir la sesión
    de comité.

  Ninguno de los dos exige sesión de comité. Si hay una abierta, el dictamen queda ligado a ella
  (`sesionComiteId`); sin sesión, solo Coordinación AMPIP captura, porque no hay consultor de comité. Un
  consultor asignado recibe 403.

  Errores:
  - 409 `dictamen_duplicado`: el expediente vigente ya tiene un dictamen (en "borrador" se corrige con PATCH).
  - 422 `otorgar_sin_100_obligatorios`: "No se puede otorgar sin el 100 % de los obligatorios cumplidos".
  - 422 `otorgar_sin_autoevaluacion_revisada`: "No se puede otorgar sin la autoevaluación revisada: hay
    criterios pendientes o en revisión".
  - 422 `otorgar_sin_opinion_favorable`: "No se puede otorgar sin la Opinión de Cumplimiento final favorable del
    consultor".
"""))
pdp = paths["/dictamenes/{dictamenId}"]["patch"]
pdp["description"] = str(pdp["description"]).replace(
    "Dos usos, excluyentes en un mismo cuerpo:",
    "Dos usos, excluyentes en un mismo cuerpo. Si el dictamen no tenía sesión de comité y hay una abierta, la edición\n"
    "lo liga a ella.", 1)
paths["/parques/{parqueId}/dictamenes"]["get"]["description"] = (
    "Devuelve el dictamen de cada expediente del parque (la generación vigente y las anteriores), en \"borrador\" o\n"
    "\"firmado\".\n")

# --- D-19 (O-13, gap 26, RD-14): historial de calificaciones de un criterio. Cada cambio de estado, manual o
# automático, agrega un registro; el criterio del parque guarda solo el estado actual. ---
S["CalificacionCriterio"] = cargar(io.StringIO("""
type: object
description: Un cambio del estado de calificación de un criterio del parque. Solo se agregan; nunca se editan.
required: [id, criterioId, estadoAnterior, estadoNuevo, motivo, origen, consultorId, fecha]
properties:
  id:
    type: string
    format: uuid
  criterioId:
    type: string
    format: uuid
  estadoAnterior:
    $ref: '#/components/schemas/EstadoCalificacion'
  estadoNuevo:
    $ref: '#/components/schemas/EstadoCalificacion'
  motivo:
    type: string
    nullable: true
    description: Obligatorio en la reapertura (RF-27-AC-8).
  origen:
    type: string
    enum: [consultor, sistema]
    description: '`sistema` para los cambios automáticos por evidencia enviada (RF-27-AC-4, RF-27-AC-7).'
  consultorId:
    type: string
    format: uuid
    nullable: true
    description: Nulo cuando `origen` es `sistema`.
  fecha:
    type: string
    format: date-time
"""))
paths["/parques/{parqueId}/criterios/{criterioId}/calificaciones"] = cargar(io.StringIO("""
parameters:
  - $ref: '#/components/parameters/ParqueId'
  - $ref: '#/components/parameters/CriterioId'
get:
  tags: [Criterios del parque]
  operationId: listarCalificacionesCriterio
  summary: Historial de calificaciones de un criterio
  description: |
    Todos los cambios del estado de calificación del criterio en el expediente vigente, del más reciente al más
    antiguo, con quién y cuándo los hizo y el motivo de cada reapertura (RD-14). Incluye los cambios automáticos.
  x-acceptance-criteria: [RF-27-AC-2, RF-27-AC-4, RF-27-AC-7, RF-27-AC-8]
  responses:
    '200':
      description: Historial del criterio.
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/components/schemas/CalificacionCriterio'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
    '404':
      $ref: '#/components/responses/NotFound'
    '500':
      $ref: '#/components/responses/InternalError'
"""))
pcp = paths["/parques/{parqueId}/criterios/{criterioId}"]["patch"]
pcp["description"] = str(pcp["description"]).replace(
    "Se registran fecha y consultor del cambio, y el cálculo de cumplimiento lo refleja.",
    "Cada cambio, incluidos los automáticos de RF-27-AC-4 y AC-7, agrega un registro al historial\n"
    "(`GET /parques/{parqueId}/criterios/{criterioId}/calificaciones`) con fecha, consultor y motivo, y el cálculo de\n"
    "cumplimiento lo refleja.")

# --- D-20 (O-02): el token de recuperación va en el cuerpo, no en la ruta, para que no quede en los registros
# de acceso del proxy. ---
del paths["/recuperaciones-contrasena/{token}"]
del S["RecuperacionContrasenaUpdate"]
del d["components"]["parameters"]["TokenEnlace"]
S["RestablecimientoContrasenaCreate"] = cargar(io.StringIO("""
type: object
required: [token, nuevaContrasena]
properties:
  token:
    type: string
    minLength: 32
    description: Token del enlace de recuperación que llegó por correo.
  nuevaContrasena:
    type: string
    format: password
    minLength: 10
"""))
paths["/restablecimientos-contrasena"] = cargar(io.StringIO("""
post:
  tags: [Autenticación]
  operationId: crearRestablecimientoContrasena
  summary: Fijar contraseña nueva con el enlace de recuperación
  description: |
    Recibe el token del enlace en el cuerpo, fija la contraseña nueva y revoca las sesiones activas del usuario.
    El enlace deja de funcionar 30 minutos después de generado o en cuanto se usa una vez, lo que ocurra primero.

    Errores:
    - 410 `enlace_no_vigente`: el enlace ya se usó o tiene más de 30 minutos.
    - 422 `token_invalido`: el token no corresponde a ningún enlace de recuperación.
  security: []
  x-acceptance-criteria: [RF-26-AC-4]
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/RestablecimientoContrasenaCreate'
  responses:
    '204':
      description: Contraseña actualizada y sesiones anteriores revocadas.
    '400':
      $ref: '#/components/responses/BadRequest'
    '410':
      $ref: '#/components/responses/Gone'
    '422':
      $ref: '#/components/responses/UnprocessableEntity'
    '500':
      $ref: '#/components/responses/InternalError'
"""))

# --- D-21 (gaps 14 y 30): criterios de una versión del catálogo y lista de observaciones de una evidencia ---
paths["/versiones-catalogo/{versionId}/criterios"] = cargar(io.StringIO("""
parameters:
  - $ref: '#/components/parameters/VersionId'
get:
  tags: [Catálogo]
  operationId: listarCriteriosVersion
  summary: Listar los criterios de una versión del catálogo
  description: |
    Criterios de la versión con su método de verificación, sus marcas por tipo de PI y la descripción de evidencia
    suficiente, para que Coordinación AMPIP la capture o la revise (RF-24). Solo Coordinación AMPIP.
  x-acceptance-criteria: [RF-01-AC-1, RF-24-AC-1]
  parameters:
    - $ref: '#/components/parameters/Estandar'
  responses:
    '200':
      description: Criterios de la versión, ordenados por clave.
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/components/schemas/Criterio'
    '401':
      $ref: '#/components/responses/Unauthorized'
    '403':
      $ref: '#/components/responses/Forbidden'
    '404':
      $ref: '#/components/responses/NotFound'
    '500':
      $ref: '#/components/responses/InternalError'
"""))
paths["/evidencias/{evidenciaId}/observaciones"]["get"] = cargar(io.StringIO("""
tags: [Evidencias]
operationId: listarObservaciones
summary: Listar las observaciones de una evidencia
description: |
  Observaciones de la evidencia en todas sus versiones, de la más reciente a la más antigua. Con `criterioId`
  devuelve solo las de ese vínculo. Las recomendaciones del consultor no aparecen aquí (RF-36-AC-2).
x-acceptance-criteria: [RF-05-AC-2, RF-05-AC-6, RF-36-AC-2]
parameters:
  - name: criterioId
    in: query
    required: false
    description: Filtra por el criterio del vínculo observado.
    schema:
      type: string
      format: uuid
responses:
  '200':
    description: Observaciones de la evidencia.
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/Observacion'
  '401':
    $ref: '#/components/responses/Unauthorized'
  '403':
    $ref: '#/components/responses/Forbidden'
  '404':
    $ref: '#/components/responses/NotFound'
  '500':
    $ref: '#/components/responses/InternalError'
"""))

# --- D-23 (gap 50, idea de Erick): los procesos programados del worker quedan declarados en el contrato, con
# sus criterios, aunque no sean rutas. Solo los de prioridad MVP y 2027. ---
d["info"]["x-procesos-programados"] = cargar(io.StringIO("""
- nombre: revision-diaria-plazos
  horario: Diario a las 00:00, America/Mexico_City
  descripcion: |
    Marca como atrasado un renglón del plan de trabajo cuando vence su fecha comprometida y el criterio no está
    cumplido, y marca el parque como atrasado cuando vence su fecha de próxima actualización anual.
  x-acceptance-criteria: [RF-09-AC-2, RF-09-AC-3, RF-30-AC-2, RF-30-AC-3]
- nombre: envio-correos
  horario: Cada minuto
  descripcion: |
    Envía los mensajes pendientes de la outbox (invitaciones, recuperación de contraseña, avisos de observación) con
    hasta 3 intentos; la falla definitiva queda registrada (RNF-12).
  x-acceptance-criteria: []
"""))

# --- Reordenar: las rutas /auth primero, igual que estaba /sesiones ---
orden = ["/auth/register", "/auth/login", "/auth/me", "/auth/logout"]
nuevo = CommentedMap()
for k in orden:
    nuevo[k] = paths[k]
for k in paths:
    if k not in orden:
        nuevo[k] = paths[k]
d["paths"] = nuevo

# --- Etiquetas e info ---
tags = d["tags"]
tags[0]["description"] = "Registro con invitación, inicio y cierre de sesión, recuperación de contraseña (RF-03, RF-26)."
for nombre, desc in [("Fases", "Fases del expediente, cierre y avance por excepción (RF-32)."),
                     ("Configuración", "Parámetros del programa: límite de archivo y vigencia del distintivo (RF-06, RD-08)."),
                     ("Bitácora", "Consulta de la bitácora de solo append (RF-35, RNF-03).")]:
    tags.append(CommentedMap([("name", nombre), ("description", desc)]))
d["info"]["title"] = "SGPIS API (contrato de equipo)"
d["info"]["version"] = "2.0.0"

buf = io.StringIO()
yaml.dump(d, buf)
texto = buf.getvalue()
reemplazos = [
    ("Alcance: requerimientos funcionales del SRS v1.4 con prioridad \"MVP feb-2027\" y \"2027\".\n"
     "    Quedan fuera los RF con prioridad \"Posterior\" (RF-18, RF-19, RF-20, RF-22).",
     "Alcance: requerimientos funcionales de `SRS_equipo.md` v2.0 con prioridad \"MVP feb-2027\" y \"2027\".\n"
     "    Quedan fuera los RF con prioridad \"Posterior\" (RF-18, RF-19, RF-20, RF-22, RF-37, RF-38, RF-39).\n"
     "    Contrato consolidado del equipo 19 (S05-S06-A1); las diferencias con los diseños individuales y su resolución\n"
     "    están en `diferencias_diseno.md`."),
    ("diagrama de clases de S04_A1", "`diagrama_clases_equipo.puml`"),
    ("`POST /parques/{parqueId}/criterios/{criterioId}/evidencias`", "`POST /parques/{parqueId}/evidencias`"),
    ("registrar una observación (`POST /evidencias/{evidenciaId}/observaciones`), que crea un recurso Observación y,\n"
     "    como efecto, pasa la evidencia a \"observada\".",
     "registrar una observación (`POST /evidencias/{evidenciaId}/observaciones`), que crea un recurso Observación y,\n"
     "    como efecto, pasa a \"observada\" el vínculo de la evidencia con ese criterio."),
    ("- **413**: archivo de evidencia mayor a 100 MB (104,857,600 bytes).",
     "- **413**: archivo de evidencia mayor al límite configurado (inicial 100 MB = 104,857,600 bytes, RF-06-AC-6)."),
    ("/api/v1/", "/api/"),
    ("POST /sesiones", "POST /auth/login"),
    ("`PATCH /invitaciones/{token}`", "`POST /auth/register`"),
]
for a, b in reemplazos:
    texto = texto.replace(a, b)
Path(salida).write_text(texto, encoding="utf-8")
print("ok", salida)
