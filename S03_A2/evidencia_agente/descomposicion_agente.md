# Salida del Agente 2: descomposición en tareas técnicas

> Salida sin editar del agente de descomposición (prompt en `prompts_agentes.md`). La versión ajustada y los cambios están en `tareas_tecnicas.md`.

## Habilitador técnico: esqueleto del backend

| # | Tarea | Rol | Horas | Criterio de done |
|---|---|---|---|---|
| 1 | Configurar el proyecto: FastAPI, Docker, PostgreSQL y Alembic | DevOps | 6 | El proyecto corre localmente. |
| 2 | Configurar CI/CD con GitHub Actions y despliegue automático | DevOps | 4 | El pipeline se ejecuta en cada push y despliega. |

## HU-01 Iniciar sesión

| # | Tarea | Rol | Horas | Criterio de done |
|---|---|---|---|---|
| 3 | Crear el modelo de usuario | Backend | 2 | El modelo existe en la base de datos. |
| 4 | Implementar login con JWT y bloqueo de cuenta | Backend | 6 | El usuario puede iniciar sesión y la cuenta se bloquea tras 5 intentos. |
| 5 | Implementar logout y expiración del token | Backend | 2 | El JWT expira a los 60 minutos. |
| 6 | Implementar recuperación de contraseña por correo con SendGrid | Backend | 4 | El usuario recibe un correo con el enlace. |
| 7 | Crear la pantalla de login en React | Frontend | 5 | La pantalla permite iniciar sesión. |
| 8 | Escribir pruebas unitarias | QA | 4 | Cobertura de al menos 80 %. |
| 9 | Documentar la API | Backend | 2 | La documentación está actualizada. |

**Total:** 35 horas.
