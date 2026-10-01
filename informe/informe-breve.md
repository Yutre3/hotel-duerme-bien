
# Qué hará el sistema


## 1 Introducción

Problema: el hotel Duerme Bien usa planillas Excel para sus habitaciones y pasajeros. Objetivo: guardar esa información en un solo sistema, revisar habitaciones libres y calcular el costo por persona.

Alcance: habitaciones, huéspedes, reservas, entradas, salidas, costos, usuarios e informes. Público: administrador, encargados del hotel, equipo de desarrollo y profesor.

Palabras: huésped es la persona que se aloja. Reserva guarda una habitación para después. Estadía registra su alojamiento. Check-in significa llegada. Check-out significa salida.


## 2 Descripción general

El trabajador abre el sistema en un navegador. La demostración guarda datos en ese navegador. El sistema real necesitará servidor, base de datos y contraseñas protegidas. La demostración permite elegir un usuario de ejemplo; no verifica identidades reales.


| Tarea | Encargado | Administrador |
| --- | --- | --- |
| Buscar habitación, huéspedes y reservas | Sí | Sí |
| Registrar llegada y salida | Sí | Sí |
| Gestionar habitaciones y usuarios | No | Sí |
| Ver informes de ocupación y reservas | No | Sí |

Supuestos propuestos: una habitación por reserva y estadía; el grupo entra y sale en las mismas fechas. El precio por persona y noche es una regla de prueba, pendiente de validar.

Límites: no incluye pagos por internet, restaurante ni facturación. Dependencias: equipos y red del hotel para un sistema central. Los permisos exactos, la tarifa real y la plantilla del informe se deben confirmar.


# Tareas que debe permitir


## 3 Requisitos funcionales


| ID | Tarea | Cómo debe funcionar |
| --- | --- | --- |
| RF01 | Habitaciones | Guardar número único, capacidad y orientación. Editar sin afectar alojamientos vigentes. |
| RF02 | Huéspedes | Anotar identificación, nombres y apellidos. No repetir la misma persona. |
| RF03 | Disponibilidad | Buscar habitaciones que estén libres y tengan espacio para el grupo. |
| RF04 | Llegada | Entrar con o sin reserva. Anotar a todas las personas y asignar la habitación. |
| RF05 | Salida | Revisar la cuenta, cerrar la estadía y liberar la habitación. |
| RF06 | Costos | Mostrar el costo de cada persona y el total del grupo. |
| RF07 | Usuarios | Guardar trabajadores y sus roles. Permitir solo las tareas de cada rol. |
| RF08 | Reservas | Crear, modificar y cancelar reservas. Revisar fechas y espacio antes de guardar. |
| RF09 | Informes | Mostrar ocupación y reservas por fechas, incluyendo su estado. |


## 4 Calidad y seguridad propuestas

RNF01: impedir tareas sin permiso. RNF02: rechazar datos repetidos o incorrectos. RNF03: usar nombres claros y mensajes que digan qué corregir. RNF04: conservar datos al recargar la demo; usar datos centrales en el sistema real. RNF05: impedir que dos trabajadores reserven a la vez una habitación incompatible; esto requiere un servidor y transacciones. RNF06: relacionar cada tarea con sus dibujos, datos y pantallas.


# Reglas del hotel y entrevista


## 5 Reglas propuestas


| ID | Regla |
| --- | --- |
| RN01 | No alojar más personas que las que caben en la habitación. |
| RN02 | No dar la misma habitación a dos grupos en fechas que se cruzan. |
| RN03 | Anotar a cada persona una sola vez dentro de su estadía. |
| RN04 | Una salida permite otra entrada ese mismo día. Una habitación sigue ocupada hasta registrar la salida. |
| RN05 | Una reserva se usa para entrar una sola vez. Una persona no puede tener dos estadías activas. |
| RN06 | Solo se modifica o cancela una reserva REGISTRADA. No borrar su historial. |
| RN07 | La salida debe ser posterior a la entrada. La tarifa debe estar definida antes de calcular. |
| RN08 | Guardar el precio y el costo aplicado a cada persona al cerrar la estadía. |
| RN09 | Si alguien se queda más días, revisar conflictos con reservas antes de cerrar o extender. |


## 6 Entrevista simulada

Estas respuestas son un ejemplo académico, no una entrevista real.


| Pregunta | Respuesta propuesta |
| --- | --- |
| ¿Qué datos tiene la habitación? | Número, capacidad y orientación. |
| ¿Quién usa el sistema? | Administrador y encargados del hotel. |
| ¿Cómo se cobra? | En la prueba: precio por persona y noche. Falta confirmar la regla real. |
| ¿Qué necesitan consultar? | Habitaciones ocupadas y reservas por fechas. |


# Cómo funciona y si se puede construir


## 7 Factibilidad inicial

Técnica: el prototipo demuestra formularios, datos y validaciones. Un sistema compartido necesitará servidor, base de datos y seguridad. De negocio: evita buscar la información en varias planillas. Falta confirmar equipos, tarifa y presupuesto; no se inventa un costo de instalación.


## 8 Casos de uso

El administrador también realiza las tareas del encargado. Las tareas de administración se muestran aparte dentro del mismo dibujo. Incluir disponibilidad significa revisarla antes de guardar. La salida incluye calcular la cuenta.


| Código | Tarea | Requisito |
| --- | --- | --- |
| CU01 | Iniciar sesión | RF07 |
| CU02 | Gestionar habitaciones | RF01 |
| CU03 | Registrar huéspedes | RF02 |
| CU04 | Registrar check-in | RF02, RF03, RF04 |
| CU05 | Consultar disponibilidad | RF03 |
| CU06 | Registrar check-out | RF05, RF06 |
| CU07 | Calcular cuenta por pasajero | RF06 |
| CU08 | Gestionar usuarios | RF07 |
| CU09 | Registrar reserva | RF03, RF08 |
| CU10 | Generar informes | RF09 |
| CU11 | Modificar reserva | RF03, RF08 |
| CU12 | Cancelar reserva | RF08 |


## 9 Procesos

Reserva: anotar datos → comprobar → guardar. Llegada: elegir habitación → identificar personas → comprobar → guardar estadía. Salida: elegir estadía → calcular cuenta → confirmar → cerrar. Si hay un error, las flechas vuelven a los datos para corregirlos.


# Dónde se guardan los datos


## 10 Modelo de datos y clases


| Tabla | Guarda | Se conecta con |
| --- | --- | --- |
| ROL | Tipo de trabajador | USUARIO |
| USUARIO | Acceso y rol del trabajador | ROL |
| HABITACION | Número, capacidad y orientación | RESERVA y ESTADIA |
| HUESPED | Identificación, nombres y apellidos | RESERVA y ESTADIA_HUESPED |
| RESERVA | Titular, habitación, fechas y cantidad | HUESPED, HABITACION y ESTADIA |
| ESTADIA | Habitación, fechas, estado y noches cobradas | HABITACION, RESERVA y ESTADIA_HUESPED |
| ESTADIA_HUESPED | Persona, tarifa aplicada y costo histórico | ESTADIA y HUESPED |

PK: número que identifica un registro. FK: número que lo une a otra tabla. UQ: dato que no se repite. NULL: dato que aún puede faltar. Una estadía puede no tener reserva. Cada estadía tiene una o más personas. El dibujo de clases añade las acciones que realiza cada parte.


## 11 Guardar datos sin repetirlos

1FN: un dato en cada espacio; cada pasajero tiene su fila. 2FN: nombres van en Huésped y fechas en Estadía; la pareja estadía y huésped identifica la participación. 3FN: cada tabla guarda sus propios datos; no se copia el nombre del rol en Usuario ni el nombre del titular en Reserva.

La tarifa y el costo de cada participación conservan la cuenta histórica. La ocupación y el total se calculan con los registros; no son datos independientes que se cambian por separado.


## 12 Cuenta de ejemplo

Tarifa ficticia: $10.000 CLP por persona y noche. Dos noches cuestan $20.000 CLP por persona. Para dos personas, el total es $40.000 CLP. La tarifa real se confirma con el hotel.


# Pantallas tareas y revisión


## 13 Diseño de interfaz

Sketch: primer dibujo. Wireframe: lugar de cada campo y botón. Mockup: apariencia con colores y ejemplos. Prototipo: versión que permite probar las tareas. Hay nueve pantallas: acceso, disponibilidad, habitaciones, huéspedes, reservas, llegada, salida, informes y usuarios.


## 14 Trazabilidad


| Requisito | Casos de uso | Pantallas |
| --- | --- | --- |
| RF01 | CU02 | habitaciones |
| RF02 | CU03, CU04 | huespedes, checkin |
| RF03 | CU05 | disponibilidad |
| RF04 | CU04 | checkin |
| RF05 | CU06, CU07 | checkout |
| RF06 | CU07 | checkout |
| RF07 | CU01, CU08 | acceso, usuarios |
| RF08 | CU09, CU11, CU12 | reservas |
| RF09 | CU10 | informes |


## 15 Kanban y comprobaciones

El tablero separa lo pendiente, lo que se revisa y lo terminado. El trabajo técnico terminado no significa que el profesor ya lo aprobó.

Las pruebas comprueban permisos, duplicados, capacidad, fechas, reservas que se cruzan, llegada con y sin reserva, pasajeros individuales, cuentas, salida e informes. La demostración no prueba seguridad real ni uso simultáneo desde varios equipos.


# Entrega y fuentes


## 16 Entregas y fuentes

Evaluación 1: introducción, descripción, entrevista, requisitos, reglas y factibilidad. Evaluación 2: corregir lo anterior según el profesor y entregar diagramas, pantallas y Kanban.

Fuente del alcance: Definición de proyectos, caso 6. Guías de casos de uso, clases, procesos, normalización, mockups y GitHub del profesor. Videos: Wireframes en Figma; Introducción a Figma; Cómo usar GitHub. Los enlaces se conservan en fuentes/videos-y-herramientas.md.

Falta confirmar la tarifa, los permisos definitivos y la retroalimentación. No se recibió la rúbrica ni la plantilla IEEE 830 original. Las respuestas y datos de ejemplo son simulados.
