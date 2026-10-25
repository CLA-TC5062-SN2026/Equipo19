# Revisión inicial

Se revisó `openapi.yaml` tomando como referencia el `SRS_equipo.md` y los diagramas de clases y componentes.

La especificación es coherente en términos generales, pero se identificaron algunos puntos por corregir:

1. **Trazabilidad:** agregar el criterio faltante `RF-23-AC-2` y verificar que cada endpoint realmente satisfaga los criterios asociados.
2. **Recuperación de contraseña:** completar el flujo para permitir establecer una nueva contraseña mediante el token recibido.
3. **Evidencias:** aclarar cómo se manejan las versiones, el historial y los archivos vinculados a varios criterios.
4. **Procesos automáticos:** revisar la trazabilidad de las notificaciones por vencimiento y el registro de descargas.
5. **Respuestas HTTP:** agregar códigos 401 en los endpoints protegidos y revisar los demás códigos según corresponda.
6. **Esquemas:** corregir la carga opcional de archivos y documentar las validaciones principales del SRS.
7. **Alcance:** distinguir las funcionalidades del MVP de aquellas previstas para futuras etapas.

# Indicaciones

Realiza únicamente las correcciones necesarias en openapi.yaml, manteniendo la arquitectura y los principios REST.

No modifiques los archivos originales de referencia ni agregues funcionalidades innecesarias.

Al finalizar, valida la especificación OpenAPI 3.0.3 y verifica la cobertura de los 150 criterios de aceptación del SRS.

