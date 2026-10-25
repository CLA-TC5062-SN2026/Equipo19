# Prompts usados con el agente (S04_A1)

Agente: Claude (Anthropic). Cada parte corrió en una sesión aparte. Insumos comunes: `SRS_final.md` v1.4 (31 RF, 14 RNF, 13 RD, 110 AC) y `stack_decision.md` (S01_A2). Las salidas se guardan sin editar en esta carpeta; lo que cambié y por qué está en los entregables de la raíz.

## Parte 1. Estilo arquitectónico → `estilo_agente.md`

```text
Eres arquitecto de software. Te doy la descripción de mi proyecto y su SRS.

Proyecto: SGPIS, Sistema de Gestión del Programa Parque Industrial Seguro de AMPIP.
Aplicación web que reemplaza Excel, correo y carpetas compartidas para llevar el
expediente de cada parque industrial: catálogo de criterios, autoevaluación, carga
y revisión de evidencias, cálculo de cumplimiento, Opiniones de Cumplimiento,
comité y dictamen. Unos 41 parques hoy, 70 a 80 a futuro, cerca de 150 usuarios.
Lo construye un solo desarrollador en 12 semanas. Stack ya elegido: Python 3.12 +
FastAPI, PostgreSQL 16, React + Vite, Docker compose.

1. Analiza los requerimientos no funcionales del SRS y di cuáles pesan más en la
   decisión de arquitectura.
2. Recomienda un estilo arquitectónico (cliente-servidor, MVC, capas,
   microservicios, event-driven, etc.) con su justificación.
3. Presenta al menos 2 alternativas con sus trade-offs en escalabilidad,
   mantenibilidad, complejidad de implementación y adecuación al equipo (un solo
   desarrollador).
```

## Parte 2. Diagramas de arquitectura → `componentes_agente.puml`, `despliegue_agente.puml`

```text
Con el estilo elegido (monolito modular en capas: SPA en React que consume una API
REST en FastAPI, PostgreSQL), genera en PlantUML:

1. Diagrama de componentes a nivel C4 Container: frontend, backend, base de datos
   y sus interfaces, incluidos los sistemas externos que necesite el SRS.
2. Diagrama de despliegue: cómo se despliega el sistema (servidor cloud,
   contenedores, cliente web). Restricción del SRS: almacenamiento en un solo
   proveedor con región fija en México o Estados Unidos (RNF-05), sin licencias por
   usuario (RD-12), respaldos diarios (RNF-13), monitoreo externo (RNF-08).
```

## Parte 3. Diagrama de clases del dominio → `clases_agente.puml`

```text
Basándote en los requerimientos del SRS, identifica las entidades principales del
dominio de SGPIS y propón un diagrama de clases en PlantUML con:
- atributos principales de cada clase,
- relaciones (asociación, composición, herencia),
- multiplicidades.
```
