#!/usr/bin/env bash
# Pruebas manuales de protección de rutas (S05-S06-A2, parte 2). Requiere la API en http://localhost:8000 con la
# base recién cargada y `uv run python -m app.semilla --demo`. Uso: ./pruebas_terminal.sh <token_invitacion>
set -u
API=http://localhost:8000/api
TOKEN_INVITACION="$1"
CORREO=coordinacion.demo@ampip.mx
CONTRASENA="${CONTRASENA_DEMO:-contrasena-demo-2026}"
APPI_CORREO=appi.demo@parquedemo.mx
APPI_CONTRASENA="${SEMILLA_APPI_CONTRASENA:?exporta SEMILLA_APPI_CONTRASENA}"
GEN=$(psql -h localhost -U postgres -d sgpis -tAc "select id from generacion where nombre='2027'")
PARQUE='{"tipoRegistro":"activo","nombre":"Parque Prueba Terminal","desarrollador":"Desarrolladora Demo","tipoPI":"operacion_cerrado","region":"MX-NLE","generacionId":"'"$GEN"'"}'

caso() { echo; echo "### $1"; shift; echo "\$ curl $*" | sed -E 's/Bearer [A-Za-z0-9._-]+/Bearer <token>/'; curl -s -w '\nHTTP %{http_code}\n' "$@"; }

caso "0. Registro con la invitación" -X POST $API/auth/register -H 'Content-Type: application/json' \
  -d '{"tokenInvitacion":"'"$TOKEN_INVITACION"'","contrasena":"'"$CONTRASENA"'"}'
TOKEN=$(curl -s -X POST $API/auth/login -H 'Content-Type: application/json' \
  -d '{"correo":"'"$CORREO"'","contrasena":"'"$CONTRASENA"'"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
TOKEN_APPI=$(curl -s -X POST $API/auth/login -H 'Content-Type: application/json' \
  -d '{"correo":"'"$APPI_CORREO"'","contrasena":"'"$APPI_CONTRASENA"'"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')
ALTERADO="${TOKEN%?}$( [ "${TOKEN: -1}" = "A" ] && echo B || echo A )"

caso "1. Ruta protegida sin token (esperado 401)" -X POST $API/parques -H 'Content-Type: application/json' -d "$PARQUE"
caso "2. Ruta protegida con token inválido, último carácter cambiado (esperado 401)" -X POST $API/parques \
  -H "Authorization: Bearer $ALTERADO" -H 'Content-Type: application/json' -d "$PARQUE"
caso "3. Ruta protegida con rol incorrecto, APPI (esperado 403)" -X POST $API/parques \
  -H "Authorization: Bearer $TOKEN_APPI" -H 'Content-Type: application/json' -d "$PARQUE"
caso "4. Ruta protegida con token válido y rol correcto, Coordinación AMPIP (esperado 201)" -X POST $API/parques \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$PARQUE"
OTRO=$(psql -h localhost -U postgres -d sgpis -tAc "select id from parque where nombre='Parque Prueba Terminal'")
caso "5. APPI de Parque Demo consulta otro parque (esperado 403, RNF-01)" $API/parques/$OTRO -H "Authorization: Bearer $TOKEN_APPI"
caso "6. Bitácora: el intento denegado quedó registrado (esperado 200)" "$API/bitacora?accion=acceso_denegado&tamanoPagina=5" \
  -H "Authorization: Bearer $TOKEN"
