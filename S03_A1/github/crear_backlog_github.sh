#!/usr/bin/env bash
# Crea en GitHub las etiquetas, los 22 issues del backlog de SGPIS y el GitHub Project.
# Requisitos: gh CLI autenticado con permiso de proyectos:
#   gh auth login
#   gh auth refresh -s project,read:project
# Uso (desde la carpeta S03_A1/github):
#   ./crear_backlog_github.sh   (por omisión: CLA-TC5062-SN2026/Equipo19)
# Funciona con el bash 3.2 de macOS (no usa arreglos asociativos).

set -euo pipefail

OWNER="${OWNER:-CLA-TC5062-SN2026}"
REPO="${REPO:-Equipo19}"
PROJECT_TITLE="${PROJECT_TITLE:-SGPIS - Product Backlog}"
FULL_REPO="$OWNER/$REPO"
cd "$(dirname "$0")"

# Orden de la columna Backlog: priorización del equipo (priorizacion_comparada.md)
ORDEN="HU-01 HU-02 HU-03 HU-04 HU-06 HU-15 HU-14 HU-05 HU-07 HU-08 HU-10 HU-09 HU-12 HU-13 HU-11 HU-17 HU-18 HU-19 HU-16 HU-20 HU-22 HU-21"

echo "== Etiquetas"
crear_label () { gh label create "$1" --repo "$FULL_REPO" --color "$2" --description "$3" --force >/dev/null; echo "  $1"; }
crear_label "epica:E1" "1f6feb" "Acceso y administración del programa"
crear_label "epica:E2" "8250df" "Autoevaluación y evidencias"
crear_label "epica:E3" "1a7f37" "Seguimiento y cumplimiento"
crear_label "epica:E4" "bf8700" "Opinión, comité y dictamen"
crear_label "epica:E5" "6e7781" "Reportes y vigencia"
crear_label "prioridad:alta"  "d1242f" "Prioridad Alta"
crear_label "prioridad:media" "fb8f44" "Prioridad Media"
crear_label "prioridad:baja"  "afb8c1" "Prioridad Baja"
for sp in 1 2 3 5 8 13; do crear_label "sp:$sp" "ededed" "$sp story points"; done

echo "== Issues"
: > urls.tsv
while IFS=$'\t' read -r id titulo labels cuerpo; do
  [ -z "$id" ] && continue
  existente=$(gh issue list --repo "$FULL_REPO" --state all --search "\"$id \" in:title" --json url,title --jq ".[] | select(.title | startswith(\"$id \")) | .url" | head -n1)
  if [ -n "$existente" ]; then
    url="$existente"; echo "  $id ya existía: $url"
  else
    url=$(gh issue create --repo "$FULL_REPO" --title "$titulo" --body-file "$cuerpo" --label "$labels")
    echo "  $id creado: $url"
  fi
  printf '%s\t%s\n' "$id" "$url" >> urls.tsv
done < issues.tsv

echo "== Proyecto"
NUM=$(gh project list --owner "$OWNER" --format json --jq ".projects[] | select(.title==\"$PROJECT_TITLE\") | .number" | head -n1)
if [ -z "$NUM" ]; then
  NUM=$(gh project create --owner "$OWNER" --title "$PROJECT_TITLE" --format json --jq .number)
  echo "  Proyecto creado: #$NUM"
else
  echo "  Proyecto existente: #$NUM"
fi
gh project link "$NUM" --owner "$OWNER" --repo "$FULL_REPO" >/dev/null 2>&1 || true

PROJECT_ID=$(gh project view "$NUM" --owner "$OWNER" --format json --jq .id)
STATUS_FIELD=$(gh project field-list "$NUM" --owner "$OWNER" --format json --jq '.fields[] | select(.name=="Status") | .id')
TODO_OPT=$(gh project field-list "$NUM" --owner "$OWNER" --format json --jq '.fields[] | select(.name=="Status") | .options[] | select(.name=="Todo") | .id')

echo "== Agregando issues al proyecto en el orden de prioridad"
for id in $ORDEN; do
  url=$(awk -F'\t' -v k="$id" '$1==k {print $2}' urls.tsv)
  item=$(gh project item-add "$NUM" --owner "$OWNER" --url "$url" --format json --jq .id)
  if [ -n "$STATUS_FIELD" ] && [ -n "$TODO_OPT" ]; then
    gh project item-edit --id "$item" --project-id "$PROJECT_ID" --field-id "$STATUS_FIELD" --single-select-option-id "$TODO_OPT" >/dev/null
  fi
  echo "  $id"
done

echo
echo "Listo. Abre el proyecto:"
gh project view "$NUM" --owner "$OWNER" --format json --jq .url
echo "Falta en la interfaz web: crear la vista Board agrupada por Status y tomar la captura (ver README_github.md)."
