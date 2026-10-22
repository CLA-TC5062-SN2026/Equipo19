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
