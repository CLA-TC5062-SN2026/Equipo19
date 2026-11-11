#!/usr/bin/env bash
# Análisis estático del backend (S09_A1). Uso: desde backend/, `bash scripts/calidad.sh > output_linter.txt`.
# Corre las tres herramientas aunque alguna encuentre problemas y al final devuelve 1 si alguna falló.
cd "$(dirname "$0")/.." || exit 2
estado=0
echo "# Análisis estático del backend de SGPIS (equipo 19)"
echo "# Fecha: $(date '+%Y-%m-%d %H:%M %Z')"
echo "# Commit: $(git rev-parse --short HEAD 2>/dev/null || echo 'sin git')"
echo "# Herramientas: $(uv run pylint --version | head -1) | flake8 $(uv run flake8 --version | head -1 | cut -d' ' -f1) | $(uv run mypy --version) | $(uv run bandit --version | head -1)"
echo "# Configuración: pyproject.toml ([tool.pylint], [tool.mypy], [tool.pydantic-mypy]) y .flake8"
echo "# Alcance: paquete app/ (código de la API). tests/ queda fuera del análisis."
echo
echo "================================================================================"
echo "1. PYLINT   (uv run pylint app)"
echo "================================================================================"
uv run pylint app || estado=1
echo
echo "================================================================================"
echo "2. FLAKE8   (uv run flake8 app --statistics --count)"
echo "================================================================================"
uv run flake8 app --statistics --count || estado=1
echo
echo "================================================================================"
echo "3. MYPY     (uv run mypy)   [archivos y opciones en pyproject.toml]"
echo "================================================================================"
uv run mypy --show-error-codes --pretty || estado=1
echo
echo "================================================================================"
echo "4. BANDIT   (uv run bandit -r app)   [complemento de seguridad]"
echo "================================================================================"
uv run bandit -r app || estado=1
exit $estado
