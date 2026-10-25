# ADR-001: Selección del estilo arquitectónico
**Fecha:** 2026-10-09
**Estado:** Aceptado
**Contexto:** 
El Sistema de Gestión del Programa Parque Industrial Seguro (SGPIS) requiere centralizar la gestión de parques industriales, el checklist de seguridad, las evidencias documentales, las revisiones de consultores y la generación de opiniones y evaluaciones. Actualmente, estos procesos dependen de herramientas como hojas de cálculo, correo electrónico y carpetas compartidas. El sistema debe garantizar la seguridad de la información, el aislamiento de los datos por parque, la trazabilidad de las operaciones y el almacenamiento seguro de evidencias. Además, debe permitir el crecimiento de 41 a entre 70 y 80 parques industriales, mantener tiempos de respuesta adecuados y ofrecer disponibilidad y acceso desde dispositivos móviles.

Considerando el alcance funcional, los requerimientos no funcionales, el uso de Python, PostgreSQL y almacenamiento de objetos, así como el tiempo de implementación de 12 semanas, se necesita una arquitectura que facilite el desarrollo, las pruebas y el mantenimiento sin introducir complejidad operativa innecesaria.

**Decisión:** 
Se decidió ir por una arquitectura monolítica modular organizada en capas, bajo un modelo cliente-servidor. La aplicación contará con un frontend web para la interacción con los usuarios y un backend desarrollado en Python que expondrá una API REST. El backend se organizará en módulos funcionales para la gestión de usuarios y permisos, parques industriales, checklist, evidencias, revisiones, evaluaciones, notificaciones, auditoría y reportes.

PostgreSQL se utilizará para almacenar los datos estructurados, los estados de los procesos, los metadatos y las referencias a los archivos. Las evidencias se almacenarán en un servicio de almacenamiento de objetos, con controles de acceso y mecanismos de protección para la información sensible. Las tareas que no requieran una respuesta inmediata, como el envío de notificaciones por correo electrónico y ciertos procesos programados, podrán ejecutarse mediante un trabajador en segundo plano.

Esta arquitectura permitirá mantener una separación clara de responsabilidades y facilitar futuras modificaciones. Si el crecimiento del sistema o las necesidades operativas lo justifican, los módulos con mayores requerimientos de escalabilidad podrán extraerse posteriormente como servicios independientes.

**Alternativas consideradas:**
**Arquitectura de microservicios orientada a eventos.** 
Divide el sistema en servicios independientes, por ejemplo, gestión de usuarios, parques, evidencias y evaluaciones. La comunicación entre servicios puede apoyarse en APIs y eventos asíncronos. Esta alternativa ofrece mayor independencia de despliegue y escalabilidad por componente, pero requiere más infraestructura, monitoreo, coordinación y mecanismos para gestionar la comunicación y consistencia entre servicios.

**Consecuencias:**
Ventajas:
* Reduce la complejidad inicial de desarrollo, despliegue y operación.
* Facilita la implementación dentro del plazo establecido y resulta adecuada para un equipo de desarrollo pequeño.
* Permite organizar el código en módulos, favoreciendo la mantenibilidad y las pruebas independientes de cada componente.
* Simplifica las transacciones y la consistencia de los datos al utilizar una base de datos relacional centralizada.
* Permite escalar inicialmente los recursos del backend y la base de datos, además de optimizar consultas e índices conforme aumente la carga.
* Facilita la integración con almacenamiento de objetos para separar los archivos de los datos estructurados.
* Permite incorporar procesamiento asíncrono para notificaciones y tareas programadas sin adoptar una arquitectura distribuida completa.
* Conserva la posibilidad de extraer módulos como servicios independientes si aparecen necesidades justificadas.

Desventajas:
* El backend se despliega como una unidad, por lo que una modificación puede requerir desplegar nuevamente toda la aplicación.
* La escalabilidad independiente de cada módulo es limitada en comparación con los microservicios.
* Un módulo con alto consumo de recursos puede afectar el rendimiento general si no se controla adecuadamente.
* La separación modular depende de mantener límites claros entre componentes; de lo contrario, pueden generarse dependencias que dificulten el mantenimiento.
* La arquitectura, por sí sola, no garantiza los requerimientos de seguridad, disponibilidad y rendimiento. Será necesario implementar controles de acceso por parque y rol, auditoría, cifrado, respaldos, pruebas de restauración y pruebas de carga.