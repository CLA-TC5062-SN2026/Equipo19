# Evidencia de S09_A1

| Archivo o carpeta | Qué contiene |
|---|---|
| `configuracion/` | `pyproject.toml` (secciones `[tool.pylint]`, `[tool.mypy]` y `[tool.pydantic-mypy]`), `.flake8` y `calidad.sh`, el script que genera `../output_linter.txt`. En el repositorio están en `backend/` y `backend/scripts/`. |
| `pruebas_nuevas/` | Las 7 pruebas de caracterización, las 2 que reproducen CR-03 y CR-04, y el script de medición del listado. En el repositorio están en `backend/tests/`. |
| `pruebas_codigo_original.txt` | pytest sobre el código original con la configuración de las herramientas (paso 1): 82 pasan |
| `pruebas_antes.txt` | pytest en el paso 2: las 82 originales y las 7 de caracterización pasan; las 2 que reproducen CR-03 y CR-04 fallan |
| `pruebas_despues.txt` | pytest sobre el código final: 91 pasan |
| `pruebas_originales_despues.txt` | Solo las 82 pruebas originales sobre el código final: 82 pasan |
| `medicion_antes.txt`, `medicion_despues.txt` | Sentencias SQL y tiempos de `GET /parques` con 10, 41 y 80 parques, tres corridas antes y tres después de R2 |
| `output_linter_despues.txt` | `calidad.sh` sobre el código final, para comparar con `../output_linter.txt` |
| `refactorizacion.diff` | Cambios en `backend/app/` entre el código original y el final |
| `commits.txt` | Los commits de la actividad, uno por paso, con el hash que tienen en el repositorio de trabajo |

Para reproducir todo desde `backend/`: `uv sync`, `uv run pytest`, `uv run pytest tests/medicion_s09.py -s -q` y `bash scripts/calidad.sh`. Las pruebas necesitan PostgreSQL 16 local (ver `backend/README.md`).
