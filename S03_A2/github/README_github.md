# Tareas del Sprint 1 en GitHub Projects

`crear_tareas_sprint1.sh` deja el Sprint 1 reflejado en el tablero "Tablero Kanban S03" del repo Equipo19:

- Crea HT-01 (habilitador técnico) y HU-23 (pantallas de inicio de sesión, que salen de dividir HU-01).
- Crea las 14 tareas de `tareas_tecnicas.md` como issues, asignados a quien corre el script, con las etiquetas `tarea`, `sprint:1`, `rol:…` y `horas:N`.
- Las liga como sub-issues de HT-01 y de HU-01, y agrega la lista de tareas con casillas al cuerpo de cada padre.
- Mueve HT-01, HU-01 y las 14 tareas a la columna "Sprint actual", y deja HU-23 en "Backlog".

Se puede correr más de una vez: busca cada issue por su ID antes de crearlo.

## Pasos

```bash
cd ~/Downloads/S03_A2/github
chmod +x crear_tareas_sprint1.sh
./crear_tareas_sprint1.sh
```

Después, en el tablero:

1. Abre la vista Kanban. "Sprint actual" debe tener 16 tarjetas: HT-01, HU-01 y T-01 a T-14.
2. Para ver las tareas de una historia, abre HU-01 o HT-01: aparecen como sub-issues y como lista de casillas.
3. Opcional, para la entrega: toma una captura de la columna "Sprint actual" y guárdala como `S03_A2/sprint1_tablero.png`.
