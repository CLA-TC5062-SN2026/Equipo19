# SGPIS: frontend

SPA en **React 19 + Vite 8 + Tailwind CSS 4 + React Router 7** que consume la API de `../backend`. La decisión de stack
está en `../S07_S08_A1/decision_stack_frontend.md`.

## Arranque

Con el backend corriendo en `localhost:8000` (ver `../README.md`):

```bash
cp .env.example .env     # VITE_API_URL=http://localhost:8000/api
npm install
npm run dev              # http://localhost:5173
```

## Pantallas

| Ruta | Pantalla | RF |
|---|---|---|
| `/login` | Inicio de sesión con los mensajes del SRS (credenciales incorrectas, bloqueo) | RF-26 |
| `/` | Tablero: parques visibles para el rol, con fase, % de obligatorios, criterios atrasados y actualización anual vencida; filtros por generación, región y estado | RF-07, RF-08, RF-09, RF-30, RF-32 |
| `/parques/nuevo` | Alta de parque (solo Coordinación) | RF-02, RF-28 |
| `/parques/:id` | Expediente: datos, cumplimiento por estándar, fases, criterios con estado y atraso; edición y baja (solo Coordinación) | RF-07, RF-08, RF-29, RF-30, RF-32 |
| `/componentes` | Demo de componentes de S07-S08-A1 | — |

El frontend no decide permisos: muestra u oculta botones según el rol, pero quien niega es la API (403).

## Estructura

```
src/
├── services/     api.js (cliente único: token, errores {codigo, mensaje, detalles}, red caída), auth.js, parques.js
├── sesion/       ProveedorSesion.jsx y useSesion (Context API; regresa al login cuando la API responde 401)
├── components/   Boton, CampoEntrada, CampoSelect, Tarjeta, Navbar, Aviso, Etiqueta, BarraAvance, RutaProtegida
├── pages/        LoginPage, ParquesPage, ParqueNuevoPage, ParqueDetallePage, NoEncontradoPage, DemoComponentes
├── lib/          catalogos.js (etiquetas de enums), errores.js (mensajes y errores por campo), formato.js
├── App.jsx       Rutas
└── index.css     Tailwind + tokens de color con contraste AA
e2e/flujos_s11.py Prueba de punta a punta con Playwright (ver ../README.md, sección Pruebas)
```

## Scripts

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo con recarga |
| `npm run build` | Build de producción en `dist/` |
| `npm run preview` | Sirve el build |
| `npm run lint` | oxlint |
