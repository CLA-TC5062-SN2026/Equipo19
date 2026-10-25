# Explicacion de los diagramas SGPIS

## Alcance y fuentes

Los diagramas se basan en `SRS_equipo.md`, `decision_arquitectonica.md` y las tareas tecnicas de S03-A2. Usan notacion C4: el primer archivo es un diagrama de contenedores del sistema y el segundo muestra su despliegue propuesto.

## Decisiones ya documentadas

- El ADR-001 establece React + Vite como frontend, FastAPI como backend y PostgreSQL como base de datos, en un monolito modular por capas.
- El backend se representa como una unica API. Sus modulos internos son una convencion de organizacion de codigo, no servicios independientes ni unidades de despliegue.
- PostgreSQL contiene datos estructurados, sesiones, estados, referencias y metadatos; las evidencias se guardan fuera de la base de datos en almacenamiento de objetos.
- La API debe autorizar por rol, parque y asignacion antes de exponer evidencias o emitir una URL firmada. Esto responde a RNF-01, RNF-02, RNF-04 y RNF-15.
- La bitacora es transversal y de solo append (RNF-03). Las tareas del Sprint 1 indican que el usuario de aplicacion no tendra permisos de `UPDATE` ni `DELETE` sobre ella.
- El almacenamiento de objetos debe usar un unico proveedor en Mexico o Estados Unidos, cifrado y sin URL publica. El SRS exige URL firmadas de hasta cinco minutos, pero no define proveedor.
- El correo es el canal de notificaciones y requiere hasta tres reintentos (RNF-12), sin que se haya seleccionado un proveedor.

## Propuestas de despliegue

El diagrama de despliegue propone una sola unidad cloud con una API monolitica, PostgreSQL y un proxy inverso, mas almacenamiento de objetos administrado. Esta topologia minimiza componentes que una sola persona debe configurar, monitorear y recuperar. El frontend se ejecuta en el navegador; el proxy entrega sus archivos compilados y enruta las solicitudes REST a FastAPI.

- El proveedor cloud se deja intencionalmente sin nombre: el SRS solo fija la region para los objetos y no selecciona proveedor.
- Docker Compose con PostgreSQL 16 esta documentado en S03-A2 para desarrollo local. Su uso para produccion se marca como propuesta y requiere validacion operativa.
- El proxy inverso y su tecnologia concreta son propuestas. Su funcion seria terminar HTTPS y servir los archivos estaticos sin crear un servicio de negocio adicional.
- Se muestra monitoreo externo porque RNF-08 exige una comprobacion de disponibilidad cada cinco minutos. La herramienta de monitoreo no esta elegida.
- Los respaldos diarios y la restauracion mensual son obligatorios por RNF-13, pero su automatizacion concreta debe definirse conforme al proveedor elegido.

## Consideraciones para revision critica

La propuesta no presupone escalamiento distribuido: los limites del SRS son hasta 80 parques y 30 cargas simultaneas. La respuesta esperada depende de indices, paginacion, pruebas de carga, limites de carga y almacenamiento de objetos, no de dividir el backend en microservicios. Si mediciones futuras demuestran un cuello de botella, deberia evaluarse el componente afectado antes de cambiar el estilo arquitectonico.

La descarga de archivos se representa mediante URL firmadas emitidas solo despues de autorizar la solicitud. Esto evita exponer el almacenamiento como publico, conforme a RNF-15. El diagrama conserva la carga y su validacion en FastAPI, porque los RF-05 y RF-06 asignan al sistema el registro de metadatos y la validacion de formato y tamano; no presupone un mecanismo de carga directa que el SRS no define.
