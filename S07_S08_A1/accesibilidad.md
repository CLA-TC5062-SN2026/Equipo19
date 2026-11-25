# Evaluación básica de accesibilidad (WCAG 2.1)

**Proyecto:** SGPIS. Equipo 19, TC5062
**Actividad:** S07-S08-A1, Parte 3
**Alcance:** los cuatro componentes de la Parte 2 y la página de demo, contra WCAG 2.1 nivel AA en tres frentes: contraste de color, nombres accesibles donde no hay texto visible, y manejo del foco.

## Método

1. **Contraste medido, no estimado.** Calculamos la razón de contraste de cada par color de texto / fondo y de los bordes de controles con la fórmula de luminancia relativa de WCAG (la misma que usa WebAIM Contrast Checker), con un script de Node sobre los valores hex reales de la paleta Tailwind del proyecto.
2. **Revisión de marcado** de cada componente contra los criterios 1.1.1, 1.3.1, 1.4.1, 3.3.1, 3.3.2 y 4.1.2.
3. **Prueba de teclado en el navegador** (servidor de desarrollo): recorrido con Tab por todos los interactivos, verificando indicador de foco visible (2.4.7) y que el menú móvil se opera sin ratón.

## Problemas encontrados y correcciones

Los dos primeros son los críticos que pide la actividad; ambos quedaron corregidos en el código.

### 1. (Crítico, corregido) Bordes de controles por debajo de 3:1 — WCAG 1.4.11 Contraste no textual

El borde `gray-400` (#99a1af) que la primera versión usaba en el campo de entrada y en el botón secundario da **2.60:1** sobre blanco, por debajo del mínimo de **3:1** que exige 1.4.11 para la parte visual que identifica un control. Para un usuario con baja visión, el límite del campo de texto prácticamente desaparece: no se ve dónde hay que hacer click para escribir.

**Corrección** (`CampoEntrada.jsx`, `Boton.jsx`): borde `gray-500` (#6a7282), que da **4.84:1**. El estado de error ya usaba `red-700` (6.47:1), que cumplía.

### 2. (Crítico, corregido) Botón del menú móvil sin nombre accesible — WCAG 4.1.2 Nombre, función, valor / 1.1.1 Contenido no textual

El botón de hamburguesa del Navbar venía solo con el SVG del icono: un lector de pantalla lo anunciaba como "botón" a secas, sin decir qué hace ni si el menú está abierto.

**Corrección** (`Navbar.jsx`): texto `sr-only` que alterna entre "Abrir menú" y "Cerrar menú", `aria-expanded` con el estado real, `aria-controls="menu-principal"` apuntando al contenedor del menú, y `aria-hidden="true"` en el SVG para que el icono no se anuncie por separado. Verificado con teclado: el botón recibe foco, Enter/Espacio alternan el menú y el estado se refleja en `aria-expanded`.

### 3. (Corregido) Error de validación señalado solo por color — WCAG 1.4.1 Uso del color / 3.3.1 Identificación de errores

En la primera versión del campo, el estado inválido era únicamente el borde rojo. Quien no distingue el rojo, o quien usa lector de pantalla, no recibía el error.

**Corrección** (`CampoEntrada.jsx`): mensaje de error en texto (`red-700`, 6.47:1, además en semibold para no depender solo del color), asociado al input con `aria-describedby={id}-error` y `aria-invalid="true"`, de modo que el lector de pantalla anuncia el error al enfocar el campo. Verificado en la demo: enviar el formulario vacío muestra "El correo es obligatorio." bajo el campo y el input queda marcado inválido.

### 4. (Corregido) Placeholder con contraste insuficiente — WCAG 1.4.3 Contraste mínimo

El placeholder heredaba el gris por defecto (`gray-400`, **2.60:1**), por debajo del **4.5:1** para texto normal. **Corrección:** `placeholder:text-gray-600` (**7.56:1**) en `CampoEntrada.jsx`. Además el placeholder es solo un ejemplo de formato: la instrucción real vive en el `label` visible y en el texto de ayuda (3.3.2), así que ningún campo depende del placeholder para explicarse.

### 5. (Corregido) Indicador de foco explícito — WCAG 2.4.7 Foco visible

Más que un defecto, un riesgo: el anillo de foco quedaba al valor por defecto de cada navegador, que sobre el fondo azul del navbar se pierde. **Corrección:** todos los interactivos llevan `focus-visible:outline-2` con `outline-offset`; sobre fondo azul el contorno es blanco (6.70:1 contra el azul) y sobre fondo claro es `primario-700` o `red-700` según el estado. Verificado con Tab en el navegador.

## Mejoras añadidas durante la evaluación

- **Enlace "Saltar al contenido"** (2.4.1 Evitar bloques): primer elemento enfocable de la página; invisible hasta recibir foco. Verificado: el primer Tab lo muestra sobre el navbar.
- **Estado de carga anunciado** (4.1.2): el botón en carga lleva `aria-busy` y se deshabilita, con el texto siempre visible.
- **`aria-current="page"`** en el enlace activo del navbar, en lugar de solo el fondo más oscuro (1.4.1).
- **`lang="es"`** en `index.html` (3.1.1 Idioma de la página), que el template de Vite trae como `en`.

## Contrastes finales de la paleta

| Par | Razón | Criterio | Resultado |
|---|---|---|---|
| Texto principal `gray-900` sobre blanco | 17.75:1 | 1.4.3 (≥ 4.5) | Cumple |
| Texto secundario y ayuda `gray-600` sobre blanco | 7.56:1 | 1.4.3 (≥ 4.5) | Cumple |
| Blanco sobre `primario-700` (navbar, botón primario) | 6.70:1 | 1.4.3 (≥ 4.5) | Cumple |
| Blanco sobre `primario-800` (badge de rol, hover) | 8.72:1 | 1.4.3 (≥ 4.5) | Cumple |
| Error `red-700` sobre blanco | 6.47:1 | 1.4.3 (≥ 4.5) | Cumple |
| Borde de controles `gray-500` sobre blanco | 4.84:1 | 1.4.11 (≥ 3.0) | Cumple |

Nota: el botón deshabilitado (`opacity-60`) queda por debajo de 4.5:1, pero los controles inactivos están explícitamente exentos del criterio 1.4.3.

## Pendientes para las siguientes semanas

- Mover el foco al primer campo con error al enviar un formulario inválido (3.3.1 va más fluido con manejo de foco), y una región `aria-live` para errores que vienen del API.
- Cuando exista navegación real entre páginas (router), anunciar el cambio de página y devolver el foco al inicio del contenido.
- Pasar axe DevTools sobre cada pantalla nueva del MVP antes de darla por terminada.
