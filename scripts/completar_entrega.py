"""Completar la entrega visual a partir del modelo compartido del hotel."""
from pathlib import Path
import json, html, shutil, runpy, urllib.parse, xml.etree.ElementTree as ET
import fitz
ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'scripts/construir_modelado.py').read_text()
exec(source[:source.index('cases={')])
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Helvetica','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('Helvetica-Bold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
names={i:n for i,n,_ in MODEL['casos']}

# Una única imagen de casos de uso con asociaciones ortogonales y herencia real.
d=D('sistema-casos-de-uso','Casos de uso · Hotel Duerme Bien',1850,1900)
d.node('system','Sistema del hotel',300,90,1490,1740,'frame')
d.node('admin','Administrador',50,120,170,175,'actor')
d.node('enc','Encargado',50,1060,170,175,'actor')
d.edge('admin','enc',kind='general',source=(.5,1),target=(.5,0))
d.note('También realiza',215,610,17);d.note('las tareas del',215,640,17);d.note('encargado',215,670,17)
for i,id in enumerate(['CU02','CU08','CU10']):
 y=165+i*155;d.node(id,id+'\n'+names[id],420,y,580,90,'ellipse')
 d.edge('admin',id,points=[(260,181),(260,y+45)],kind='association',source=(.5,.35),target=(0,.5))
order=['CU01','CU03','CU09','CU11','CU12','CU04','CU06']
for i,id in enumerate(order):
 y=700+i*160;d.node(id,id+'\n'+names[id],420,y,580,90,'ellipse')
 d.edge('enc',id,points=[(270,1121.25),(270,y+45)],kind='association',source=(.5,.35),target=(0,.5))
d.node('CU05','CU05\n'+names['CU05'],1190,1180,500,90,'ellipse')
d.node('CU07','CU07\n'+names['CU07'],1190,1660,500,90,'ellipse')
for id,yy in [('CU09',1200),('CU11',1225),('CU04',1250)]:
 n=d.nodes[id];sy=n['y']+45
 d.edge(id,'CU05',points=[(1090,sy),(1090,yy)],label='«include»',kind='include',source=(1,.5),target=(0,(yy-1180)/90),labelpos=(1045,sy-28))
d.edge('CU06','CU07',label='«include»',kind='include',source=(1,.5),target=(0,.5),labelpos=(1090,1686))
d.note('Línea: puede hacer la tarea.  Flecha punteada: necesita esa otra tarea.',925,1870,18)
d.save()

# Reserva, entrada y salida en un mismo dibujo, con rutas claras de corrección.
d=D('proceso-completo','Reservar · Entrar · Salir',2400,1700)
def process(prefix,x,title,steps):
 d.node(prefix+'-title',title,x+50,90,560,60,'caption')
 for i,(key,label,shape) in enumerate(steps):d.node(prefix+key,label,x+70,190+i*175,460,105,shape)
 for i in range(len(steps)-1):
  a=prefix+steps[i][0];b=prefix+steps[i+1][0]
  d.edge(a,b,label='Sí' if steps[i][2]=='diamond' else '',labelpos=(x+330,190+i*175+144))
 # Las alternativas vuelven al formulario: la flecha final apunta a la caja.
 for i,(key,label,shape) in enumerate(steps):
  if shape!='diamond':continue
  sy=190+i*175+52.5;backy=190+175+52.5
  side=x+610+(i-2)*36
  d.edge(prefix+key,prefix+steps[1][0],points=[(side,sy),(side,backy)],label='No: corregir',source=(1,.5),target=(1-12.5/460,.5),labelpos=(side-4,sy-20))
process('r',0,'1 Guardar una habitación',[
 ('start','Inicio','ellipse'),('data','Anotar titular, habitación,\nfechas y cantidad de personas','input'),
 ('valid','¿Datos correctos?','diamond'),('free','¿Disponible y con espacio?','diamond'),
 ('save','Guardar reserva','rect'),('end','Fin · habitación reservada','ellipse')])
process('i',800,'2 Registrar la llegada',[
 ('start','Inicio','ellipse'),('data','Elegir reserva o ingreso directo;\nanotar a todos los huéspedes','input'),
 ('valid','¿Fechas y huéspedes correctos?','diamond'),('free','¿Disponible y con espacio?','diamond'),
 ('save','Guardar estadía y pasajeros;\nmarcar reserva CHECK_IN si existe','rect'),('end','Fin · habitación ocupada','ellipse')])
process('o',1600,'3 Registrar la salida',[
 ('start','Inicio','ellipse'),('data','Elegir estadía activa\ny fecha de salida','input'),
 ('valid','¿Fecha y tarifa correctas?','diamond'),('calc','Calcular cuenta por persona','rect'),
 ('confirm','¿Cuenta confirmada y\nsalida sin conflicto?','diamond'),
 ('save','Guardar costos, cerrar estadía\ny liberar habitación','rect'),('end','Fin · salida registrada','ellipse')])
d.note('Una reserva puede modificarse o cancelarse antes de la llegada.',1200,1530,24)
d.note('La entrada también puede registrarse sin reserva.',1200,1570,24)
d.save()

# Imágenes reales de cada gráfico, sin agrupar gráficos distintos en una imagen.
for key,out in [('sistema-casos-de-uso','casos-de-uso'),('proceso-completo','procesos'),('diagrama-de-clases','clases'),('modelo-de-datos','base-de-datos'),('wireframe-completo','wireframe'),('mockup-completo','mockup'),('kanban','kanban')]:
 pdf=fitz.open(ROOT/'diagramas'/f'{key}.pdf');pdf[0].get_pixmap(matrix=fitz.Matrix(1,1),alpha=False).save(ROOT/'resumenes'/f'{out}.png')

# Fuentes SVG con textos y figuras separados, listas para importar como capas.
fig=ROOT/'figma';fig.mkdir(exist_ok=True)
for mode in ['wireframe','mockup']:
 for key,name in MODEL['pantallas']:
  shutil.copyfile(ROOT/'mockups'/f'{mode}-{key}.svg',fig/f'{mode}-{key}.svg')
for mode in ['wireframe','mockup']:
 groups=[]
 for i,(key,name) in enumerate(MODEL['pantallas']):
  doc=ET.parse(fig/f'{mode}-{key}.svg').getroot()
  inner=''.join(ET.tostring(x,encoding='unicode') for x in doc)
  x=(i%3)*1560;y=(i//3)*1250
  groups.append(f'<g id="{key}" transform="translate({x},{y})">{inner}</g>')
 (fig/f'{mode}-todas-las-pantallas.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="4680" height="3750" viewBox="0 0 4680 3750">'+''.join(groups)+'</svg>')
manifest={'herramienta_de_los_videos':'Figma','file_url':None,'estado':'Pendiente de crear el archivo en Figma','pantallas':[k for k,n in MODEL['pantallas']],'fuentes':['https://www.youtube.com/watch?v=PbjNO8Ya3_0','https://www.youtube.com/watch?v=pM53Vj2yqMo&list=PLyezufEz_5vbqXgI9b30PF4_XLInLYGe_']}
if (fig/'proyecto.json').exists():
 old=json.loads((fig/'proyecto.json').read_text())
 if old.get('file_url'):manifest=old
(fig/'proyecto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(fig/'README.md').write_text('# Pantallas para Figma\n\nWireframes y mockups de las nueve pantallas. Cada SVG contiene figuras y textos separados para su edición.\n\n'+('[Abrir archivo en Figma]('+manifest['file_url']+')\n' if manifest.get('file_url') else 'Los SVG están preparados; todavía no hay un archivo creado en Figma ni un enlace de edición.\n'))

cards=''.join(f'<section><h2>{html.escape(name)}</h2><img src="mockup-{key}.svg" alt="{html.escape(name)}"><p><a href="wireframe-{key}.svg" download>Wireframe SVG</a> · <a href="mockup-{key}.svg" download>Mockup SVG</a></p></section>' for key,name in MODEL['pantallas'])
(fig/'index.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pantallas para Figma</title><style>body{font:18px Arial;margin:30px auto;max-width:1100px;padding:20px;color:#183746}img{width:100%}section{margin:40px 0}a{color:#136879}</style><h1>Pantallas para Figma</h1><p>'+('Archivo creado: <a href="'+html.escape(manifest['file_url'])+'">Editar en Figma</a>' if manifest.get('file_url') else 'SVG editables preparados. El archivo en Figma está pendiente.')+'</p><p><a href="../">Volver al proyecto</a> · <a href="wireframe-todas-las-pantallas.svg" download>Todos los wireframes</a> · <a href="mockup-todas-las-pantallas.svg" download>Todos los mockups</a></p>'+cards+'</html>')

repo='https://github.com/Yutre3/hotel-duerme-bien';site='https://yutre3.github.io/hotel-duerme-bien/'
def edit(key):return 'https://app.diagrams.net/?mode=device#U'+urllib.parse.quote('https://raw.githubusercontent.com/Yutre3/hotel-duerme-bien/main/diagramas-editables/'+key+'.drawio',safe='')
items=[('Quién hace cada tarea','Casos de uso','casos-de-uso','sistema-casos-de-uso'),('Reservar, llegar y salir','Diagrama de flujo','procesos','proceso-completo'),('Las partes del sistema','Diagrama de clases','clases','diagrama-de-clases'),('Dónde se guardan los datos','Base de datos','base-de-datos','modelo-de-datos'),('Dónde va cada botón','Wireframe','wireframe','wireframe-completo'),('Cómo se verá el sistema','Mockup','mockup','mockup-completo'),('Qué está hecho y qué falta','Kanban','kanban','kanban')]
md='# Hotel Duerme Bien\n\n**Proyecto 6 · Luis Huenchul**\n\n[Ver proyecto]('+site+') · [Probar sistema]('+site+'prototipo/) · [Informe](informe/informe-con-diagramas.pdf)\n'
sections=''
for label,kind,img,key in items:
 md+=f'\n## {kind}\n\n![{label}](resumenes/{img}.png)\n\n[Editar en diagrams.net]({edit(key)})\n'
 sections+=f'<section id="{img}" class="card"><div class="heading"><div><span>{kind}</span><h2>{label}</h2></div><div class="links"><a href="diagramas/{key}.svg">Ver grande</a><a href="{edit(key)}" target="_blank" rel="noopener">Editar</a></div></div><a href="diagramas/{key}.svg"><img src="resumenes/{img}.png" alt="{kind} del Hotel Duerme Bien" loading="lazy"></a></section>'
figlink='<a href="'+html.escape(manifest['file_url'])+'">Editar en Figma</a>' if manifest.get('file_url') else '<a href="figma/">Archivos preparados para Figma</a>'
md+='\n## Pantallas\n\n[Ver las nueve pantallas]('+site+'mockups/) · [Abrir demo en Figma]('+manifest.get('prototype_url',manifest.get('file_url','figma/'))+') · [Editar en Figma]('+manifest.get('file_url','figma/')+')\n\n## Entregas\n\n[Informe editable](informe/requerimientos-y-modelado.md) · [Kanban](planificacion/kanban.md) · [Material del profesor](fuentes/) · [Videos y herramientas](fuentes/videos-y-herramientas.md)\n'
(ROOT/'README.md').write_text(md)
css='''*{box-sizing:border-box}body{margin:0;color:#183746;background:#f1f5f6;font:17px/1.5 Arial,sans-serif}header,main,footer{max-width:1180px;margin:auto;padding:24px}header{padding-top:48px}h1{font-size:44px;margin:0}h2{font-size:26px;margin:0}p{margin:8px 0 24px}a{color:#136879}.buttons,.links,nav{display:flex;flex-wrap:wrap;gap:12px}.button,.links a{border:1px solid #b8cdd2;padding:10px 16px;border-radius:8px;text-decoration:none;background:white;font-weight:bold}.button.primary{background:#166879;color:white;border-color:#166879}.card{background:white;border:1px solid #cedde1;border-radius:14px;margin:24px 0;padding:26px}.heading{display:flex;justify-content:space-between;gap:24px;align-items:center}.heading span{font-size:14px;color:#65747a}.card img{display:block;width:100%;height:auto;margin-top:24px}.route{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:28px 0}.route div{background:#e8f2f3;padding:18px;border-radius:10px}.route strong{display:block;font-size:23px}.route span{font-size:30px}.demo{width:100%;height:830px;border:1px solid #ccd8dc;border-radius:10px;margin-top:20px}nav{margin:24px 0}nav a{font-size:15px}footer{font-size:14px;color:#65747a}@media(max-width:760px){h1{font-size:34px}.route{grid-template-columns:1fr 1fr}.heading{display:block}.links{margin-top:14px}.card{padding:18px}header,main{padding:18px}}'''
page=f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hotel Duerme Bien</title><style>{css}</style></head><body><header><h1>Hotel Duerme Bien</h1><p>Proyecto 6 · Luis Huenchul</p><div class="buttons"><a class="button primary" href="prototipo/">Probar sistema</a><a class="button" href="informe/informe-con-diagramas.pdf">Informe</a><a class="button" href="{repo}">Repositorio</a></div><div class="route"><div><span>▣</span><strong>1 Buscar habitación</strong></div><div><span>▤</span><strong>2 Guardar reserva</strong></div><div><span>↪</span><strong>3 Registrar llegada</strong></div><div><span>↩</span><strong>4 Registrar salida</strong></div></div><nav>'''+''.join(f'<a href="#{img}">{kind}</a>' for _,kind,img,key in items)+f'''</nav></header><main>{sections}<section class="card"><h2>Pantallas editables</h2><div class="links"><a href="mockups/">Ver las nueve pantallas</a>{figlink}<a href="{edit('interfaces')}">Editar en diagrams.net</a></div></section><section class="card"><h2>Probar el sistema</h2><div class="links"><a href="prototipo/">Abrir en pantalla completa</a><a href="https://github.dev/Yutre3/hotel-duerme-bien/tree/main/prototipo">Editar código</a></div><iframe class="demo" src="prototipo/" title="Demostración del hotel" loading="lazy"></iframe></section></main><footer><a href="informe/requerimientos-y-modelado.md">Informe editable</a> · <a href="fuentes/videos-y-herramientas.md">Videos y herramientas</a> · <a href="{repo}/tree/main/fuentes">Material del profesor</a></footer></body></html>'''
(ROOT/'index.html').write_text(page)

# Evidencia de herramientas verificada, sin atribuir falsamente creación en Figma.
(ROOT/'fuentes/videos-y-herramientas.md').write_text('''# Videos y herramientas

| Material | Herramienta | Uso |
|---|---|---|
| [Wireframes en Figma](https://www.youtube.com/watch?v=PbjNO8Ya3_0) | Figma | Dibujar la estructura de las pantallas. |
| [Tutorial Figma 1 Introducción a Figma](https://www.youtube.com/watch?v=pM53Vj2yqMo&list=PLyezufEz_5vbqXgI9b30PF4_XLInLYGe_) | Figma | Trabajar con el editor de interfaces. |
| [Cómo usar GitHub](https://www.youtube.com/watch?v=44ziZ12rJwU) | Git y GitHub | Guardar y compartir el proyecto. |
| Github_Git_VSCode | Git, GitHub y VS Code | Clonar, editar y guardar cambios en el repositorio. |
| Guías UML y base de datos | diagrams.net | Figuras y conectores editables de los diagramas. La guía no obliga a un editor único. |

Los títulos de los dos videos de Figma fueron verificados en YouTube. No se afirma haber revisado cada minuto. El estado real del archivo de Figma se registra en figma/proyecto.json.
''')

# Informe completo conservado; se corrigen referencias y ausencia de los videos.
report=ROOT/'informe/requerimientos-y-modelado.md'
t=report.read_text()
t=t.replace('No se recibieron rúbrica, plantilla IEEE original, PPT/PPTX ni videos; no se simula haberlos consultado.','Se recibieron tres enlaces de video: Wireframes en Figma, Introducción a Figma y Cómo usar GitHub. Los dos primeros identifican Figma como herramienta de interfaces. No se recibieron rúbrica ni plantilla IEEE original. [Videos y herramientas](../fuentes/videos-y-herramientas.md).')
t=t.replace('Se conserva diagrams.net porque es el formato del repositorio de referencia. No se afirma haber creado proyectos en plataformas distintas.','Los diagramas UML y de datos se editan en diagrams.net. Las interfaces también cuentan con SVG de capas separadas para Figma, la herramienta de los videos. El enlace del archivo de Figma se registra únicamente después de crearlo.')
t=t.replace('Los flujos muestran inicio/fin, entradas/salidas, acciones, decisiones con salidas etiquetadas, retornos por error y finalización sin cambios.','Los flujos muestran inicio/fin, entradas/salidas, acciones y decisiones. El proceso completo devuelve los errores al formulario. Los diagramas detallados también muestran salidas sin cambios.')
report.write_text(t)
print('Entrega visual actualizada.')

# Mantener el modelo de figuras sincronizado con los dos diagramas renovados.
scenes_path=ROOT/'modelo/diagramas.json'
scenes=json.loads(scenes_path.read_text())
keys={x.key for x in ALL}
scenes=[v for v in scenes if v['key'] not in keys]+[dict(key=x.key,title=x.title,nodes=x.nodes,edges=x.edges) for x in ALL]
scenes_path.write_text(json.dumps(scenes,ensure_ascii=False,indent=2))
