#!/usr/bin/env bash
# Sprint 1 de SGPIS en GitHub:
#  - crea HT-01 (habilitador) y HU-23 (pantallas, división de HU-01)
#  - crea las 14 tareas como issues, asignadas a ti, con etiquetas de rol y horas
#  - las liga como sub-issues de HT-01 y HU-01 y agrega la lista de tareas al cuerpo de cada padre
#  - mueve HT-01, HU-01 y las tareas a la columna "Sprint actual" del tablero; HU-23 a "Backlog"
# Uso, desde S03_A2/github:   ./crear_tareas_sprint1.sh
# Se puede correr más de una vez: no duplica issues.

set -euo pipefail
OWNER="${OWNER:-CLA-TC5062-SN2026}"
REPO="${REPO:-Equipo19}"
PROJECT_TITLE="${PROJECT_TITLE:-Tablero Kanban S03}"
FULL_REPO="$OWNER/$REPO"
cd "$(dirname "$0")"

# Lista completa de issues (sin búsqueda, para no depender del índice de búsqueda)
listar () { gh issue list --repo "$FULL_REPO" --state all --limit 300 --json number,title --jq '.[] | "\(.number)\t\(.title)"'; }
numero_de () { listar | awk -F'\t' -v p="$1 " '!f && index($2,p)==1 {print $1; f=1}'; }
crear_issue () { # titulo cuerpo etiquetas [asignar]
  local url
  if [ "${4:-}" = "si" ]; then
    url=$(gh issue create --repo "$FULL_REPO" --title "$1" --body-file "$2" --label "$3" --assignee "@me")
  else
    url=$(gh issue create --repo "$FULL_REPO" --title "$1" --body-file "$2" --label "$3")
  fi
  echo "${url##*/}"
}

echo "== Etiquetas"
lab () { gh label create "$1" --repo "$FULL_REPO" --color "$2" --description "$3" --force >/dev/null; echo "  $1"; }
lab "tarea" "0e8a16" "Tarea técnica de una historia"
lab "habilitador" "5319e7" "Trabajo técnico sin story points que habilita historias"
lab "sprint:1" "fbca04" "Comprometido en el Sprint 1"
lab "rol:backend" "1d76db" "Backend dev"
lab "rol:qa" "c5def5" "QA"
lab "rol:devops" "bfdadc" "DevOps"
lab "rol:seguridad" "b60205" "Revisión de seguridad"
for h in 2 3 4; do lab "horas:$h" "ededed" "Estimación de $h horas"; done

echo "== Elementos padre"
HU01=$(numero_de "HU-01")
[ -z "$HU01" ] && { echo "No encontré HU-01 en $FULL_REPO"; exit 1; }
gh issue edit "$HU01" --repo "$FULL_REPO" --add-label "sprint:1" >/dev/null
echo "  HU-01 es #$HU01"

HT01=$(numero_de "HT-01")
if [ -z "$HT01" ]; then
  HT01=$(crear_issue "HT-01 Esqueleto técnico del backend (habilitador del Sprint 1)" HT-01.md "habilitador,sprint:1,prioridad:alta")
  echo "  HT-01 creado: #$HT01"
else
  echo "  HT-01 ya existía: #$HT01"
fi

HU23=$(numero_de "HU-23")
if [ -z "$HU23" ]; then
  HU23=$(crear_issue "HU-23 Como usuario del programa, quiero pantallas para iniciar sesión, cerrar sesión y recuperar mi contraseña, para usar el sistema desde el navegador" HU-23.md "epica:E1,prioridad:alta,sp:3")
  gh issue comment "$HU01" --repo "$FULL_REPO" --body "Sprint 1 Planning: esta historia se dividió. HU-01 conserva la API y los seis criterios de RF-26, verificados contra endpoints. Las pantallas pasan a #$HU23, que se planea en el primer sprint con frontend (semanas 7 y 8 del curso)." >/dev/null
  echo "  HU-23 creado: #$HU23 (y comentario de la división en HU-01)"
else
  echo "  HU-23 ya existía: #$HU23"
fi

echo "== Tareas"
: > tareas_urls.tsv
while IFS=$'\t' read -r id padre titulo etiquetas cuerpo; do
  [ -z "$id" ] && continue
  n=$(numero_de "$id")
  if [ -z "$n" ]; then
    n=$(crear_issue "$titulo" "$cuerpo" "$etiquetas" si)
    echo "  $id creado: #$n"
  else
    echo "  $id ya existía: #$n"
  fi
  if [ "$padre" = "HT-01" ]; then p="$HT01"; else p="$HU01"; fi
  printf '%s\t%s\t%s\t%s\n' "$id" "$n" "$p" "$titulo" >> tareas_urls.tsv
done < tareas.tsv

echo "== Sub-issues"
nodo () { gh issue view "$1" --repo "$FULL_REPO" --json id --jq .id; }
while IFS=$'\t' read -r id n p titulo; do
  if gh api graphql -H "GraphQL-Features: sub_issues" \
      -f query='mutation($p:ID!,$c:ID!){addSubIssue(input:{issueId:$p,subIssueId:$c}){issue{number}}}' \
      -f p="$(nodo "$p")" -f c="$(nodo "$n")" >/dev/null 2>&1; then
    echo "  #$n bajo #$p"
  else
    echo "  #$n: no se pudo ligar como sub-issue (puede que ya lo esté); queda en la lista del padre"
  fi
done < tareas_urls.tsv

echo "== Lista de tareas en el cuerpo de cada padre"
for p in "$HT01" "$HU01"; do
  cuerpo=$(gh issue view "$p" --repo "$FULL_REPO" --json body --jq .body)
  case "$cuerpo" in
    *"## Tareas del Sprint 1"*) echo "  #$p ya tenía la lista";;
    *)
      { printf '%s\n\n## Tareas del Sprint 1\n\n' "$cuerpo"
        awk -F'\t' -v p="$p" '$3==p {print "- [ ] #" $2 " " $1}' tareas_urls.tsv; } > cuerpo_tmp.md
      gh issue edit "$p" --repo "$FULL_REPO" --body-file cuerpo_tmp.md >/dev/null
      rm -f cuerpo_tmp.md
      echo "  #$p actualizado";;
  esac
done

echo "== Tablero"
NUM=$(gh project list --owner "$OWNER" --format json --jq ".projects[] | select(.title==\"$PROJECT_TITLE\") | .number" | head -n1)
[ -z "$NUM" ] && { echo "No encontré el proyecto \"$PROJECT_TITLE\""; exit 1; }
PID=$(gh project view "$NUM" --owner "$OWNER" --format json --jq .id)
FIELD=$(gh project field-list "$NUM" --owner "$OWNER" --format json --jq '.fields[] | select(.name=="Status") | .id')
OPT_SPRINT=$(gh project field-list "$NUM" --owner "$OWNER" --format json --jq '.fields[] | select(.name=="Status") | .options[] | select(.name|ascii_downcase=="sprint actual") | .id')
OPT_BACKLOG=$(gh project field-list "$NUM" --owner "$OWNER" --format json --jq '.fields[] | select(.name=="Status") | .options[] | select(.name|ascii_downcase=="backlog") | .id')
[ -z "$OPT_SPRINT" ] && { echo "No encontré la columna \"Sprint actual\" en el campo Status"; exit 1; }

mover () { # numero opcion
  local url item
  url="https://github.com/$FULL_REPO/issues/$1"
  item=$(gh project item-add "$NUM" --owner "$OWNER" --url "$url" --format json --jq .id)
  gh project item-edit --id "$item" --project-id "$PID" --field-id "$FIELD" --single-select-option-id "$2" >/dev/null
}
mover "$HT01" "$OPT_SPRINT"; echo "  HT-01 → Sprint actual"
mover "$HU01" "$OPT_SPRINT"; echo "  HU-01 → Sprint actual"
while IFS=$'\t' read -r id n p titulo; do mover "$n" "$OPT_SPRINT"; echo "  $id → Sprint actual"; done < tareas_urls.tsv
[ -n "$OPT_BACKLOG" ] && { mover "$HU23" "$OPT_BACKLOG"; echo "  HU-23 → Backlog"; }

echo
echo "Listo: https://github.com/orgs/$OWNER/projects/$NUM"
