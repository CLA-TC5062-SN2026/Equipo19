# Prompts usados con el agente (S05-S06-A2)

Las salidas del agente quedaron sin editar en el historial de git del backend: commit "v0 del módulo de autenticación generado por el agente" (parte 1) y commit "v0 de la protección de rutas generado por el agente" (parte 2). Las correcciones están en `revision_seguridad.md`.

## Prompt 1: módulo de autenticación (Parte 1)

```text
Eres un desarrollador Python. Agrega el módulo de autenticación completo a un backend FastAPI existente, siguiendo el
contrato OpenAPI del equipo.

Insumos: openapi_equipo.yaml (operaciones bajo /auth, securitySchemes: BearerAuth y los schemas RegistroCreate,
SesionCreate, SesionCreada, SesionActual, Usuario y Error); el backend existente (main.py, comun.py con la dependencia
provisional usuario_actual, modelos.py con las tablas usuario, sesion, enlace_un_solo_uso, intento_login y
registro_bitacora, routers/usuarios.py, errores.py); esquema_bd.sql (no se cambia).

Implementa:
- POST /api/auth/register: registro con el token de invitación; contraseña con hash bcrypt; responde 201 con los
  datos del usuario, sin la contraseña.
- POST /api/auth/login: autenticación con correo y contraseña; 200 con el token JWT; 401 con credenciales
  incorrectas; bloqueo tras 5 intentos fallidos (429).
- GET /api/auth/me: ruta protegida que devuelve el usuario autenticado a partir del token.
- POST /api/auth/logout.
- Middleware (o dependencia de FastAPI) de autenticación que valide el JWT del encabezado
  Authorization: Bearer <token> y rechace las peticiones sin token válido con 401.
- Usa variables de entorno para el secret del JWT y el tiempo de expiración: JWT_SECRET y JWT_EXPIRATION.
  Agrégalas a .env.example y a la configuración.
- Usa PyJWT y bcrypt.
- Reemplaza la dependencia provisional usuario_actual para que el actor sea el usuario autenticado.
- En esta tarea NO protejas todavía las rutas CRUD existentes ni implementes control por rol.

Escribe el código en una sola pasada; es un borrador que el equipo revisará con enfoque de seguridad.
```

## Prompt 2: protección de rutas y control por rol (Parte 2)

```text
Eres un desarrollador Python. En un backend FastAPI que ya tiene módulo de autenticación JWT, aplica el middleware de
seguridad a los endpoints CRUD existentes y agrega control de acceso por rol.

Insumos: openapi_equipo.yaml (security: [BearerAuth: []] global; las operaciones con security: [] son públicas; la
description de cada operación dice qué rol puede ejecutarla y quién recibe 403); SRS_equipo.md (2.3, RNF-01, RNF-02 y
los AC que mencionan 403); el backend (seguridad.py, comun.py con la rama transitoria del usuario técnico, main.py y
routers/).

Tareas:
1. Identifica qué rutas implementadas deben estar protegidas según el contrato (las que no tienen security: []) y
   aplícales el middleware de autenticación: sin token válido, 401.
2. Implementa control de acceso por rol: además de validar el token, verifica que el rol del usuario (leído de la
   base, nunca del token) tiene permiso para esa ruta específica; si no, 403 con el schema Error. Aplica también el
   aislamiento por parque: una APPI solo opera su parque, un consultor solo los parques donde tiene asignación
   vigente, un gerente corporativo solo los parques de su desarrollador.
3. Registra en la bitácora cada acceso denegado con 403 (RF-35-AC-2), con resultado "denegado".
4. Elimina la rama transitoria del usuario técnico y su configuración.
5. Deja el mapa de permisos en un solo lugar del código, fácil de leer y revisar.

Escribe el código en una sola pasada; es un borrador que el equipo revisará.
```
