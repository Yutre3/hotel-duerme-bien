# Sistema de Pasajeros de Hotel - Duerme Bien

Luis Huenchul

## 1. Introducción

### 1.1 Propósito
Definir los requerimientos y el modelado del sistema que reemplazará las planillas Excel del hotel Duerme Bien. El documento sigue las secciones IEEE 830 adaptadas que enumera «Definición de proyectos(2).docx». La plantilla original y la rúbrica no están entre los adjuntos.

### 1.2 Alcance
Registrar habitaciones y huéspedes, asignar habitaciones, controlar ocupación y disponibilidad, calcular costos por pasajero, gestionar perfiles y presentar informes de ocupación y reservas. Se modelan check-in, check-out y reservas. No se incorporan servicios ajenos al tema 6.

### 1.3 Público objetivo
Administrador y encargados del hotel, docente y equipo de desarrollo.

### 1.4 Definiciones
Huésped: pasajero alojado. Habitación: unidad con capacidad y orientación. Reserva: solicitud de alojamiento para fechas futuras. Estadía: registro del alojamiento efectivo. Check-in: inicio de la estadía. Check-out: cierre de la estadía. Mockup: diseño visual. Wireframe: estructura de interfaz. Prototipo: simulación navegable.

## 2. Descripción general

### 2.1 Perspectiva del producto
El sistema centraliza la información hoy registrada en Excel. El material no fija lenguaje, motor de base de datos, infraestructura ni tipo de instalación. Este trabajo presenta el análisis y diseño preliminar.

### 2.2 Funciones generales
Las funciones se detallan en RF01 a RF09 y se conectan con los casos de uso, clases, modelo de datos y pantallas.

### 2.3 Clases de usuario
Administrador y encargado de hotel, expresamente indicados en el tema 6. Para el diseño se propone que el administrador gestione usuarios y habitaciones e informes, y el encargado atienda huéspedes, estadías y reservas. Esta distribución debe validarse en la toma de requerimientos. El huésped no se representa como usuario directo: el caso no solicita autoservicio.

### 2.4 Entorno operativo
La instalación final no está definida. La maqueta local funciona en un navegador y representa únicamente la interfaz. No implementa autenticación real ni una base de datos productiva.

### 2.5 Restricciones
Conservar los perfiles del caso, la capacidad y orientación de habitaciones, los costos por pasajero y los informes. Mantener trazabilidad. Aplicar los símbolos y relaciones UML de los archivos de referencia. Los importes de la maqueta se expresan en pesos chilenos si se ingresa una tarifa de prueba.

### 2.6 Supuestos y dependencias
La separación entre reserva y estadía y la asignación de una habitación completa son decisiones preliminares de modelado. El caso no aclara si permite habitaciones compartidas, varias habitaciones por reserva ni cambios de habitación durante una estadía. El diseño debe revisarse si esas condiciones cambian.

## 3. Requisitos específicos preliminares

### 3.1 Requisitos funcionales

| ID | Requisito | Comportamiento |
|---|---|---|

| RF01 | Registrar y editar habitaciones | Número, capacidad y orientación. |

| RF02 | Registrar huéspedes | Identificar al huésped y asociarlo a una habitación mediante su estadía. |

| RF03 | Consultar disponibilidad y ocupación | Consultar habitaciones para un intervalo y cantidad de pasajeros. |

| RF04 | Registrar check-in | Asignar una habitación disponible y registrar los pasajeros de la estadía. |

| RF05 | Registrar check-out | Finalizar la estadía y liberar la habitación. Incluir el cálculo de cuenta. |

| RF06 | Calcular costos por pasajero | Calcular y mostrar costos de cada pasajero. La fórmula y tarifa requieren confirmación. |

| RF07 | Gestionar usuarios y perfiles | Distinguir administrador y encargado del hotel. La matriz detallada de permisos es preliminar. |

| RF08 | Registrar y gestionar reservas | Guardar fechas, habitación solicitada y cantidad de pasajeros. |

| RF09 | Generar informes | Mostrar ocupación y reservas con filtros de fecha. |

### 3.2 Requisitos no funcionales propuestos

El documento de definición solicita requisitos no funcionales, pero no establece valores. Los siguientes criterios son propuestas verificables, pendientes de validación con el cliente simulado.

| ID | Requisito propuesto | Criterio de aceptación |
|---|---|---|

| RNF01 | Acceso según perfil | Un usuario sin permiso no puede ejecutar operaciones restringidas. |

| RNF02 | Integridad | Rechazar capacidades inválidas, fechas incoherentes y asignaciones que excedan capacidad. |

| RNF03 | Usabilidad | Campos etiquetados, navegación consistente y mensajes de corrección en los formularios. |

| RNF04 | Conservación de datos | Los registros guardados siguen disponibles al cerrar y abrir el sistema final. |

| RNF05 | Consistencia de disponibilidad | Dos operaciones concurrentes no confirman la misma habitación para intervalos incompatibles. |

## 4. Reglas de negocio conocidas y derivadas

| ID | Regla | Origen y estado |
|---|---|---|

| RN01 | La cantidad de pasajeros asignados no debe superar la capacidad de la habitación. | Derivada de capacidad y asignación del tema 6. |

| RN02 | Una habitación no se asigna a estadías simultáneas que superen su disponibilidad. | Derivada del control de ocupación. Propuesta: reservar la habitación completa. |

| RN03 | El check-out termina la estadía y libera la habitación. | Proceso explícito del tema 6. |

| RN04 | El check-out incluye calcular la cuenta. | UML_CASOS_DE_USO_2(2).jpg. |

| RN05 | La disponibilidad futura considera reservas vigentes y estadías registradas. | Derivada de reservas y disponibilidad. |

| RN06 | Los perfiles del sistema son administrador y encargado de hotel. | Funciones explícitas del tema 6. |

### 4.1 Cobro pendiente de definir
El caso exige cálculo automático por pasajero, pero no indica tarifa ni unidad de cobro. No se fija una fórmula como regla del hotel. Para probar la pantalla se ofrece una simulación opcional: costo por pasajero = tarifa de prueba × noches de prueba. Esta fórmula no constituye un requerimiento confirmado. El modelo almacena el costo calculado de cada pasajero como resultado del cobro.

## 5. Toma de requerimientos
No se ha recibido una entrevista previa ni retroalimentación de la Evaluación 1. El análisis se basa en el caso escrito. Las siguientes preguntas forman el guion de entrevista simulada y quedan pendientes de respuesta.

| ID | Pregunta | Requisito afectado |
|---|---|---|

| P01 | ¿Qué datos identifican de forma única a cada huésped? | RF02 |

| P02 | ¿La tarifa se cobra por noche, día u otra unidad? ¿Cómo se calcula por pasajero? | RF06 |

| P03 | ¿Puede una habitación compartirse entre estadías distintas? | RF03, RF04 |

| P04 | ¿Una reserva puede incluir varias habitaciones? | RF08 |

| P05 | ¿Se permiten cambios de habitación durante la estadía? | RF04 |

| P06 | ¿Qué permisos exactos corresponden a cada perfil? | RF07 |

| P07 | ¿Qué estados y condiciones permiten modificar o cancelar reservas? | RF08 |

| P08 | ¿Qué filtros y campos deben aparecer en los informes? | RF09 |

| P09 | ¿Cuál es el entorno de instalación y cómo se conservarán los datos? | RNF04 |

| P10 | ¿Qué plantilla y rúbrica se utilizarán para la entrega? | Informe |

## 6. Factibilidad inicial

### 6.1 Técnica
Las funciones se pueden representar mediante formularios, reglas de validación y una base de datos relacional. El modelo distingue habitaciones, huéspedes, reservas y estadías para conservar el historial. La selección tecnológica requiere conocer infraestructura y entorno. La viabilidad final depende de resolver permisos, cobro y concurrencia.

### 6.2 De negocio
El sistema responde al objetivo de reemplazar planillas y controlar ocupación. La centralización puede reducir registros duplicados y asignaciones incompatibles. No se cuantifican ahorros, costos ni retorno porque no hay datos económicos en el caso.

## 7. Modelado UML y de procesos

### 7.1 Casos de uso
Los actores corresponden a roles. Las asociaciones con casos de uso son líneas sin flecha. La relación <<include>> apunta al caso incluido. CU06 incluye CU07, siguiendo la imagen del hotel. CU04 y CU09 incluyen CU05 porque consultar disponibilidad es obligatorio en el diseño propuesto. No se añade <<extend>> artificialmente: el caso no especifica una función opcional que lo justifique.

El archivo diagramas/casos-de-uso.svg contiene los actores fuera del límite del sistema. La autenticación se trata como precondición de las operaciones para evitar saturar el diagrama con inclusiones.

### 7.2 Especificaciones de casos de uso

#### CU01 - Iniciar sesión

Actor: Administrador y encargado.

Precondición: Usuario registrado.

Flujo principal: Ingresar credenciales. Validar identidad. Abrir la sesión con el perfil correspondiente.

Alternativa: Credenciales incorrectas: mostrar error y permitir corregir.

Postcondición: Sesión activa.

Trazabilidad: RF07.

#### CU02 - Gestionar habitaciones

Actor: Administrador (propuesta).

Precondición: Sesión activa con permiso.

Flujo principal: Ingresar número, capacidad y orientación. Validar. Guardar habitación o modificación.

Alternativa: Número repetido o capacidad inválida: corregir sin guardar.

Postcondición: Habitación registrada o actualizada.

Trazabilidad: RF01.

#### CU03 - Registrar huésped

Actor: Encargado (propuesta).

Precondición: Sesión activa.

Flujo principal: Ingresar identificación y nombre. Revisar si existe. Guardar registro nuevo o seleccionar el existente.

Alternativa: Datos incompletos: corregir. Registro existente: reutilizar.

Postcondición: Huésped identificado.

Trazabilidad: RF02.

#### CU04 - Registrar check-in

Actor: Encargado (propuesta).

Precondición: Sesión activa. Habitación disponible.

Flujo principal: Seleccionar fechas y pasajeros. Consultar disponibilidad (CU05). Seleccionar habitación. Asociar huéspedes. Guardar estadía activa.

Alternativa: No hay disponibilidad o se supera capacidad: corregir selección sin asignar.

Postcondición: Estadía activa y habitación ocupada.

Trazabilidad: RF02, RF03, RF04.

#### CU05 - Consultar disponibilidad

Actor: Encargado (propuesta).

Precondición: Sesión activa.

Flujo principal: Ingresar intervalo y cantidad de pasajeros. Revisar capacidad, reservas y estadías. Mostrar habitaciones compatibles.

Alternativa: Fechas inválidas: solicitar corrección. Sin resultados: mostrar mensaje.

Postcondición: Listado de disponibilidad.

Trazabilidad: RF03.

#### CU06 - Registrar check-out

Actor: Encargado (propuesta).

Precondición: Estadía activa.

Flujo principal: Seleccionar estadía. Revisar pasajeros. Ejecutar Calcular cuenta (CU07). Confirmar salida. Finalizar estadía y liberar habitación.

Alternativa: Tarifa o regla de cobro sin definir: impedir confirmar cuenta y solicitar definición.

Postcondición: Estadía finalizada y habitación liberada.

Trazabilidad: RF05, RF06.

#### CU07 - Calcular cuenta

Actor: Incluido en CU06.

Precondición: Estadía identificada y regla de cobro definida.

Flujo principal: Obtener pasajeros y datos de cobro. Aplicar regla aprobada por el hotel. Mostrar costo por pasajero y total.

Alternativa: Regla o tarifa faltante: informar que no se puede calcular.

Postcondición: Costos calculados y visibles.

Trazabilidad: RF06.

#### CU08 - Gestionar usuarios

Actor: Administrador (propuesta).

Precondición: Sesión con permiso administrativo.

Flujo principal: Registrar usuario. Asignar perfil administrador o encargado. Guardar cambios.

Alternativa: Usuario duplicado o perfil inválido: corregir.

Postcondición: Usuario con perfil asignado.

Trazabilidad: RF07.

#### CU09 - Gestionar reservas

Actor: Encargado (propuesta).

Precondición: Sesión activa.

Flujo principal: Ingresar huésped titular, fechas y pasajeros. Consultar disponibilidad (CU05). Seleccionar habitación. Guardar reserva.

Alternativa: Fechas inválidas, capacidad excedida o conflicto: corregir antes de guardar.

Postcondición: Reserva registrada.

Trazabilidad: RF08, RF03.

#### CU10 - Generar informes

Actor: Administrador (propuesta).

Precondición: Sesión con permiso.

Flujo principal: Seleccionar ocupación o reservas. Indicar fechas. Consultar datos y presentar resultados.

Alternativa: Sin registros: mostrar informe vacío con mensaje.

Postcondición: Informe consultable.

Trazabilidad: RF09.

### 7.3 Flujos
Los tres procesos se documentan por separado: check-in, check-out y reserva. Se usan inicio/fin, entrada de datos, decisiones y acciones, tomando como referencia diagrama_de_procesos(2).jpg. Los errores de entrada vuelven a la captura. Los conflictos de disponibilidad permiten corregir o terminar sin guardar.

### 7.4 Clases
Cada clase muestra nombre, atributos y operaciones. Los atributos privados llevan «-» y los métodos públicos «+». Administrador y Encargado especializan Usuario mediante generalización, sin cardinalidad en la herencia. Estadia se asocia con Habitacion y compone sus registros EstadiaHuesped. Cada registro vincula un Huesped y conserva su costo calculado. La relación es de composición con Estadia, no con Huesped, porque un huésped existe independientemente de una estadía.

## 8. Modelo de datos y normalización

### 8.1 Entidades
ROL: id_rol (PK), nombre (único). USUARIO: id_usuario (PK), id_rol (FK), nombre_usuario (único), hash_clave. HABITACION: id_habitacion (PK), numero (único), capacidad, orientacion. HUESPED: id_huesped (PK), identificacion (único, pendiente de confirmar tipo), nombres, apellidos. RESERVA: id_reserva (PK), id_huesped_titular (FK), id_habitacion (FK), fecha_entrada, fecha_salida, cantidad_pasajeros, estado. ESTADIA: id_estadia (PK), id_habitacion (FK), id_reserva (FK opcional y única), fecha_entrada, fecha_salida_prevista, fecha_salida_real (opcional), estado. ESTADIA_HUESPED: id_estadia (PK/FK), id_huesped (PK/FK), costo_calculado_clp (opcional hasta calcular).

### 8.2 Cardinalidades
Un rol agrupa cero o muchos usuarios y cada usuario tiene un rol. Una habitación tiene cero o muchas reservas y estadías a lo largo del tiempo. Cada reserva y estadía tiene una habitación en este diseño preliminar. Un huésped puede ser titular de varias reservas. Una reserva puede originar cero o una estadía y una estadía puede no provenir de reserva. Una estadía activa tiene uno o más pasajeros y un huésped puede tener muchas estadías mediante ESTADIA_HUESPED. Una clave foránea por sí sola no evita superposición de fechas: esa regla requiere validación transaccional en el sistema final.

### 8.3 Primera forma normal
Cada campo representa un valor. Los huéspedes no se almacenan como una lista dentro de una habitación o estadía. Nombres y apellidos se separan según el enfoque del material de normalización.

### 8.4 Segunda forma normal
En ESTADIA_HUESPED el costo calculado depende de la participación de un huésped en una estadía, es decir, de la clave compuesta completa. Los datos personales dependen de HUESPED y las fechas de ESTADIA.

### 8.5 Tercera forma normal
El nombre del rol permanece en ROL y se referencia por su clave. La capacidad y orientación permanecen en HABITACION. Los datos del huésped no se copian en las reservas o estadías. El total de cuenta y la disponibilidad se derivan para evitar duplicación. El costo por participación es un resultado histórico, no una tarifa general duplicada.

## 9. Wireframes, mockups y prototipo

La estructura de pantallas mantiene acceso, disponibilidad, habitaciones, huéspedes, reservas, check-in, check-out, informes y usuarios. Las vistas siguen la distinción del documento MOCKUP_COMPLETO: wireframe en escala de grises, mockup con estilo y prototipo navegable.

mockups/index.html permite navegar entre pantallas y alternar la vista de wireframe. Los datos de ejemplo son ficticios y están identificados. El cálculo de cuenta usa exclusivamente una tarifa de prueba ingresada por el usuario. La maqueta no guarda información real ni representa un sistema final.

### 9.1 Plataformas del material
MOCKUP_COMPLETO(2).pdf, página 16, menciona Cacoo para diagramas y wireframes. Las páginas 25-26 mencionan Justinmind, Axure, Balsamiq y MockFlow, entre otras. La página 25 también permite realizar un prototipo con HTML/CSS. El material no obliga a una sola plataforma. No se presenta una creación local como si se hubiera guardado en Cacoo. El editor de Cacoo requiere acceso a una cuenta para completar esa parte online.

## 10. Planificación inicial
El tablero Kanban incluye Por hacer, En curso, En revisión y Terminado. Los artefactos preparados quedan En revisión, porque faltan la validación del caso y la rúbrica. Las preguntas pendientes y el guardado en las plataformas quedan Por hacer. No se inventan integrantes, plazos ni aprobaciones.

## 11. Trazabilidad

| Requisito | Caso de uso | Clases o entidades | Pantalla |
|---|---|---|---|

| RF01 | CU02 | Habitacion | Habitaciones |

| RF02 | CU03, CU04 | Huesped, EstadiaHuesped | Huéspedes, Check-in |

| RF03 | CU05 | Habitacion, Reserva, Estadia | Disponibilidad |

| RF04 | CU04 | Estadia, EstadiaHuesped | Check-in |

| RF05 | CU06, CU07 | Estadia, EstadiaHuesped | Check-out |

| RF06 | CU07 | EstadiaHuesped | Check-out |

| RF07 | CU01, CU08 | Usuario, Rol | Usuarios, Acceso |

| RF08 | CU09 | Reserva | Reservas |

| RF09 | CU10 | Reserva, Estadia, Habitacion | Informes |

## 12. Referencias

1. Definición de proyectos(2).docx: tema 6 y esquema de entregables UA1, Evaluaciones 1 y 2.

2. UML_CASOS_DE_USO_2(2).jpg: ejemplo hotel, check-out incluye calcular cuenta.

3. UML_CASOS_DE_USO(2).jpg: ejemplo de actores, límite y relaciones de inclusión/extensión.

4. CASOS_DE_USO_como_iniciar(2).pdf: actores, casos de uso, flechas y límites.

5. CASOS_DE_USO_extend_y_include(2).pdf: inclusión obligatoria, extensión condicional y uso moderado.

6. diagrama_de_procesos(2).jpg: captura, validación y retorno por error.

7. Diagramas de Clase(2).pdf y GUIA_diagramas_de_clase(2).pdf: atributos, métodos, visibilidad y relaciones. El ejercicio de empleados se usa como referencia técnica, sin incorporar sus funcionalidades al hotel.

8. MODELO_E_R_NORMALIZACION(1).pdf: 1FN, 2FN y 3FN.

9. MOCKUP_COMPLETO(2).pdf: wireframes, mockups, prototipos y herramientas.

10. Github_Git_VSCode(1).docx: repositorio, control de versiones y colaboración.

### Enlaces contenidos en las fuentes
Cacoo: https://cacoo.com/
MockFlow: http://www.mockflow.com/
Justinmind: http://www.justinmind.com/
Axure: http://www.axure.com/
Balsamiq: http://balsamiq.com/products/mockups/
GitHub: https://github.com
Git: https://git-scm.com/downloads

### Material no recibido
No hay archivos PPT/PPTX, videos ni enlaces a videos entre los 11 adjuntos. Los PDFs sirven como material de clase. No se atribuyen al profesor criterios de una rúbrica no proporcionada ni resultados de una entrevista no realizada.