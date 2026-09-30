# Sistema de Pasajeros - Hotel Duerme Bien

**Tema 6 · Luis Huenchul**

**[VER TODOS LOS ENTREGABLES](https://yutre3.github.io/hotel-duerme-bien/)** · **[ABRIR PROTOTIPO FUNCIONAL](https://yutre3.github.io/hotel-duerme-bien/prototipo/)**

## Informe de requerimientos y modelado

[Informe PDF con diagramas](informe/informe-con-diagramas.pdf) · [Informe editable](informe/requerimientos-y-modelado.md)

Incluye introducción, descripción general, requerimientos preliminares, reglas de negocio, toma de requerimientos, factibilidad, casos de uso, normalización y trazabilidad.

## Casos de uso

![Casos de uso](diagramas/casos-de-uso.svg)

[PDF](diagramas/casos-de-uso.pdf) · [Archivo editable](diagramas-editables/casos-de-uso.drawio) · [Abrir editor](https://app.diagrams.net/?mode=github#HYutre3%2Fhotel-duerme-bien%2Fmain%2Fdiagramas-editables%2Fcasos-de-uso.drawio)

## Procesos

### Check-in

![Check-in](diagramas/flujo-check-in.svg)

[PDF](diagramas/flujo-check-in.pdf) · [Archivo editable](diagramas-editables/flujo-check-in.drawio)

### Check-out

![Check-out](diagramas/flujo-check-out.svg)

[PDF](diagramas/flujo-check-out.pdf) · [Archivo editable](diagramas-editables/flujo-check-out.drawio)

### Reservas

![Reservas](diagramas/flujo-reserva.svg)

[PDF](diagramas/flujo-reserva.pdf) · [Archivo editable](diagramas-editables/flujo-reserva.drawio)

## Diagrama de clases

![Clases](diagramas/diagrama-de-clases.svg)

[PDF](diagramas/diagrama-de-clases.pdf) · [Archivo editable](diagramas-editables/diagrama-de-clases.drawio)

## Modelo de datos

![Modelo de datos](diagramas/modelo-de-datos.svg)

[PDF](diagramas/modelo-de-datos.pdf) · [Archivo editable](diagramas-editables/modelo-de-datos.drawio)

## Mockups y wireframes

[Ver pantallas navegables](https://yutre3.github.io/hotel-duerme-bien/mockups/) · [Código](mockups/index.html)

Las pantallas corresponden a acceso, disponibilidad, habitaciones, huéspedes, reservas, check-in, check-out, informes y usuarios. «Ver wireframe» alterna la estructura en escala de grises.

## Prototipo funcional

[Abrir prototipo](https://yutre3.github.io/hotel-duerme-bien/prototipo/) · [HTML](prototipo/index.html) · [JavaScript](prototipo/app.js) · [Estilos](prototipo/styles.css)

Permite registrar datos ficticios de habitaciones, huéspedes, reservas y usuarios, realizar check-in y check-out y consultar informes. Conserva los registros de prueba en este navegador y valida fechas y capacidad. La tarifa de prueba se ingresa manualmente. El cálculo demostrativo usa tarifa × noches por pasajero, en pesos chilenos.

No implementa autenticación real ni sustituye una base de datos del hotel. Los permisos, los datos obligatorios de huéspedes y la regla real de cobro requieren validación.

## Planificación

[Ver Kanban](planificacion/kanban.md) · [Datos del tablero](planificacion/kanban.json)

## Materiales originales

Los 11 archivos recibidos se conservan sin modificación en [fuentes](fuentes/): definición del tema 6, casos de uso, ejemplos UML, procesos, clases, normalización, mockups y Git/GitHub/VS Code. El informe indica cómo se utilizó cada fuente.

Referencia de organización y base del prototipo: [Yutre3/diego](https://github.com/Yutre3/diego). Los nuevos diagramas, el informe y la maqueta están en este repositorio. Los archivos `.drawio` permiten editar las figuras en diagrams.net, siguiendo el formato de la referencia. No se declara que los archivos se hayan guardado en Cacoo.

No se recibieron rúbrica, plantilla IEEE 830 original, videos ni archivos PPT/PPTX. Las decisiones no especificadas en el caso se identifican como preliminares.

## Código de generación

[Generador del informe y diagramas](scripts/generar_entregables.py) · [Dependencias](scripts/requirements.txt)

Sin conexión: descargar el repositorio y abrir `index.html`, `mockups/index.html` o `prototipo/index.html`.

## Vista del prototipo publicado

![Prototipo público de Duerme Bien](evidencia/prototipo-publicado.jpg)
