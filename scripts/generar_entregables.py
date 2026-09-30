from pathlib import Path
import shutil, json, html, zipfile, hashlib
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

ROOT=Path(__file__).resolve().parents[1]
PORTADA_GUARDADA={p:p.read_text() for p in [ROOT/'README.md',ROOT/'index.html'] if p.exists()}
for d in ['fuentes','informe','diagramas','mockups','planificacion']:(ROOT/d).mkdir(parents=True,exist_ok=True)
for p in (ROOT/'fuentes').iterdir():
    if p.is_file():pass  # Los originales ya se conservan en fuentes.

req=[
('RF01','Registrar y editar habitaciones','Número, capacidad y orientación.','CU02','Habitacion','Habitaciones'),
('RF02','Registrar huéspedes','Identificar al huésped y asociarlo a una habitación mediante su estadía.','CU03, CU04','Huesped, EstadiaHuesped','Huéspedes, Check-in'),
('RF03','Consultar disponibilidad y ocupación','Consultar habitaciones para un intervalo y cantidad de pasajeros.','CU05','Habitacion, Reserva, Estadia','Disponibilidad'),
('RF04','Registrar check-in','Asignar una habitación disponible y registrar los pasajeros de la estadía.','CU04','Estadia, EstadiaHuesped','Check-in'),
('RF05','Registrar check-out','Finalizar la estadía y liberar la habitación. Incluir el cálculo de cuenta.','CU06, CU07','Estadia, EstadiaHuesped','Check-out'),
('RF06','Calcular costos por pasajero','Calcular y mostrar costos de cada pasajero. La fórmula y tarifa requieren confirmación.','CU07','EstadiaHuesped','Check-out'),
('RF07','Gestionar usuarios y perfiles','Distinguir administrador y encargado del hotel. La matriz detallada de permisos es preliminar.','CU01, CU08','Usuario, Rol','Usuarios, Acceso'),
('RF08','Registrar y gestionar reservas','Guardar fechas, habitación solicitada y cantidad de pasajeros.','CU09','Reserva','Reservas'),
('RF09','Generar informes','Mostrar ocupación y reservas con filtros de fecha.','CU10','Reserva, Estadia, Habitacion','Informes'),
]
rules=[
('RN01','La cantidad de pasajeros asignados no debe superar la capacidad de la habitación.','Derivada de capacidad y asignación del tema 6.'),
('RN02','Una habitación no se asigna a estadías simultáneas que superen su disponibilidad.','Derivada del control de ocupación. Propuesta: reservar la habitación completa.'),
('RN03','El check-out termina la estadía y libera la habitación.','Proceso explícito del tema 6.'),
('RN04','El check-out incluye calcular la cuenta.','UML_CASOS_DE_USO_2(2).jpg.'),
('RN05','La disponibilidad futura considera reservas vigentes y estadías registradas.','Derivada de reservas y disponibilidad.'),
('RN06','Los perfiles del sistema son administrador y encargado de hotel.','Funciones explícitas del tema 6.'),
]
uc=[
('CU01','Iniciar sesión','Administrador y encargado','Usuario registrado.','Ingresar credenciales. Validar identidad. Abrir la sesión con el perfil correspondiente.','Credenciales incorrectas: mostrar error y permitir corregir.','Sesión activa.','RF07'),
('CU02','Gestionar habitaciones','Administrador (propuesta)','Sesión activa con permiso.','Ingresar número, capacidad y orientación. Validar. Guardar habitación o modificación.','Número repetido o capacidad inválida: corregir sin guardar.','Habitación registrada o actualizada.','RF01'),
('CU03','Registrar huésped','Encargado (propuesta)','Sesión activa.','Ingresar identificación y nombre. Revisar si existe. Guardar registro nuevo o seleccionar el existente.','Datos incompletos: corregir. Registro existente: reutilizar.','Huésped identificado.','RF02'),
('CU04','Registrar check-in','Encargado (propuesta)','Sesión activa. Habitación disponible.','Seleccionar fechas y pasajeros. Consultar disponibilidad (CU05). Seleccionar habitación. Asociar huéspedes. Guardar estadía activa.','No hay disponibilidad o se supera capacidad: corregir selección sin asignar.','Estadía activa y habitación ocupada.','RF02, RF03, RF04'),
('CU05','Consultar disponibilidad','Encargado (propuesta)','Sesión activa.','Ingresar intervalo y cantidad de pasajeros. Revisar capacidad, reservas y estadías. Mostrar habitaciones compatibles.','Fechas inválidas: solicitar corrección. Sin resultados: mostrar mensaje.','Listado de disponibilidad.','RF03'),
('CU06','Registrar check-out','Encargado (propuesta)','Estadía activa.','Seleccionar estadía. Revisar pasajeros. Ejecutar Calcular cuenta (CU07). Confirmar salida. Finalizar estadía y liberar habitación.','Tarifa o regla de cobro sin definir: impedir confirmar cuenta y solicitar definición.','Estadía finalizada y habitación liberada.','RF05, RF06'),
('CU07','Calcular cuenta','Incluido en CU06','Estadía identificada y regla de cobro definida.','Obtener pasajeros y datos de cobro. Aplicar regla aprobada por el hotel. Mostrar costo por pasajero y total.','Regla o tarifa faltante: informar que no se puede calcular.','Costos calculados y visibles.','RF06'),
('CU08','Gestionar usuarios','Administrador (propuesta)','Sesión con permiso administrativo.','Registrar usuario. Asignar perfil administrador o encargado. Guardar cambios.','Usuario duplicado o perfil inválido: corregir.','Usuario con perfil asignado.','RF07'),
('CU09','Gestionar reservas','Encargado (propuesta)','Sesión activa.','Ingresar huésped titular, fechas y pasajeros. Consultar disponibilidad (CU05). Seleccionar habitación. Guardar reserva.','Fechas inválidas, capacidad excedida o conflicto: corregir antes de guardar.','Reserva registrada.','RF08, RF03'),
('CU10','Generar informes','Administrador (propuesta)','Sesión con permiso.','Seleccionar ocupación o reservas. Indicar fechas. Consultar datos y presentar resultados.','Sin registros: mostrar informe vacío con mensaje.','Informe consultable.','RF09'),
]

md=['# Sistema de Pasajeros de Hotel - Duerme Bien','Luis Huenchul','## 1. Introducción',
'### 1.1 Propósito\nDefinir los requerimientos y el modelado del sistema que reemplazará las planillas Excel del hotel Duerme Bien. El documento sigue las secciones IEEE 830 adaptadas que enumera «Definición de proyectos(2).docx». La plantilla original y la rúbrica no están entre los adjuntos.',
'### 1.2 Alcance\nRegistrar habitaciones y huéspedes, asignar habitaciones, controlar ocupación y disponibilidad, calcular costos por pasajero, gestionar perfiles y presentar informes de ocupación y reservas. Se modelan check-in, check-out y reservas. No se incorporan servicios ajenos al tema 6.',
'### 1.3 Público objetivo\nAdministrador y encargados del hotel, docente y equipo de desarrollo.',
'### 1.4 Definiciones\nHuésped: pasajero alojado. Habitación: unidad con capacidad y orientación. Reserva: solicitud de alojamiento para fechas futuras. Estadía: registro del alojamiento efectivo. Check-in: inicio de la estadía. Check-out: cierre de la estadía. Mockup: diseño visual. Wireframe: estructura de interfaz. Prototipo: simulación navegable.',
'## 2. Descripción general',
'### 2.1 Perspectiva del producto\nEl sistema centraliza la información hoy registrada en Excel. El material no fija lenguaje, motor de base de datos, infraestructura ni tipo de instalación. Este trabajo presenta el análisis y diseño preliminar.',
'### 2.2 Funciones generales\nLas funciones se detallan en RF01 a RF09 y se conectan con los casos de uso, clases, modelo de datos y pantallas.',
'### 2.3 Clases de usuario\nAdministrador y encargado de hotel, expresamente indicados en el tema 6. Para el diseño se propone que el administrador gestione usuarios y habitaciones e informes, y el encargado atienda huéspedes, estadías y reservas. Esta distribución debe validarse en la toma de requerimientos. El huésped no se representa como usuario directo: el caso no solicita autoservicio.',
'### 2.4 Entorno operativo\nLa instalación final no está definida. La maqueta local funciona en un navegador y representa únicamente la interfaz. No implementa autenticación real ni una base de datos productiva.',
'### 2.5 Restricciones\nConservar los perfiles del caso, la capacidad y orientación de habitaciones, los costos por pasajero y los informes. Mantener trazabilidad. Aplicar los símbolos y relaciones UML de los archivos de referencia. Los importes de la maqueta se expresan en pesos chilenos si se ingresa una tarifa de prueba.',
'### 2.6 Supuestos y dependencias\nLa separación entre reserva y estadía y la asignación de una habitación completa son decisiones preliminares de modelado. El caso no aclara si permite habitaciones compartidas, varias habitaciones por reserva ni cambios de habitación durante una estadía. El diseño debe revisarse si esas condiciones cambian.',
'## 3. Requisitos específicos preliminares','### 3.1 Requisitos funcionales',
'| ID | Requisito | Comportamiento |\n|---|---|---|']
md += [f'| {i} | {n} | {d} |' for i,n,d,*_ in req]
md += ['### 3.2 Requisitos no funcionales propuestos',
'El documento de definición solicita requisitos no funcionales, pero no establece valores. Los siguientes criterios son propuestas verificables, pendientes de validación con el cliente simulado.',
'| ID | Requisito propuesto | Criterio de aceptación |\n|---|---|---|',
'| RNF01 | Acceso según perfil | Un usuario sin permiso no puede ejecutar operaciones restringidas. |',
'| RNF02 | Integridad | Rechazar capacidades inválidas, fechas incoherentes y asignaciones que excedan capacidad. |',
'| RNF03 | Usabilidad | Campos etiquetados, navegación consistente y mensajes de corrección en los formularios. |',
'| RNF04 | Conservación de datos | Los registros guardados siguen disponibles al cerrar y abrir el sistema final. |',
'| RNF05 | Consistencia de disponibilidad | Dos operaciones concurrentes no confirman la misma habitación para intervalos incompatibles. |',
'## 4. Reglas de negocio conocidas y derivadas','| ID | Regla | Origen y estado |\n|---|---|---|']
md += [f'| {i} | {n} | {s} |' for i,n,s in rules]
md += ['### 4.1 Cobro pendiente de definir\nEl caso exige cálculo automático por pasajero, pero no indica tarifa ni unidad de cobro. No se fija una fórmula como regla del hotel. Para probar la pantalla se ofrece una simulación opcional: costo por pasajero = tarifa de prueba × noches de prueba. Esta fórmula no constituye un requerimiento confirmado. El modelo almacena el costo calculado de cada pasajero como resultado del cobro.',
'## 5. Toma de requerimientos\nNo se ha recibido una entrevista previa ni retroalimentación de la Evaluación 1. El análisis se basa en el caso escrito. Las siguientes preguntas forman el guion de entrevista simulada y quedan pendientes de respuesta.',
'| ID | Pregunta | Requisito afectado |\n|---|---|---|',
'| P01 | ¿Qué datos identifican de forma única a cada huésped? | RF02 |',
'| P02 | ¿La tarifa se cobra por noche, día u otra unidad? ¿Cómo se calcula por pasajero? | RF06 |',
'| P03 | ¿Puede una habitación compartirse entre estadías distintas? | RF03, RF04 |',
'| P04 | ¿Una reserva puede incluir varias habitaciones? | RF08 |',
'| P05 | ¿Se permiten cambios de habitación durante la estadía? | RF04 |',
'| P06 | ¿Qué permisos exactos corresponden a cada perfil? | RF07 |',
'| P07 | ¿Qué estados y condiciones permiten modificar o cancelar reservas? | RF08 |',
'| P08 | ¿Qué filtros y campos deben aparecer en los informes? | RF09 |',
'| P09 | ¿Cuál es el entorno de instalación y cómo se conservarán los datos? | RNF04 |',
'| P10 | ¿Qué plantilla y rúbrica se utilizarán para la entrega? | Informe |',
'## 6. Factibilidad inicial',
'### 6.1 Técnica\nLas funciones se pueden representar mediante formularios, reglas de validación y una base de datos relacional. El modelo distingue habitaciones, huéspedes, reservas y estadías para conservar el historial. La selección tecnológica requiere conocer infraestructura y entorno. La viabilidad final depende de resolver permisos, cobro y concurrencia.',
'### 6.2 De negocio\nEl sistema responde al objetivo de reemplazar planillas y controlar ocupación. La centralización puede reducir registros duplicados y asignaciones incompatibles. No se cuantifican ahorros, costos ni retorno porque no hay datos económicos en el caso.',
'## 7. Modelado UML y de procesos',
'### 7.1 Casos de uso\nLos actores corresponden a roles. Las asociaciones con casos de uso son líneas sin flecha. La relación <<include>> apunta al caso incluido. CU06 incluye CU07, siguiendo la imagen del hotel. CU04 y CU09 incluyen CU05 porque consultar disponibilidad es obligatorio en el diseño propuesto. No se añade <<extend>> artificialmente: el caso no especifica una función opcional que lo justifique.',
'El archivo diagramas/casos-de-uso.svg contiene los actores fuera del límite del sistema. La autenticación se trata como precondición de las operaciones para evitar saturar el diagrama con inclusiones.',
'### 7.2 Especificaciones de casos de uso']
for i,n,a,pre,flow,alt,post,r in uc:
    md += [f'#### {i} - {n}',f'Actor: {a}.\n\nPrecondición: {pre}\n\nFlujo principal: {flow}\n\nAlternativa: {alt}\n\nPostcondición: {post}\n\nTrazabilidad: {r}.']
md += ['### 7.3 Flujos\nLos tres procesos se documentan por separado: check-in, check-out y reserva. Se usan inicio/fin, entrada de datos, decisiones y acciones, tomando como referencia diagrama_de_procesos(2).jpg. Los errores de entrada vuelven a la captura. Los conflictos de disponibilidad permiten corregir o terminar sin guardar.',
'### 7.4 Clases\nCada clase muestra nombre, atributos y operaciones. Los atributos privados llevan «-» y los métodos públicos «+». Administrador y Encargado especializan Usuario mediante generalización, sin cardinalidad en la herencia. Estadia se asocia con Habitacion y compone sus registros EstadiaHuesped. Cada registro vincula un Huesped y conserva su costo calculado. La relación es de composición con Estadia, no con Huesped, porque un huésped existe independientemente de una estadía.',
'## 8. Modelo de datos y normalización',
'### 8.1 Entidades\nROL: id_rol (PK), nombre (único). USUARIO: id_usuario (PK), id_rol (FK), nombre_usuario (único), hash_clave. HABITACION: id_habitacion (PK), numero (único), capacidad, orientacion. HUESPED: id_huesped (PK), identificacion (único, pendiente de confirmar tipo), nombres, apellidos. RESERVA: id_reserva (PK), id_huesped_titular (FK), id_habitacion (FK), fecha_entrada, fecha_salida, cantidad_pasajeros, estado. ESTADIA: id_estadia (PK), id_habitacion (FK), id_reserva (FK opcional y única), fecha_entrada, fecha_salida_prevista, fecha_salida_real (opcional), estado. ESTADIA_HUESPED: id_estadia (PK/FK), id_huesped (PK/FK), costo_calculado_clp (opcional hasta calcular).',
'### 8.2 Cardinalidades\nUn rol agrupa cero o muchos usuarios y cada usuario tiene un rol. Una habitación tiene cero o muchas reservas y estadías a lo largo del tiempo. Cada reserva y estadía tiene una habitación en este diseño preliminar. Un huésped puede ser titular de varias reservas. Una reserva puede originar cero o una estadía y una estadía puede no provenir de reserva. Una estadía activa tiene uno o más pasajeros y un huésped puede tener muchas estadías mediante ESTADIA_HUESPED. Una clave foránea por sí sola no evita superposición de fechas: esa regla requiere validación transaccional en el sistema final.',
'### 8.3 Primera forma normal\nCada campo representa un valor. Los huéspedes no se almacenan como una lista dentro de una habitación o estadía. Nombres y apellidos se separan según el enfoque del material de normalización.',
'### 8.4 Segunda forma normal\nEn ESTADIA_HUESPED el costo calculado depende de la participación de un huésped en una estadía, es decir, de la clave compuesta completa. Los datos personales dependen de HUESPED y las fechas de ESTADIA.',
'### 8.5 Tercera forma normal\nEl nombre del rol permanece en ROL y se referencia por su clave. La capacidad y orientación permanecen en HABITACION. Los datos del huésped no se copian en las reservas o estadías. El total de cuenta y la disponibilidad se derivan para evitar duplicación. El costo por participación es un resultado histórico, no una tarifa general duplicada.',
'## 9. Wireframes, mockups y prototipo',
'La estructura de pantallas mantiene acceso, disponibilidad, habitaciones, huéspedes, reservas, check-in, check-out, informes y usuarios. Las vistas siguen la distinción del documento MOCKUP_COMPLETO: wireframe en escala de grises, mockup con estilo y prototipo navegable.',
'mockups/index.html permite navegar entre pantallas y alternar la vista de wireframe. Los datos de ejemplo son ficticios y están identificados. El cálculo de cuenta usa exclusivamente una tarifa de prueba ingresada por el usuario. La maqueta no guarda información real ni representa un sistema final.',
'### 9.1 Plataformas del material\nMOCKUP_COMPLETO(2).pdf, página 16, menciona Cacoo para diagramas y wireframes. Las páginas 25-26 mencionan Justinmind, Axure, Balsamiq y MockFlow, entre otras. La página 25 también permite realizar un prototipo con HTML/CSS. El material no obliga a una sola plataforma. No se presenta una creación local como si se hubiera guardado en Cacoo. El editor de Cacoo requiere acceso a una cuenta para completar esa parte online.',
'## 10. Planificación inicial\nEl tablero Kanban incluye Por hacer, En curso, En revisión y Terminado. Los artefactos preparados quedan En revisión, porque faltan la validación del caso y la rúbrica. Las preguntas pendientes y el guardado en las plataformas quedan Por hacer. No se inventan integrantes, plazos ni aprobaciones.',
'## 11. Trazabilidad','| Requisito | Caso de uso | Clases o entidades | Pantalla |\n|---|---|---|---|']
md += [f'| {i} | {c} | {e} | {s} |' for i,n,d,c,e,s in req]
md += ['## 12. Referencias',
'1. Definición de proyectos(2).docx: tema 6 y esquema de entregables UA1, Evaluaciones 1 y 2.',
'2. UML_CASOS_DE_USO_2(2).jpg: ejemplo hotel, check-out incluye calcular cuenta.',
'3. UML_CASOS_DE_USO(2).jpg: ejemplo de actores, límite y relaciones de inclusión/extensión.',
'4. CASOS_DE_USO_como_iniciar(2).pdf: actores, casos de uso, flechas y límites.',
'5. CASOS_DE_USO_extend_y_include(2).pdf: inclusión obligatoria, extensión condicional y uso moderado.',
'6. diagrama_de_procesos(2).jpg: captura, validación y retorno por error.',
'7. Diagramas de Clase(2).pdf y GUIA_diagramas_de_clase(2).pdf: atributos, métodos, visibilidad y relaciones. El ejercicio de empleados se usa como referencia técnica, sin incorporar sus funcionalidades al hotel.',
'8. MODELO_E_R_NORMALIZACION(1).pdf: 1FN, 2FN y 3FN.',
'9. MOCKUP_COMPLETO(2).pdf: wireframes, mockups, prototipos y herramientas.',
'10. Github_Git_VSCode(1).docx: repositorio, control de versiones y colaboración.',
'### Enlaces contenidos en las fuentes\nCacoo: https://cacoo.com/\nMockFlow: http://www.mockflow.com/\nJustinmind: http://www.justinmind.com/\nAxure: http://www.axure.com/\nBalsamiq: http://balsamiq.com/products/mockups/\nGitHub: https://github.com\nGit: https://git-scm.com/downloads',
'### Material no recibido\nNo hay archivos PPT/PPTX, videos ni enlaces a videos entre los 11 adjuntos. Los PDFs sirven como material de clase. No se atribuyen al profesor criterios de una rúbrica no proporcionada ni resultados de una entrevista no realizada.']
(ROOT/'informe/requerimientos-y-modelado.md').write_text('\n\n'.join(md))

# Diagramas exactos y editables como SVG. Los símbolos siguen las fuentes de clase.
class Diagram:
    def __init__(self,name,w,h):
        self.name=name;self.w=w;self.h=h;self.elements=[]
        self.c=canvas.Canvas(str(ROOT/'diagramas'/f'{name}.pdf'),pagesize=(w,h))
        self.c.setTitle(name)
    def text(self,x,y,t,size=16,anchor='middle',bold=False):
        self.elements.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}">{html.escape(t)}</text>')
        self.c.setFont('Helvetica-Bold' if bold else 'Helvetica',size)
        fn=self.c.drawCentredString if anchor=='middle' else self.c.drawString
        fn(x,self.h-y,t)
    def line(self,x1,y1,x2,y2,label='',dashed=False,arrow=False):
        self.elements.append(f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="#263545" stroke-width="1.6" {"stroke-dasharray=\"6 5\"" if dashed else ""} {"marker-end=\"url(#arrow)\"" if arrow else ""}/>' )
        self.c.setStrokeColor(colors.HexColor('#263545'));self.c.setLineWidth(1.6);self.c.setDash(6,5) if dashed else self.c.setDash()
        self.c.line(x1,self.h-y1,x2,self.h-y2);self.c.setDash()
        if arrow:
            import math
            a=math.atan2(y2-y1,x2-x1)
            for off in [-.5,.5]:
                ex=x2-11*math.cos(a+off);ey=y2-11*math.sin(a+off)
                self.c.line(x2,self.h-y2,ex,self.h-ey)
        if label:self.text((x1+x2)/2,(y1+y2)/2-9,label,13)
    def box(self,x,y,w,h,lines,shape='rect',fill='#ffffff'):
        st=f'fill="{fill}" stroke="#263545" stroke-width="1.6"'
        self.c.setFillColor(colors.HexColor(fill));self.c.setStrokeColor(colors.HexColor('#263545'))
        if shape=='ellipse':
            self.elements.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" {st}/>');self.c.ellipse(x,self.h-y-h,x+w,self.h-y,fill=1)
        elif shape=='diamond':
            pts=[(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)]
            self.elements.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in pts)}" {st}/>')
            p=self.c.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1])
            for a,b in pts[1:]:p.lineTo(a,self.h-b)
            p.close();self.c.drawPath(p,fill=1)
        elif shape=='input':
            pts=[(x+20,y),(x+w,y),(x+w-20,y+h),(x,y+h)]
            self.elements.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in pts)}" {st}/>')
            p=self.c.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1])
            for a,b in pts[1:]:p.lineTo(a,self.h-b)
            p.close();self.c.drawPath(p,fill=1)
        else:
            self.elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {st}/>');self.c.rect(x,self.h-y-h,w,h,fill=1)
        self.c.setFillColor(colors.HexColor('#182b3b'))
        step=22;start=y+h/2-(len(lines)-1)*step/2+6
        for j,t in enumerate(lines):self.text(x+w/2,start+j*step,t,15)
    def actor(self,x,y,label):
        self.elements.append(f'<circle cx="{x}" cy="{y}" r="13" fill="white" stroke="#263545"/><path d="M{x},{y+13} V{y+53} M{x-23},{y+30} H{x+23} M{x},{y+53} L{x-23},{y+82} M{x},{y+53} L{x+23},{y+82}" stroke="#263545" fill="none"/>')
        self.c.circle(x,self.h-y,13);self.line(x,y+13,x,y+53);self.line(x-23,y+30,x+23,y+30);self.line(x,y+53,x-23,y+82);self.line(x,y+53,x+23,y+82);self.text(x,y+109,label,16)
    def save(self):
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1,1 L9,5 L1,9" fill="none" stroke="#263545"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" fill="#182b3b">'+''.join(self.elements)+'</g></svg>'
        (ROOT/'diagramas'/f'{self.name}.svg').write_text(svg);self.c.showPage();self.c.save()

d=Diagram('casos-de-uso',1400,1000)
d.box(270,60,1080,870,[]);d.text(810,93,'Sistema de Pasajeros de Hotel - Duerme Bien',23,bold=True)
d.actor(115,265,'Encargado');d.actor(115,730,'Administrador')
positions={'CU01':(740,150),'CU02':(370,670),'CU03':(370,150),'CU04':(370,280),'CU05':(1000,375),'CU06':(370,505),'CU07':(1000,505),'CU08':(740,800),'CU09':(370,395),'CU10':(740,670)}
names={i:n for i,n,*_ in uc}
for i,(x,y) in positions.items():d.box(x,y,265,65,[i,names[i]],'ellipse')
for i in ['CU01','CU03','CU04','CU05','CU06','CU09']:
 x,y=positions[i];d.line(140,302,x,y+32)
for i in ['CU01','CU02','CU08','CU10']:
 x,y=positions[i];d.line(140,765,x,y+32)
for fr,to in [('CU04','CU05'),('CU09','CU05'),('CU06','CU07')]:
 x,y=positions[fr];xx,yy=positions[to];d.line(x+265,y+32,xx,yy+32,'<<include>>',True,True)
d.text(720,969,'Asignación detallada de permisos preliminar, pendiente de validar.',16);d.save()

for name,title,steps in [
 ('flujo-check-in','Check-in',[('Inicio','ellipse'),('Capturar fechas y pasajeros','input'),('¿Datos válidos?','diamond'),('Consultar disponibilidad','rect'),('¿Habitación disponible?','diamond'),('Asignar habitación y huéspedes','rect'),('Guardar estadía activa','rect'),('Fin','ellipse')]),
 ('flujo-reserva','Registro de reserva',[('Inicio','ellipse'),('Capturar titular, fechas y pasajeros','input'),('¿Datos válidos?','diamond'),('Consultar disponibilidad','rect'),('¿Habitación disponible?','diamond'),('Seleccionar habitación','rect'),('Guardar reserva','rect'),('Fin','ellipse')]),
 ('flujo-check-out','Check-out',[('Inicio','ellipse'),('Seleccionar estadía y salida','input'),('¿Estadía activa?','diamond'),('Consultar regla de cobro','rect'),('¿Regla de cobro definida?','diamond'),('Calcular cuenta por pasajero','rect'),('Confirmar salida y liberar habitación','rect'),('Fin','ellipse')])]:
 d=Diagram(name,980,1260);d.text(490,45,title,26,bold=True)
 for i,(t,shape) in enumerate(steps):
  y=80+i*140;d.box(260,y,460,82,[t],shape)
  if i<7:d.line(490,y+82,490,y+140,'Sí' if shape=='diamond' else '',arrow=True)
 # Error de la primera decisión vuelve a captura.
 d.line(260,401,100,401,'No');d.line(100,401,100,261);d.line(100,261,260,261,arrow=True)
 # Falta de disponibilidad o cobro vuelve a revisión con salida explícita.
 d.line(720,681,865,681,'No');d.box(735,765,235,92,['Fin sin guardar'],'ellipse')
 d.line(865,681,865,765,arrow=True)
 d.text(490,1230,'Referencia: captura y validación del diagrama de procesos adjunto.',15);d.save()

entities=[
 ('ROL',['id_rol PK','nombre UNIQUE']),('USUARIO',['id_usuario PK','id_rol FK','nombre_usuario UNIQUE','hash_clave']),
 ('HABITACION',['id_habitacion PK','numero UNIQUE','capacidad','orientacion']),('HUESPED',['id_huesped PK','identificacion UNIQUE','nombres','apellidos']),
 ('RESERVA',['id_reserva PK','id_huesped_titular FK','id_habitacion FK','fecha_entrada','fecha_salida','cantidad_pasajeros','estado']),
 ('ESTADIA',['id_estadia PK','id_habitacion FK','id_reserva FK UNIQUE, opcional','fecha_entrada','fecha_salida_prevista','fecha_salida_real, opcional','estado']),
 ('ESTADIA_HUESPED',['id_estadia PK/FK','id_huesped PK/FK','costo_calculado_clp, opcional'])]
d=Diagram('modelo-de-datos',1400,1110);d.text(700,42,'Modelo relacional preliminar - 3FN',25,bold=True)
ep={'ROL':(45,90),'USUARIO':(420,90),'HABITACION':(970,90),'HUESPED':(45,420),'RESERVA':(420,390),'ESTADIA':(970,390),'ESTADIA_HUESPED':(420,820)}
for n,attrs in entities:
 x,y=ep[n];h=55+len(attrs)*27;d.box(x,y,350,h,[]);d.text(x+175,y+28,n,18,bold=True);d.line(x,y+43,x+350,y+43)
 for i,a in enumerate(attrs):d.text(x+12,y+69+i*27,a,14,'start')
for a,b,label,coords in [
 ('ROL','USUARIO','1 : 0..*',(395,130,420,130)),
 ('HABITACION','RESERVA','1 : 0..*',(970,220,770,445)),
 ('HABITACION','ESTADIA','1 : 0..*',(1145,253,1145,390)),
 ('HUESPED','RESERVA','1 : 0..*',(395,470,420,470)),
 ('RESERVA','ESTADIA','0..1 : 0..1',(770,610,970,610)),
 ('HUESPED','ESTADIA_HUESPED','1 : 0..*',(220,583,420,865)),
 ('ESTADIA','ESTADIA_HUESPED','1 : 1..*',(1145,650,770,865))]:d.line(*coords,label)
d.text(700,1040,'En cada reserva y estadía: una habitación. Validar esta decisión con el hotel.',17)
d.text(700,1070,'La no superposición de fechas se valida en una transacción, no con una FK.',17);d.save()

d=Diagram('diagrama-de-clases',1480,1110);d.text(740,38,'Diagrama de clases - Duerme Bien',25,bold=True)
classes=[
 ('Usuario',45,80,['- id: int','- nombreUsuario: String','- hashClave: String'],['+ iniciarSesion()','+ cerrarSesion()']),
 ('Administrador',45,325,[],['+ gestionarUsuarios()','+ gestionarHabitaciones()','+ generarInformes()']),
 ('Encargado',45,580,[],['+ registrarHuesped()','+ registrarCheckIn()','+ registrarCheckOut()','+ gestionarReservas()']),
 ('Habitacion',1050,80,['- id: int','- numero: String','- capacidad: int','- orientacion: String'],['+ consultarDisponibilidad()','+ actualizarDatos()']),
 ('Huesped',450,80,['- id: int','- identificacion: String','- nombres: String','- apellidos: String'],['+ registrar()','+ actualizarDatos()']),
 ('Reserva',450,400,['- id: int','- fechaEntrada: Date','- fechaSalida: Date','- cantidadPasajeros: int','- estado: String'],['+ registrar()','+ modificar()']),
 ('Estadia',1050,400,['- id: int','- fechaEntrada: Date','- fechaSalidaPrevista: Date','- fechaSalidaReal: Date?','- estado: String'],['+ registrarCheckIn()','+ calcularCuenta()','+ registrarCheckOut()']),
 ('EstadiaHuesped',750,830,['- costoCalculadoCLP: Decimal?'],['+ calcularCosto(reglaCobro)'])]
for n,x,y,attrs,methods in classes:
 h=58+(len(attrs)+len(methods))*24;d.box(x,y,340,h,[]);d.text(x+170,y+28,n,19,bold=True);d.line(x,y+42,x+340,y+42)
 for i,a in enumerate(attrs):d.text(x+12,y+65+i*24,a,15,'start')
 sy=y+50+len(attrs)*24;d.line(x,sy,x+340,sy)
 for i,a in enumerate(methods):d.text(x+12,sy+24+i*24,a,15,'start')
# Generalización explícita: triángulos vacíos hacia Usuario.
for x,y in [(110,325),(315,580)]:
 d.line(x,y,x,255)
 d.elements.append(f'<polygon points="{x-9},269 {x+9},269 {x},255" fill="white" stroke="#263545"/>')
 p=d.c.beginPath();p.moveTo(x-9,d.h-269);p.lineTo(x+9,d.h-269);p.lineTo(x,d.h-255);p.close();d.c.setFillColor(colors.white);d.c.drawPath(p,fill=1);d.c.setFillColor(colors.HexColor('#182b3b'))
d.line(620,270,620,400,'1 titular / 0..* reservas')
d.line(1220,300,1220,400,'1 / 0..*')
d.line(1050,235,790,460,'1 / 0..* reservas')
d.line(790,600,1050,600,'0..1 / 0..1')
d.line(790,210,880,210);d.line(880,210,880,760);d.line(880,760,650,760);d.line(650,760,650,930);d.line(650,930,750,930,'1 / 0..*')
d.line(1220,680,1220,880);d.line(1220,880,1090,880,'1 / 1..*')
d.elements.append('<polygon points="1220,680 1212,692 1220,704 1228,692" fill="#263545"/>')
p=d.c.beginPath();p.moveTo(1220,d.h-680);p.lineTo(1212,d.h-692);p.lineTo(1220,d.h-704);p.lineTo(1228,d.h-692);p.close();d.c.setFillColor(colors.HexColor('#263545'));d.c.drawPath(p,fill=1)
d.text(740,1040,'Composición: la participación pertenece a Estadia. Huesped existe independientemente.',17)
d.text(740,1070,'Permisos y regla de cobro pendientes de validación.',17);d.save()

# Informe PDF con secciones y tablas legibles.
styles=getSampleStyleSheet();styles['BodyText'].fontSize=10;styles['BodyText'].leading=15
styles['Heading1'].fontSize=20;styles['Heading1'].leading=25;styles['Heading1'].textColor=colors.HexColor('#173b53')
styles['Heading2'].spaceBefore=14;styles['Heading2'].spaceAfter=7
import re
story=[];text=re.sub(r'(?<=\|)\n\n(?=\|)', '\n', '\n\n'.join(md))
chunks=text.split('\n\n')
def para(s,style='BodyText'):
 return Paragraph(html.escape(s).replace('\n','<br/>'),styles[style])
for ch in chunks:
 if ch.startswith('|'):
  rows=[]
  for line in ch.splitlines():
   if not line.startswith('|'):continue
   cells=[c.strip() for c in line.strip('|').split('|')]
   if all(set(c)<=set('-: ') for c in cells):continue
   rows.append([para(c) for c in cells])
  if rows:
   widths=[(A4[0]-88)/len(rows[0])]*len(rows[0]);widths[0]=66
   for i in range(1,len(widths)):widths[i]=(A4[0]-88-66)/(len(widths)-1)
   tbl=Table(rows,colWidths=widths,repeatRows=1,hAlign='LEFT')
   tbl.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eff3')),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.3,colors.HexColor('#b6c7d0')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]));story.append(tbl);story.append(Spacer(1,12))
 elif ch.startswith('# '):story.append(para(ch[2:],'Title'))
 elif ch.startswith('## '):
  lines=ch.split('\n',1);story.append(para(lines[0][3:],'Heading1'))
  if len(lines)>1:story.append(para(lines[1]))
 elif ch.startswith('### '):
  lines=ch.split('\n',1);story.append(para(lines[0][4:],'Heading2'))
  if len(lines)>1:story.append(para(lines[1]))
 elif ch.startswith('#### '):story.append(para(ch[5:],'Heading3'))
 else:story.append(para(ch));story.append(Spacer(1,7))
def footer(c,doc):
 c.setFont('Helvetica',9);c.setFillColor(colors.HexColor('#546a79'));c.drawString(44,24,'Duerme Bien - Requerimientos y modelado');c.drawRightString(A4[0]-44,24,str(doc.page))
SimpleDocTemplate(str(ROOT/'informe/requerimientos-y-modelado.pdf'),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=44,bottomMargin=44).build(story,onFirstPage=footer,onLaterPages=footer)
import fitz
report=fitz.open(ROOT/'informe/requerimientos-y-modelado.pdf')
for name in ['casos-de-uso','flujo-check-in','flujo-check-out','flujo-reserva','diagrama-de-clases','modelo-de-datos']:
 with fitz.open(ROOT/'diagramas'/f'{name}.pdf') as annex:report.insert_pdf(annex)
report.save(ROOT/'informe/informe-con-diagramas.pdf');report.close()

kanban=[('Por hacer','Validar identificación, tarifas, permisos y reglas pendientes','P01-P09'),('Por hacer','Recibir plantilla, rúbrica y retroalimentación de Evaluación 1','P10'),('Por hacer','Guardar diagramas y mockups en la plataforma acordada','Modelado'),('Terminado','Crear y publicar repositorio GitHub','Entrega'),('En revisión','Informe de requerimientos','RF01-RF09'),('En revisión','Casos de uso y flujos','CU01-CU10'),('En revisión','Clases y modelo en 3FN','RF01-RF09'),('En revisión','Wireframes y maqueta navegable','RF01-RF09')]
(ROOT/'planificacion/kanban.md').write_text('# Planificación inicial\n\nColumnas: Por hacer, En curso, En revisión y Terminado.\n\n| Estado | Tarea | Referencia |\n|---|---|---|\n'+'\n'.join(f'| {s} | {t} | {r} |' for s,t,r in kanban)+'\n\nNo se establecen fechas ni integrantes porque no se proporcionaron. En revisión no significa aprobado por el docente.\n')
(ROOT/'planificacion/kanban.json').write_text(json.dumps([dict(estado=s,tarea=t,referencia=r) for s,t,r in kanban],ensure_ascii=False,indent=2))
(ROOT/'README.md').write_text('''# Sistema de Pasajeros de Hotel - Duerme Bien

Luis Huenchul · Tema 6

## Entregables

- [Informe de requerimientos y modelado con diagramas](informe/informe-con-diagramas.pdf)
- [Versión editable del informe](informe/requerimientos-y-modelado.md)
- [Prototipo navegable y wireframes](mockups/index.html)
- [Planificación Kanban](planificacion/kanban.md)

## Diagramas

### Casos de uso
![Casos de uso](diagramas/casos-de-uso.svg)

### Check-in
![Check-in](diagramas/flujo-check-in.svg)

### Check-out
![Check-out](diagramas/flujo-check-out.svg)

### Reservas
![Reservas](diagramas/flujo-reserva.svg)

### Clases
![Clases](diagramas/diagrama-de-clases.svg)

### Modelo de datos
![Datos](diagramas/modelo-de-datos.svg)

Los diagramas están disponibles en SVG y PDF. La carpeta `fuentes` conserva los 11 archivos recibidos, sin modificación.

## Revisión pendiente

El material no contiene rúbrica, plantilla IEEE 830, entrevista previa, PPT/PPTX ni videos. El documento distingue los requisitos del tema 6 de las decisiones preliminares. Tarifas, unidad de cobro y permisos detallados requieren confirmación. El guardado en Cacoo y la publicación en GitHub deben verificarse por separado.

## Interfaz

Abrir `mockups/index.html` en el navegador. La vista «Wireframe» usa escala de grises. La maqueta contiene datos ficticios y una simulación opcional de cobro. No representa una aplicación productiva.
''')
print(ROOT)

# Conservar la portada y regenerar las versiones revisadas.
for p,contenido in PORTADA_GUARDADA.items():p.write_text(contenido)
import runpy
runpy.run_path(str(ROOT/"scripts/revisar_diagramas.py"))
runpy.run_path(str(ROOT/"scripts/generar_interfaces.py"))
