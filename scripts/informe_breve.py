"""Informe breve con los requisitos del caso 6 y anexos visuales."""
from pathlib import Path
import json,html
import fitz
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph,Table,TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'scripts/construir_informe.py').read_text();scope={'__file__':str(ROOT/'scripts/construir_informe.py')};exec(src[:src.index('parts=[]')],scope)
req=scope['requirements'];M=json.loads((ROOT/'modelo/sistema.json').read_text())
pdfmetrics.registerFont(TTFont('Hotel','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('HotelBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('Hotel',normal='Hotel',bold='HotelBold',italic='Hotel',boldItalic='HotelBold')
c=canvas.Canvas(str(ROOT/'informe/requerimientos-y-modelado.pdf'),pagesize=(612,792));c.setTitle('Hotel Duerme Bien');c.setAuthor('Luis Huenchul')
st=ParagraphStyle('body',fontName='Hotel',fontSize=10.4,leading=15,textColor=HexColor('#183746'))
ts=ParagraphStyle('table',parent=st,fontSize=9,leading=13)
md=[];y=0;page=0
def new(title):
 global y,page
 if page:c.showPage()
 page+=1;c.setFont('Hotel',8);c.drawString(42,756,'HOTEL DUERME BIEN · PROYECTO 6 · LUIS HUENCHUL');c.drawRightString(570,26,str(page));c.setFont('HotelBold',19);c.drawString(42,718,title);y=690;md.append('\n# '+title+'\n')
def p(t):
 global y
 q=Paragraph(t,st);_,h=q.wrap(528,700);assert y-h>45,(page,t[:40],y,h);q.drawOn(c,42,y-h);y-=h+12;md.append(t.replace('<b>','').replace('</b>','')+'\n')
def heading(t):
 global y
 y-=5;c.setFont('HotelBold',12);c.drawString(42,y,t);y-=22;md.append('\n## '+t+'\n')
def tab(rows,widths):
 global y
 q=Table([[Paragraph(html.escape(str(t)).replace('\n','<br/>'),ts) for t in r] for r in rows],colWidths=widths)
 q.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),HexColor('#edf4f6')),('GRID',(0,0),(-1,-1),.4,HexColor('#c5d5da')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 _,h=q.wrap(528,700);assert y-h>45,(page,y,h);q.drawOn(c,42,y-h);y-=h+15
 lines=['| '+' | '.join(str(x).replace('\n',' ') for x in r)+' |' for r in rows]
 lines.insert(1,'| '+' | '.join('---' for _ in rows[0])+' |')
 md.append('\n'+'\n'.join(lines)+'\n')

new('Qué hará el sistema')
heading('1 Introducción')
p('<b>Problema:</b> el hotel Duerme Bien usa planillas Excel para sus habitaciones y pasajeros. <b>Objetivo:</b> guardar esa información en un solo sistema, revisar habitaciones libres y calcular el costo por persona.')
p('<b>Alcance:</b> habitaciones, huéspedes, reservas, entradas, salidas, costos, usuarios e informes. <b>Público:</b> administrador, encargados del hotel, equipo de desarrollo y profesor.')
p('<b>Palabras:</b> huésped es la persona que se aloja. Reserva guarda una habitación para después. Estadía registra su alojamiento. Check-in significa llegada. Check-out significa salida.')
heading('2 Descripción general')
p('El trabajador abre el sistema en un navegador. La demostración guarda datos en ese navegador. El sistema real necesitará servidor, base de datos y contraseñas protegidas. La demostración permite elegir un usuario de ejemplo; no verifica identidades reales.')
tab([['Tarea','Encargado','Administrador'],['Buscar habitación, huéspedes y reservas','Sí','Sí'],['Registrar llegada y salida','Sí','Sí'],['Gestionar habitaciones y usuarios','No','Sí'],['Ver informes de ocupación y reservas','No','Sí']],[310,100,118])
p('<b>Supuestos propuestos:</b> una habitación por reserva y estadía; el grupo entra y sale en las mismas fechas. El precio por persona y noche es una regla de prueba, pendiente de validar.')
p('<b>Límites:</b> no incluye pagos por internet, restaurante ni facturación. <b>Dependencias:</b> equipos y red del hotel para un sistema central. Los permisos exactos, la tarifa real y la plantilla del informe se deben confirmar.')

new('Tareas que debe permitir')
heading('3 Requisitos funcionales')
simple=[('RF01','Habitaciones','Guardar número único, capacidad y orientación. Editar sin afectar alojamientos vigentes.'),('RF02','Huéspedes','Anotar identificación, nombres y apellidos. No repetir la misma persona.'),('RF03','Disponibilidad','Buscar habitaciones que estén libres y tengan espacio para el grupo.'),('RF04','Llegada','Entrar con o sin reserva. Anotar a todas las personas y asignar la habitación.'),('RF05','Salida','Revisar la cuenta, cerrar la estadía y liberar la habitación.'),('RF06','Costos','Mostrar el costo de cada persona y el total del grupo.'),('RF07','Usuarios','Guardar trabajadores y sus roles. Permitir solo las tareas de cada rol.'),('RF08','Reservas','Crear, modificar y cancelar reservas. Revisar fechas y espacio antes de guardar.'),('RF09','Informes','Mostrar ocupación y reservas por fechas, incluyendo su estado.')]
tab([['ID','Tarea','Cómo debe funcionar']]+simple,[48,102,378])
heading('4 Calidad y seguridad propuestas')
p('<b>RNF01:</b> impedir tareas sin permiso. <b>RNF02:</b> rechazar datos repetidos o incorrectos. <b>RNF03:</b> usar nombres claros y mensajes que digan qué corregir. <b>RNF04:</b> conservar datos al recargar la demo; usar datos centrales en el sistema real. <b>RNF05:</b> impedir que dos trabajadores reserven a la vez una habitación incompatible; esto requiere un servidor y transacciones. <b>RNF06:</b> relacionar cada tarea con sus dibujos, datos y pantallas.')

new('Reglas del hotel y entrevista')
heading('5 Reglas propuestas')
rules=[('RN01','No alojar más personas que las que caben en la habitación.'),('RN02','No dar la misma habitación a dos grupos en fechas que se cruzan.'),('RN03','Anotar a cada persona una sola vez dentro de su estadía.'),('RN04','Una salida permite otra entrada ese mismo día. Una habitación sigue ocupada hasta registrar la salida.'),('RN05','Una reserva se usa para entrar una sola vez. Una persona no puede tener dos estadías activas.'),('RN06','Solo se modifica o cancela una reserva REGISTRADA. No borrar su historial.'),('RN07','La salida debe ser posterior a la entrada. La tarifa debe estar definida antes de calcular.'),('RN08','Guardar el precio y el costo aplicado a cada persona al cerrar la estadía.'),('RN09','Si alguien se queda más días, revisar conflictos con reservas antes de cerrar o extender.')]
tab([['ID','Regla']]+rules,[48,480])
heading('6 Entrevista simulada')
p('Estas respuestas son un ejemplo académico, no una entrevista real.')
tab([['Pregunta','Respuesta propuesta'],['¿Qué datos tiene la habitación?','Número, capacidad y orientación.'],['¿Quién usa el sistema?','Administrador y encargados del hotel.'],['¿Cómo se cobra?','En la prueba: precio por persona y noche. Falta confirmar la regla real.'],['¿Qué necesitan consultar?','Habitaciones ocupadas y reservas por fechas.']],[230,298])

new('Cómo funciona y si se puede construir')
heading('7 Factibilidad inicial')
p('<b>Técnica:</b> el prototipo demuestra formularios, datos y validaciones. Un sistema compartido necesitará servidor, base de datos y seguridad. <b>De negocio:</b> evita buscar la información en varias planillas. Falta confirmar equipos, tarifa y presupuesto; no se inventa un costo de instalación.')
heading('8 Casos de uso')
p('El administrador también realiza las tareas del encargado. Las tareas de administración se muestran aparte dentro del mismo dibujo. Incluir disponibilidad significa revisarla antes de guardar. La salida incluye calcular la cuenta.')
tab([['Código','Tarea','Requisito']]+[[i,n,r] for i,n,r in M['casos']],[64,290,174])
heading('9 Procesos')
p('<b>Reserva:</b> anotar datos → comprobar → guardar. <b>Llegada:</b> elegir habitación → identificar personas → comprobar → guardar estadía. <b>Salida:</b> elegir estadía → calcular cuenta → confirmar → cerrar. Si hay un error, las flechas vuelven a los datos para corregirlos.')

new('Dónde se guardan los datos')
heading('10 Modelo de datos y clases')
tab([['Tabla','Guarda','Se conecta con'],['ROL','Tipo de trabajador','USUARIO'],['USUARIO','Acceso y rol del trabajador','ROL'],['HABITACION','Número, capacidad y orientación','RESERVA y ESTADIA'],['HUESPED','Identificación, nombres y apellidos','RESERVA y ESTADIA_HUESPED'],['RESERVA','Titular, habitación, fechas y cantidad','HUESPED, HABITACION y ESTADIA'],['ESTADIA','Habitación, fechas, estado y noches cobradas','HABITACION, RESERVA y ESTADIA_HUESPED'],['ESTADIA_HUESPED','Persona, tarifa aplicada y costo histórico','ESTADIA y HUESPED']],[138,240,150])
p('<b>PK:</b> número que identifica un registro. <b>FK:</b> número que lo une a otra tabla. <b>UQ:</b> dato que no se repite. <b>NULL:</b> dato que aún puede faltar. Una estadía puede no tener reserva. Cada estadía tiene una o más personas. El dibujo de clases añade las acciones que realiza cada parte.')
heading('11 Guardar datos sin repetirlos')
p('<b>1FN:</b> un dato en cada espacio; cada pasajero tiene su fila. <b>2FN:</b> nombres van en Huésped y fechas en Estadía; la pareja estadía y huésped identifica la participación. <b>3FN:</b> cada tabla guarda sus propios datos; no se copia el nombre del rol en Usuario ni el nombre del titular en Reserva.')
p('La tarifa y el costo de cada participación conservan la cuenta histórica. La ocupación y el total se calculan con los registros; no son datos independientes que se cambian por separado.')
heading('12 Cuenta de ejemplo')
p('Tarifa ficticia: $10.000 CLP por persona y noche. Dos noches cuestan $20.000 CLP por persona. Para dos personas, el total es $40.000 CLP. La tarifa real se confirma con el hotel.')

new('Pantallas tareas y revisión')
heading('13 Diseño de interfaz')
p('<b>Sketch:</b> primer dibujo. <b>Wireframe:</b> lugar de cada campo y botón. <b>Mockup:</b> apariencia con colores y ejemplos. <b>Prototipo:</b> versión que permite probar las tareas. Hay nueve pantallas: acceso, disponibilidad, habitaciones, huéspedes, reservas, llegada, salida, informes y usuarios.')
heading('14 Trazabilidad')
tab([['Requisito','Casos de uso','Pantallas']]+[[a,d,f] for a,b,c,d,e,f in req],[75,210,243])
heading('15 Kanban y comprobaciones')
p('El tablero separa lo pendiente, lo que se revisa y lo terminado. El trabajo técnico terminado no significa que el profesor ya lo aprobó.')
p('Las pruebas comprueban permisos, duplicados, capacidad, fechas, reservas que se cruzan, llegada con y sin reserva, pasajeros individuales, cuentas, salida e informes. La demostración no prueba seguridad real ni uso simultáneo desde varios equipos.')
new('Entrega y fuentes')
heading('16 Entregas y fuentes')
p('<b>Evaluación 1:</b> introducción, descripción, entrevista, requisitos, reglas y factibilidad. <b>Evaluación 2:</b> corregir lo anterior según el profesor y entregar diagramas, pantallas y Kanban.')
p('Fuente del alcance: Definición de proyectos, caso 6. Guías de casos de uso, clases, procesos, normalización, mockups y GitHub del profesor. Videos: Wireframes en Figma; Introducción a Figma; Cómo usar GitHub. Los enlaces se conservan en fuentes/videos-y-herramientas.md.')
p('Falta confirmar la tarifa, los permisos definitivos y la retroalimentación. No se recibió la rúbrica ni la plantilla IEEE 830 original. Las respuestas y datos de ejemplo son simulados.')
c.save()
# La lectura corta y las fichas detalladas quedan juntas en la versión editable.
old=(ROOT/'informe/requerimientos-y-modelado.md').read_text()
(ROOT/'informe/informe-breve.md').write_text('\n'.join(md))
out=fitz.open(ROOT/'informe/requerimientos-y-modelado.pdf')
figures=['sistema-casos-de-uso','proceso-completo','diagrama-de-clases','modelo-de-datos','wireframe-completo','mockup-completo','kanban']
for key in figures:
 src=fitz.open(ROOT/'diagramas'/f'{key}.pdf');page=out.new_page(width=842,height=595);page.show_pdf_page(fitz.Rect(24,24,818,571),src,0)
for k,n in M['pantallas']:
 src=fitz.open(ROOT/'mockups'/f'mockup-{k}.pdf');page=out.new_page(width=842,height=670);page.show_pdf_page(fitz.Rect(24,24,818,646),src,0)
out.save(ROOT/'informe/informe-con-diagramas.pdf');out.close()
print('Informe breve:',page if False else '7 páginas de texto y 16 páginas visuales')
