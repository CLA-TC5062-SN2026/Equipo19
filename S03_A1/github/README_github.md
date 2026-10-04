# Backlog en GitHub Projects

Esta carpeta crea en GitHub las etiquetas, los 22 issues del backlog y el GitHub Project del equipo.

| Archivo | Contenido |
|---|---|
| `issues.tsv` | Una línea por historia: ID, título (la historia de usuario), etiquetas y archivo con el cuerpo. |
| `issues/HU-xx.md` | Cuerpo de cada issue: épica, story points, prioridad, RF y criterios de aceptación como casillas. |
| `crear_backlog_github.sh` | Script que crea todo con `gh`. Si se vuelve a correr no duplica issues. |

Cada issue lleva tres etiquetas: `epica:E1` a `epica:E5`, `prioridad:alta|media|baja` y `sp:N`.

## Pasos (macOS)

1. Instalar y autenticar la CLI de GitHub:

   ```bash
   brew install gh
   gh auth login
   gh auth refresh -s project,read:project
   ```

2. Correr el script con el repositorio del equipo (`Equipo19` en la organización del curso):

   ```bash
   cd S03_A1/github
   OWNER=CLA-TC5062-SN2026 REPO=Equipo19 ./crear_backlog_github.sh
   ```

   Si la organización no permite crear proyectos a tu cuenta, usa `OWNER=@me` solo para el proyecto. En ese caso crea los issues en el repo de la organización editando `FULL_REPO` al inicio del script.

3. En la web, abrir el proyecto y crear la vista de tablero:
   - "New view" y luego "Board".
   - Agrupar por "Status". Los 22 issues quedan en "Todo", en el orden de `priorizacion_comparada.md`.
   - Opcional: en la configuración del campo Status, renombrar "Todo" como "Backlog".
   - En el menú de la vista, en "Fields", activar "Labels" para que se vean épica, prioridad y story points en cada tarjeta.

4. Tomar la captura del tablero completo (Cmd + Shift + 4 en macOS) y guardarla como `S03_A1/backlog_screenshot.png`.

5. Subir la carpeta al repositorio del equipo, como pide la entrega:

   ```bash
   git clone https://github.com/CLA-TC5062-SN2026/Equipo19.git
   cp -R S03_A1 Equipo19/
   cd Equipo19
   git add S03_A1
   git commit -m "S03-A1: SRS de equipo y Product Backlog"
   git push
   ```

   El mismo contenido va en el `.zip` de Canvas.
