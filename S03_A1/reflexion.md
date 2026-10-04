# Reflexión: SCRUM y uso de IA para construir el Product Backlog

**Autor:** Ángel Sebastián Kociankowski Montelongo (A01379225), Gpo 10, TC5062

## 1. Ventajas y riesgos de usar un agente para generar el Product Backlog

La ventaja más clara fue la velocidad en el trabajo mecánico. El agente leyó los tres SRS individuales, unos 180 KB de texto, y en una pasada listó 17 requerimientos en consenso, los gaps de cada integrante y 19 conflictos con el ID de cada versión. Hacer esa tabla a mano habría tomado una tarde y seguramente me habría saltado algunos. Lo mismo con el backlog: 17 historias en el formato correcto, con estimación y prioridad, en minutos. También fue útil como revisor de mi propio trabajo. En el análisis de diferencias advirtió que mi SRS, al ser la base más probable, podía meter al documento de equipo decisiones que solo yo había tomado, y puso como ejemplo que Coordinación AMPIP no vea el contenido de las evidencias de seguridad. Tenía razón, y por eso esa decisión quedó como conflicto C-03 para que el equipo la ratificara en lugar de entrar sin discusión.

El riesgo principal es que la salida se ve terminada antes de estarlo. El backlog v0 tenía todo lo que pedía el formato y aun así no podía funcionar: le faltaba la historia del análisis de riesgos, y sin ella la historia de calificar criterios no podía cerrar 3 de los 10 estándares. Varios criterios de aceptación tenían forma de criterio sin serlo ("el estado se actualiza correctamente"). Dos historias estaban escritas desde "el sistema". Nada de eso salta a la vista si uno revisa que haya dos criterios por historia y un número de Fibonacci; hay que leer cada historia contra el SRS.

El segundo riesgo es la falsa objetividad. La priorización del agente vino con una fórmula, una tabla de puntajes y decimales. Se ve más rigurosa que mi lista sin números. Pero el juicio estaba en los puntajes de 1 a 10, y el agente los asignó a partir de las etiquetas del SRS. Con eso mandó el historial de parques al lugar 19, cuando el cliente real lo había puesto entre lo indispensable del primer mes. Un equipo con prisa acepta esa tabla porque parece análisis.

El tercero es de manejo de información. El catálogo de criterios es propiedad de AMPIP (RD-05) y las evidencias de los parques son información de seguridad. Al agente solo le dimos los SRS, que describen el sistema sin contener el texto del checklist ni datos de ningún parque. Si en semanas posteriores alguien le pasa el CSV del catálogo o evidencias reales para generar datos de prueba, estaríamos sacando información del cliente a un servicio externo sin su autorización.

## 2. ¿Puede un agente reemplazar al Product Owner?

No en este proyecto, y no creo que sea un tema de capacidad del modelo.

El Product Owner responde por el valor de lo que se construye ante alguien. En SGPIS ese alguien es AMPIP, y la información que más cambió el producto no estaba en ningún documento hasta que alguien se sentó con el miembro del comité y le preguntó. "Si no está terminada no entregamos" eliminó el dictamen con condiciones y reescribió RD-09, RF-14 y RF-15. El agente trabaja con lo que le damos; no puede ir a buscar la siguiente respuesta, ni notar en una entrevista que el cliente duda, ni regresar con AMPIP a decir que algo no cabe en 12 semanas y negociar qué sale.

El PO también decide qué no se construye y carga con esa decisión. La resolución C-03 es un buen ejemplo: ocultar a Coordinación AMPIP el contenido de las evidencias de seguridad protege a los parques, pero le quita visibilidad al dueño del programa. Si mañana AMPIP pregunta por qué no puede abrir el plan de contingencia de un parque, alguien del equipo tiene que explicar la decisión y responder por ella. Un agente puede proponer la resolución y su razón; no puede ser responsable de ella.

Lo que sí puede hacer, y lo hizo bien, es trabajar como asistente del PO: preparar borradores, detectar inconsistencias entre documentos, calcular, proponer un orden con un método explícito y atrapar algunas dependencias. Usado así ahorra tiempo. Usado como sustituto, le entrega al equipo un backlog con buena forma y prioridades que nadie defendió frente al cliente.

## 3. Cómo afecta la calidad del SRS a la calidad del backlog

De forma directa, y en los dos sentidos.

Donde el SRS de equipo era preciso, el backlog salió bien casi sin esfuerzo. Los 150 criterios de aceptación con valores concretos me permitieron reescribir cada criterio de cada historia citando su AC de origen. Por ejemplo, el rechazo de video en la historia de carga de evidencias es RF-06-AC-4, con su mensaje exacto. Eso deja la historia lista para escribir la prueba y conecta el backlog con las pruebas de semanas posteriores sin trabajo extra.

Donde el SRS era vago, el backlog heredó la vaguedad. La secuencia de fases sigue pendiente de confirmar con AMPIP, y la historia de la vista de avance depende de ella. El papel de la Evaluación de Desempeño en el dictamen no está definido, y por eso no tiene historia todavía. Ningún agente puede escribir una buena historia sobre un requerimiento que el equipo no ha entendido.

Vale la pena pensar qué habría salido sin la consolidación de la Parte 0. Con el SRS de Erick como base, el backlog habría tenido historias para un "evaluador de AMPIP", un rol que el cliente real nunca mencionó. Con el de Leonardo, varios criterios habrían salido de AC como "el sistema debe permitir gestionar el proceso", que no se pueden probar. Con el mío solo, faltarían la gestión explícita de fases y el contacto principal de la APPI. El agente no mejora los requerimientos; produce más rápido sobre lo que le damos, con sus aciertos y sus huecos.

La lección que me llevo es sobre lo que hay que escribir en el SRS. El agente tomó literalmente las etiquetas de prioridad (MVP, 2027, Posterior) y no tenía forma de saber cuáles venían de una frase del cliente real y cuáles de un supuesto del equipo. Si el SRS registra la razón de cada prioridad y quién la pidió, con la cita cuando existe, cualquiera que genere el backlog después, persona o agente, va a priorizar con el mismo criterio con que se escribieron los requerimientos.
