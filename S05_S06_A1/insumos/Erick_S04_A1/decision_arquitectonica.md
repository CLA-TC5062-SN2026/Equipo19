# ADR-001: Selección del estilo arquitectónico

**Fecha:** 2026-10-07  
**Estado:** Aceptado

## Contexto

El Sistema de Gestión del Programa Parque Industrial Seguro (SGPIS) es una aplicación web que permitirá administrar expedientes, evidencias, evaluaciones y dictámenes de parques industriales.

De acuerdo con el SRS, el sistema debe contemplar aspectos como el control de acceso según roles y parques (RNF-01), la protección de información sensible (RNF-02 y RNF-04), el registro de actividades mediante una bitácora (RNF-03) y el manejo seguro de archivos (RNF-05 y RNF-15).

Además, se considera una escala inicial de hasta 80 parques industriales y 30 cargas de evidencia simultáneas (RNF-07 y RNF-10).

Dado que el proyecto será desarrollado por una sola persona utilizando React + Vite, FastAPI y PostgreSQL, es necesario seleccionar una arquitectura que facilite el mantenimiento, permita cumplir los requerimientos y evite complejidad innecesaria.

## Alternativas consideradas

A partir del análisis del agente de IA, se evaluaron dos alternativas:

| Criterio | Monolito modular por capas | Microservicios |
|---|---|---|
| Escalabilidad | Adecuada para el alcance inicial, aunque requiere escalar la aplicación completa. | Permite escalar servicios de manera independiente. |
| Mantenibilidad | Facilita organizar el código por módulos y responsabilidades. | Ofrece independencia entre servicios, pero requiere mayor coordinación. |
| Complejidad | Baja a media, con una sola aplicación backend. | Alta, debido a la comunicación y administración de múltiples servicios. |
| Desarrollo individual | Alta viabilidad por su simplicidad operativa. | Baja viabilidad debido al trabajo adicional de implementación y mantenimiento. |

## Decisión

He decidido utilizar una **arquitectura de monolito modular por capas**, con React + Vite como frontend, FastAPI como backend y PostgreSQL como base de datos.

Considero que esta arquitectura es la más adecuada porque permite organizar el sistema en módulos independientes a nivel de código, sin necesidad de desplegar múltiples servicios.

El backend podrá dividirse en componentes relacionados con usuarios, expedientes, evidencias, evaluaciones y dictámenes, separando la lógica de negocio del acceso a datos y de las rutas de la API.

Una de las principales razones para elegir esta arquitectura es que desarrollaré el proyecto individualmente. Por lo tanto, considero más importante contar con una estructura clara, fácil de mantener y probar, que implementar una arquitectura distribuida cuya complejidad no se justifica con el alcance actual.

También considero que el monolito modular facilita mantener controles de autorización y auditoría consistentes, lo cual es especialmente importante para los RNF relacionados con seguridad y privacidad.

Aunque los microservicios ofrecen ventajas de escalabilidad, no encuentro una necesidad actual que justifique introducir su complejidad. Prefiero comenzar con una arquitectura más sencilla y evaluar posibles cambios si el sistema crece.

## Consecuencias

**Positivas:**

- Menor complejidad de implementación, despliegue y mantenimiento.
- Organización del código mediante módulos y capas con responsabilidades definidas.
- Mayor facilidad para implementar y verificar controles de seguridad y auditoría.
- Compatibilidad con el stack tecnológico seleccionado.
- Posibilidad de evolucionar la arquitectura conforme aumenten las necesidades del sistema.

**Negativas:**

- No será posible escalar cada módulo de forma independiente sin realizar cambios arquitectónicos.
- Un problema de rendimiento en un módulo podría afectar al resto del backend.
- Será necesario mantener una buena organización del código para evitar dependencias innecesarias entre módulos.

En conclusión, considero que el monolito modular por capas representa el mejor equilibrio entre mantenibilidad, complejidad y escalabilidad para el alcance actual de SGPIS.