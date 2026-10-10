from pathlib import Path
import json,html,math,textwrap,xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1]
MODEL=json.loads((ROOT/'modelo/sistema.json').read_text())
BLUE='#163b50';INK='#253747';EDGE='#30363b';LIGHT='#edf4f7';WHITE='#ffffff';TEAL='#20aaa9';RED='#ff7474'
ALL=[]
class D:
 def __init__(self,key,title,w,h):self.key=key;self.title=title;self.w=w;self.h=h;self.nodes={};self.edges=[];self.notes=[];ALL.append(self)
 def node(self,id,label,x,y,w=400,h=90,shape='rect',attrs=None,methods=None,fill=WHITE,stroke=EDGE):
  self.nodes[id]=dict(id=id,label=label,x=x,y=y,w=w,h=h,shape=shape,attrs=attrs or [],methods=methods or [],fill=fill,stroke=stroke);return id
 def edge(self,a,b,points=None,label='',kind='arrow',source=(.5,1),target=(.5,0),sm='',tm='',labelpos=None,smpos=None,tmpos=None):
  A=self.nodes[a];B=self.nodes[b];p=(A['x']+A['w']*source[0],A['y']+A['h']*source[1]);q=(B['x']+B['w']*target[0],B['y']+B['h']*target[1]);self.edges.append(dict(a=a,b=b,points=[p]+(points or [])+[q],label=label,kind=kind,sm=sm,tm=tm,source=source,target=target,labelpos=labelpos,smpos=smpos,tmpos=tmpos))
 def note(self,text,x,y,size=16):self.notes.append((text,x,y,size))
 def save(self):
  svg=[];c=canvas.Canvas(str(ROOT/'diagramas'/f'{self.key}.pdf'),pagesize=(self.w,self.h));c.setTitle(self.title)
  def text(t,x,y,size=18,anchor='middle',bold=False,color=INK):
   svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{"bold" if bold else "normal"}">{html.escape(str(t))}</text>');c.setFillColor(colors.HexColor(color));c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);fn=c.drawCentredString if anchor=='middle' else c.drawString;fn(x,self.h-y,str(t))
  def boxed_text(t,x,y,size=20,bold=True,color=BLUE):
   width=max(48,len(str(t))*size*.62+20);height=size+14
   svg.append(f'<rect x="{x-width/2}" y="{y-size-3}" width="{width}" height="{height}" rx="5" fill="#ffffff" stroke="none"/>')
   c.setFillColor(colors.white);c.roundRect(x-width/2,self.h-y-8,width,height,5,fill=1,stroke=0)
   text(t,x,y,size,'middle',bold,color)
  def path(pts,fill='none',dash=False,closed=False,stroke=EDGE):
   d='M'+' L'.join(f'{x},{y}' for x,y in pts)+(' Z' if closed else '');svg.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="4"'+(' stroke-dasharray="12 8"' if dash else '')+'/>');c.setStrokeColor(colors.HexColor(stroke));c.setLineWidth(4);c.setDash(12,8) if dash else c.setDash();p=c.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1]);[p.lineTo(x,self.h-y) for x,y in pts[1:]]
   if closed:p.close()
   if fill!='none':c.setFillColor(colors.HexColor(fill))
   c.drawPath(p,fill=int(fill!='none'),stroke=1);c.setDash()
  def ellipse(x,y,w,h,fill=WHITE,stroke=EDGE):
   svg.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="4"/>');c.setStrokeColor(colors.HexColor(stroke));c.setLineWidth(4);c.setFillColor(colors.HexColor(fill));c.ellipse(x,self.h-y-h,x+w,self.h-y,fill=1)
  def mark(tip,other,kind):
   x,y=tip;dx,dy=other[0]-x,other[1]-y;l=math.hypot(dx,dy) or 1;u,v=dx/l,dy/l
   def p(a,b):return (x+u*a-v*b,y+v*a+u*b)
   if kind=='arrow':path([p(13,-6),tip,p(13,6)])
   elif kind=='general':path([tip,p(19,-11),p(19,11)],WHITE,closed=True)
   elif kind=='composition':path([tip,p(10,-7),p(20,0),p(10,7)],EDGE,closed=True)
   elif kind=='aggregation':path([tip,p(10,-7),p(20,0),p(10,7)],WHITE,closed=True)
   elif kind in ['one','zeroone','many','zeromany','onemany']:
    if 'many' in kind:
     path([p(18,0),p(0,-8)]);path([p(18,0),tip]);path([p(18,0),p(0,8)])
    else:path([p(6,-9),p(6,9)])
    if kind.startswith('zero'):
     cx,cy=p(27,0);ellipse(cx-5,cy-5,10,10)
    else:path([p(25,-9),p(25,9)])
  text(self.title,self.w/2,44,27,bold=True,color=BLUE)
  for n in self.nodes.values():
   if n['shape']=='frame':
    x,y,w,h=n['x'],n['y'],n['w'],n['h'];path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],WHITE,closed=True);text(n['label'],x+20,y+30,20,'start',True)
  for e in self.edges:
   pts=e['points'];path(pts,dash=e['kind']=='include')
   if e['kind'] in ['arrow','include','general']:mark(pts[-1],pts[-2],'general' if e['kind']=='general' else 'arrow')
   if e['kind'] in ['composition','aggregation']:mark(pts[0],pts[1],e['kind'])
   if e['kind']=='er':mark(pts[0],pts[1],e['sm']);mark(pts[-1],pts[-2],e['tm'])
   if e['label']:
    pos=e['labelpos'] or ((pts[0][0]+pts[-1][0])/2,(pts[0][1]+pts[-1][1])/2-13);boxed_text(e['label'],*pos,20)
   if e['kind']!='er':
    for t,p,o,manual in [(e['sm'],pts[0],pts[1],e.get('smpos')),(e['tm'],pts[-1],pts[-2],e.get('tmpos'))]:
     if t:
      if manual:
       boxed_text(t,*manual,23)
      else:
       dx,dy=o[0]-p[0],o[1]-p[1];l=math.hypot(dx,dy) or 1
       # La multiplicidad queda junto a su extremo y separada de la línea.
       u,v=dx/l,dy/l;boxed_text(t,p[0]+u*55-v*24,p[1]+v*55+u*24,23)
  for n in self.nodes.values():
   x,y,w,h=n['x'],n['y'],n['w'],n['h'];sh=n['shape'];fill=n['fill'];stroke=n.get('stroke',EDGE)
   if sh=='frame':continue
   if sh=='caption':
    text(n['label'],x+4,y+h/2+6,17,'start',color=n.get('color',INK));continue
   if sh=='actor':
    ellipse(x+w/2-16,y,32,32,WHITE,stroke);cx=x+w/2;path([(cx,y+32),(cx,y+90)],stroke=stroke);path([(cx-35,y+57),(cx+35,y+57)],stroke=stroke);path([(cx,y+90),(cx-30,y+135)],stroke=stroke);path([(cx,y+90),(cx+30,y+135)],stroke=stroke);text(n['label'],cx,y+162,20);continue
   if sh in ['rounded','control']:
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="4"/>');c.setFillColor(colors.HexColor(fill));c.setStrokeColor(colors.HexColor(stroke));c.setLineWidth(4);c.roundRect(x,self.h-y-h,w,h,8,fill=1)
   elif sh=='ellipse':ellipse(x,y,w,h,fill,stroke)
   elif sh=='diamond':path([(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)],fill,closed=True,stroke=stroke)
   elif sh=='input':path([(x+25,y),(x+w,y),(x+w-25,y+h),(x,y+h)],fill,closed=True,stroke=stroke)
   else:path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,closed=True,stroke=stroke)
   if sh=='table':
    path([(x,y+58),(x+w,y+58)],stroke=stroke);text(n['label'],x+w/2,y+39,28,bold=True)
    for i,t in enumerate(n['attrs']):text(t,x+22,y+94+i*42,27,'start')
    sy=y+72+len(n['attrs'])*42
    if n['methods']:
     path([(x,sy),(x+w,sy)],stroke=stroke)
     for i,t in enumerate(n['methods']):text(t,x+22,sy+37+i*42,27,'start')
   elif sh=='frame':text(n['label'],x+20,y+30,20,'start',True)
   else:
    lines=n['label'].split('\n');size=22 if sh!='diamond' else 20
    for i,t in enumerate(lines):text(t,x+15 if sh=='control' else x+w/2,y+h/2+(i-(len(lines)-1)/2)*25+7,size,anchor='start' if sh=='control' else 'middle',bold=n.get('bold',False) or sh=='ellipse' and n['id'].startswith('CU'),color=n.get('color',INK))
  for t,x,y,size in self.notes:text(t,x,y,size)
  (ROOT/'diagramas'/f'{self.key}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/><g font-family="Arial,sans-serif">'+''.join(svg)+'</g></svg>');c.save()
  mx=ET.Element('mxfile',host='app.diagrams.net');dia=ET.SubElement(mx,'diagram',id=self.key,name=self.title);g=ET.SubElement(dia,'mxGraphModel',grid='1',gridSize='10',page='1',pageWidth=str(self.w),pageHeight=str(self.h));root=ET.SubElement(g,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
  def vertex(id,value,style,x,y,w,h,parent='1'):
   c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent=parent);ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
  for n in self.nodes.values():
   sh=n['shape'];styles={'caption':'text;strokeColor=none;fillColor=none;align=left;','control':'rounded=1;align=left;spacingLeft=15;','rounded':'rounded=1;','rect':'rounded=0;','ellipse':'ellipse;','input':'shape=parallelogram;fixedSize=1;size=25;','diamond':'rhombus;','actor':'shape=umlActor;','frame':'rounded=0;verticalAlign=top;align=left;spacing=18;','table':'shape=swimlane;startSize=44;horizontal=1;collapsible=0;'}
   title=n['label'];style=styles[sh]+f'html=0;whiteSpace=wrap;strokeColor={n.get("stroke",EDGE)};strokeWidth=4;fillColor={n["fill"]};fontColor={n.get('color',INK)};fontSize=21;'+('fontStyle=1;' if sh=='table' or n.get('bold') else '')
   if sh=='caption':style+='strokeColor=none;fillColor=none;'
   vertex(n['id'],title,style,n['x'],n['y'],n['w'],n['h'])
   if sh=='table':
    vertex(n['id']+'-attrs','\n'.join(n['attrs']),f'text;html=0;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=20;fontSize=27;',0,68,n['w'],len(n['attrs'])*42,n['id'])
    if n['methods']:
     sy=72+len(n['attrs'])*42;vertex(n['id']+'-methods','\n'.join(n['methods']),f'text;html=0;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=20;fontSize=27;',0,sy+13,n['w'],len(n['methods'])*42,n['id']);vertex(n['id']+'-line','',f'shape=line;strokeColor={EDGE};strokeWidth=3;',0,sy,n['w'],1,n['id'])
  for i,e in enumerate(self.edges):
   sa='none';ea='none';kind=e['kind']
   if kind in ['arrow','include']:ea='open'
   if kind=='general':ea='block'
   if kind=='composition':sa='diamond'
   if kind=='aggregation':sa='diamond'
   er={'one':'ERmandOne','zeroone':'ERzeroToOne','many':'ERmany','zeromany':'ERzeroToMany','onemany':'ERoneToMany'}
   if kind=='er':sa=er[e['sm']];ea=er[e['tm']]
   style=f'html=0;edgeStyle=orthogonalEdgeStyle;orthogonalLoop=1;jettySize=32;rounded=0;strokeWidth=4;strokeColor={EDGE};fontSize=22;fontStyle=1;fontColor={BLUE};labelBackgroundColor=#ffffff;endArrow={ea};endFill=0;startArrow={sa};startFill={1 if kind=="composition" else 0};exitX={e["source"][0]};exitY={e["source"][1]};exitPerimeter=0;entryX={e["target"][0]};entryY={e["target"][1]};entryPerimeter=0;'+('dashed=1;' if kind=='include' else '')
   c=ET.SubElement(root,'mxCell',id='edge'+str(i),value=e['label'],style=style,edge='1',source=e['a'],target=e['b'],parent='1');geo=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
   for x,y in e['points'][1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
   if kind!='er':
    for j,(label,t) in enumerate([(e['sm'],-.9),(e['tm'],.9)]):
     if label:
      v=ET.SubElement(root,'mxCell',id=f'edge{i}-label{j}',value=label,style='edgeLabel;html=0;align=center;fontSize=25;fontStyle=1;fontColor='+BLUE+';labelBackgroundColor=#ffffff;',vertex='1',connectable='0',parent='edge'+str(i));gg=ET.SubElement(v,'mxGeometry',x=str(t),y='-1',relative='1',attrib={'as':'geometry'});ET.SubElement(gg,'mxPoint',y='-14',attrib={'as':'offset'})
  for i,(t,x,y,size) in enumerate(self.notes):vertex('note'+str(i),t,'text;html=0;strokeColor=none;fillColor=none;fontSize='+str(size)+';',x-450,y-25,900,35)
  ET.indent(mx);ET.ElementTree(mx).write(ROOT/'diagramas-editables'/f'{self.key}.drawio',encoding='utf-8',xml_declaration=True)

cases={i:n for i,n,_ in MODEL['casos']}
d=D('casos-de-uso','Casos de uso · Operación del hotel',1650,1640)
d.node('limit','Duerme Bien',260,85,1330,1470,'frame');d.node('enc','Encargado',35,600,165,175,'actor')
ys={'CU01':170,'CU03':345,'CU04':520,'CU09':695,'CU11':870,'CU12':1045,'CU06':1280}
for i,(id,y) in enumerate(ys.items()):
 d.node(id,id+'\n'+cases[id],340,y,440,90,'ellipse')
 # Cada asociación sale por un punto diferente y va directamente a su caso.
 d.edge('enc',id,kind='association',source=(1,.16+i*.115),target=(0,.5))
d.node('CU05','CU05\n'+cases['CU05'],1070,685,440,90,'ellipse');d.node('CU07','CU07\n'+cases['CU07'],1070,1280,440,90,'ellipse')
for id,ty in [('CU04',.25),('CU09',.5),('CU11',.75)]:
 d.edge(id,'CU05',label='«include»',kind='include',source=(1,.5),target=(0,ty),labelpos=(900,ys[id]+30))
d.edge('CU06','CU07',label='«include»',kind='include',source=(1,.5),target=(0,.5),labelpos=(925,1305))
d=D('casos-de-uso-administracion','Casos de uso · Administración',1320,1020)
d.node('limit','Duerme Bien',420,85,820,850,'frame');d.node('enc','Encargado',115,100,165,175,'actor');d.node('admin','Administrador',115,550,165,175,'actor');d.edge('admin','enc',kind='general',source=(.5,0),target=(.5,1))
for i,id in enumerate(['CU02','CU08','CU10']):
 d.node(id,id+'\n'+cases[id],585,290+i*220,470,95,'ellipse');d.edge('admin',id,kind='association',source=(.5,.35),target=(0,.5))

# Flujos con rutas de validación, rechazo, cancelación y confirmación.
def flow(key,title,steps,branches):
 h=180+len(steps)*165;d=D(key,title,1660,h)
 for i,(id,t,sh) in enumerate(steps):
  d.node(id,t,450,95+i*165,480,95,sh,stroke=RED if sh=='ellipse' else TEAL if sh=='input' else EDGE)
 for i in range(len(steps)-1):
  id=steps[i][0];label='Sí' if steps[i][2]=='diamond' else '';d.edge(id,steps[i+1][0],label=label,labelpos=(720,95+i*165+130))
 for i,(origin,text,back) in enumerate(branches):
  n=d.nodes[origin];side='error'+str(i)
  # Cada alternativa termina en un solo resultado, sin retornos ni cajas repetidas.
  ending='Fin ·\n'+'\n'.join(textwrap.wrap(text.replace('\n',' ').lower(),28))
  d.node(side,ending,1090,n['y'],390,95,'ellipse',stroke=RED);d.edge(origin,side,label='No',source=(1,.5),target=(0,.5),labelpos=(1010,n['y']+32))
 return d
flow('flujo-reserva','Registrar reserva · CU09',[
 ('inicio','Inicio','ellipse'),('datos','Capturar titular, habitación,\nfechas y cantidad de pasajeros','input'),('validar','¿Titular registrado y\ndatos completos y válidos?','diamond'),('consultar','Consultar disponibilidad\npara intervalo y capacidad · CU05','rect'),('disponible','¿Habitación disponible\ny capacidad suficiente?','diamond'),('confirmar','¿Confirma la reserva?','diamond'),('guardar','Guardar reserva REGISTRADA','rect'),('respuesta','Mostrar número y resumen\nde reserva registrada','input'),('fin','Fin','ellipse')], [('validar','Mostrar campos\nque requieren corrección','datos'),('disponible','Mostrar conflicto y\notras habitaciones','datos'),('confirmar','Cancelar la operación',None)])
flow('flujo-check-in','Check-in y asignación · CU04',[
 ('inicio','Inicio','ellipse'),('datos','Seleccionar reserva o ingreso directo;\nhabitación, fechas y todos los huéspedes','input'),('origen','¿Sin reserva o reserva\nREGISTRADA?','diamond'),('identificar','Validar huéspedes registrados\ny cantidad de pasajeros','rect'),('validar','¿Fechas y pasajeros válidos,\nsin estadía activa previa?','diamond'),('consulta','Revisar capacidad, reservas\ny ocupación actual · CU05','rect'),('disponible','¿Habitación disponible y\ncapacidad suficiente?','diamond'),('confirmar','¿Confirma el ingreso?','diamond'),('guardar','Crear estadía ACTIVA\ny registrar ESTADIA_HUESPED','rect'),('actualizar','Si hay reserva: pasar a CHECK_IN;\nmostrar habitación OCUPADA','rect'),('respuesta','Mostrar estadía y\nlista de pasajeros asignados','input'),('fin','Fin','ellipse')], [('origen','Informar reserva inválida\no ya utilizada','datos'),('validar','Identificar pasajeros faltantes\no corregir sus datos','datos'),('disponible','Mostrar conflicto; elegir\nfechas o habitación distintas','datos'),('confirmar','Cancelar la operación',None)])
flow('flujo-check-out','Check-out y cuenta · CU06',[
 ('inicio','Inicio','ellipse'),('seleccionar','Seleccionar estadía\ny fecha de salida real','input'),('activa','¿Estadía ACTIVA y\nsalida posterior a entrada?','diamond'),('pasajeros','Recuperar huéspedes asignados\ny parámetros de cobro','rect'),('regla','¿Regla de cobro y\ntarifa válidas y definidas?','diamond'),('cuenta','Calcular costo por pasajero\ny total de cuenta · CU07','rect'),('detalle','Mostrar detalle por huésped,\nperíodo, costos y total','input'),('confirmar','¿Confirma la cuenta\ny la salida?','diamond'),('conflicto','¿Salida sin conflicto con\nreservas posteriores?','diamond'),('guardar','Guardar costo de cada pasajero\ny estadía FINALIZADA','rect'),('liberar','Cerrar reserva asociada, si existe;\nliberar ocupación de habitación','rect'),('fin','Fin','ellipse')], [('activa','Informar estadía\no fecha inválidas','seleccionar'),('regla','Solicitar definición o\ncorrección del cobro','pasajeros'),('confirmar','Mantener estadía ACTIVA',None),('conflicto','Resolver fecha de salida\ny conflicto de reserva','seleccionar')])
# Gestión de reservas: dos ramas limpias y un final propio para cada resultado.
d=D('flujo-gestion-reservas','Modificar o cancelar reserva · CU11 / CU12',1800,1530)
nodes=[
 ('inicio','Inicio',550,70,'ellipse'),('select','Seleccionar reserva',550,215,'input'),
 ('estado','¿Reserva REGISTRADA?',550,360,'diamond'),('op','¿Modificar o cancelar?',550,530,'diamond'),
 ('invalid','Informar que la reserva\nno admite cambios',1050,360,'rect'),('invalidFin','Fin sin cambios',1050,500,'ellipse'),
 ('mod','Modificar fechas,\nhabitación o cantidad',120,730,'input'),('disp','Validar datos y disponibilidad',120,885,'rect'),
 ('ok','¿Cambio válido?',120,1040,'diamond'),('save','Guardar cambios',120,1200,'rect'),('modFin','Fin · reserva modificada',120,1360,'ellipse'),
 ('modNo','Fin sin cambios',520,1040,'ellipse'),
 ('cancel','¿Confirma la cancelación?',950,730,'diamond'),('canceled','Marcar CANCELADA y\nliberar disponibilidad',950,930,'rect'),
 ('cancelFin','Fin · reserva cancelada',950,1090,'ellipse')]
for id,t,x,y,sh in nodes:d.node(id,t,x,y,400,90,sh,stroke=RED if sh=='ellipse' else TEAL if sh=='input' else EDGE)
d.node('cancelNo','Fin sin cambios',1450,850,300,80,'ellipse',stroke=RED)
for a,b in [('inicio','select'),('select','estado'),('estado','op'),('mod','disp'),('disp','ok'),('ok','save'),('save','modFin'),('invalid','invalidFin'),('cancel','canceled'),('canceled','cancelFin')]:d.edge(a,b,label='Sí' if a in ['estado','ok','cancel'] else '')
d.edge('estado','invalid',source=(1,.5),target=(0,.5),label='No')
d.edge('op','mod',points=[(320,650)],label='Modificar',labelpos=(350,650))
d.edge('op','cancel',points=[(1150,650)],label='Cancelar',labelpos=(1120,650))
d.edge('ok','modNo',source=(1,.5),target=(0,.5),label='No')
d.edge('cancel','cancelNo',points=[(1400,775),(1600,775)],source=(1,.5),target=(.5,0),label='No',labelpos=(1415,755))

# Clases y entidades provienen de las mismas definiciones.
tables={
 'ROL':('Rol',['id: int','nombre: String'],['permite(operacion: String): bool']),
 'USUARIO':('Usuario',['id: int','nombreUsuario: String','hashClave: String','activo: bool'],['iniciarSesion(clave: String): Sesion','asignarRol(rol: Rol): void','desactivar(): void']),
 'HABITACION':('Habitacion',['id: int','numero: String','capacidad: int','orientacion: String'],['disponible(entrada, salida): bool','actualizarDatos(): void']),
 'HUESPED':('Huesped',['id: int','identificacion: String','nombres: String','apellidos: String'],['registrar(): void','consultarHistorial(): List<Estadia>']),
 'RESERVA':('Reserva',['id: int','entrada: Date','salida: Date','cantidadPasajeros: int','estado: EstadoReserva'],['registrar(): void','modificar(): void','cancelar(): void']),
 'ESTADIA':('Estadia',['id: int','entrada: Date','salidaPrevista: Date','salidaReal: Date [0..1]','estado: EstadoEstadia','nochesCobradas: int [0..1]'],['registrarCheckIn(): void','calcularCuenta(): Dinero','registrarCheckOut(): void']),
 'ESTADIA_HUESPED':('EstadiaHuesped',['tarifaCLP: Dinero [0..1]','costoCLP: Dinero [0..1]'],['calcularCosto(regla): Dinero'])}
dbattrs={
 'ROL':['PK id_rol : INTEGER','UQ nombre : VARCHAR(30) NOT NULL'],
 'USUARIO':['PK id_usuario : INTEGER','FK id_rol : INTEGER NOT NULL','UQ nombre_usuario : VARCHAR(50) NOT NULL','hash_clave : VARCHAR(255) NOT NULL','activo : BOOLEAN NOT NULL'],
 'HABITACION':['PK id_habitacion : INTEGER','UQ numero : VARCHAR(20) NOT NULL','capacidad : INTEGER NOT NULL CHECK (capacidad > 0)','orientacion : VARCHAR(30) NOT NULL'],
 'HUESPED':['PK id_huesped : INTEGER','UQ identificacion : VARCHAR(50) NOT NULL','nombres : VARCHAR(100) NOT NULL','apellidos : VARCHAR(100) NOT NULL'],
 'RESERVA':['PK id_reserva : INTEGER','FK id_huesped_titular : INTEGER NOT NULL','FK id_habitacion : INTEGER NOT NULL','fecha_entrada : DATE NOT NULL','fecha_salida : DATE NOT NULL','cantidad_pasajeros : INTEGER NOT NULL CHECK > 0','estado : VARCHAR(20) NOT NULL','CHECK (fecha_salida > fecha_entrada)','CHECK estado: REGISTRADA / CHECK_IN / CANCELADA / FINALIZADA'],
 'ESTADIA':['PK id_estadia : INTEGER','FK id_habitacion : INTEGER NOT NULL','FK/UQ id_reserva : INTEGER NULL','fecha_entrada : DATE NOT NULL','fecha_salida_prevista : DATE NOT NULL','fecha_salida_real : DATE NULL','estado : VARCHAR(20) NOT NULL','noches_cobradas : INTEGER NULL CHECK > 0','CHECK estado: ACTIVA / FINALIZADA'],
 'ESTADIA_HUESPED':['PK/FK id_estadia : INTEGER','PK/FK id_huesped : INTEGER','tarifa_clp : INTEGER NULL CHECK >= 0','costo_clp : INTEGER NULL CHECK >= 0']}
# Modelo lógico en formato horizontal. Las relaciones usan pasillos libres y
# las cardinalidades se ubican junto a sus extremos, nunca sobre los campos.
d=D('modelo-de-datos','Modelo lógico de datos completo · Hotel Duerme Bien · 3FN',2200,3000)
db_layout={
 'ROL':(80,110,620),'USUARIO':(850,90,1260),
 'HUESPED':(80,620,900),'HABITACION':(1200,620,900),
 'RESERVA':(80,1260,980),'ESTADIA':(1200,1260,900),
 'ESTADIA_HUESPED':(650,2210,980)}
for id,(x,y,w) in db_layout.items():
 attrs=dbattrs[id];d.node(id,id,x,y,w,100+len(attrs)*42,'table',attrs,[])
def dbrel(a,b,source,target,points,sm,tm):
 d.edge(a,b,points=points,source=source,target=target,kind='er',sm=sm,tm=tm)
dbrel('ROL','USUARIO',(1,.5),(0,.5),[], 'one','zeromany')
dbrel('HUESPED','RESERVA',(.42,1),(.30,0),[(458,1135),(374,1135)],'one','zeromany')
dbrel('HABITACION','RESERVA',(.25,1),(1,.22),[(1425,1140),(1110,1140),(1110,1375)],'one','zeromany')
dbrel('HABITACION','ESTADIA',(.75,1),(.72,0),[(1875,1140),(1848,1140)],'one','zeromany')
dbrel('RESERVA','ESTADIA',(1,.62),(0,.62),[],'zeroone','zeroone')
dbrel('ESTADIA','ESTADIA_HUESPED',(.55,1),(1,.32),[(1695,2110),(1680,2110),(1680,2315)],'one','onemany')
dbrel('HUESPED','ESTADIA_HUESPED',(0,.50),(0,.50),[(25,754),(25,2344)],'one','zeromany')
d.note('PK = clave primaria   ·   FK = clave foránea   ·   UQ = valor único   ·   NULL = dato opcional',1100,2935,25)
db_model=d

# Clases de dominio. La zona operativa usa una distribución planar: huésped,
# reserva y habitación arriba; la clase asociativa y la estadía abajo. Así cada
# relación tiene un pasillo propio y ninguna línea necesita rodear la página.
d=D('diagrama-de-clases','Diagrama de clases completo · Hotel Duerme Bien',2400,2500)
class_defs={
 'ROL':('Rol',['- id: int','- nombre: String'],['+ permite(operacion: String): bool']),
 'USUARIO':('«abstract» Usuario',['- id: int','- nombreUsuario: String','- hashClave: String','- activo: bool'],['+ iniciarSesion(clave: String): Sesion','+ tienePermiso(operacion: String): bool']),
 'ADMIN':('Administrador',[],['+ gestionarHabitaciones(): void','+ gestionarUsuarios(): void','+ generarInformes(): void']),
 'ENCARGADO':('Encargado',[],['+ registrarReserva(): void','+ registrarCheckIn(): void','+ registrarCheckOut(): void']),
 'HABITACION':('Habitacion',['- id: int','- numero: String','- capacidad: int','- orientacion: String'],['+ disponible(entrada, salida): bool','+ actualizarDatos(): void']),
 'HUESPED':('Huesped',['- id: int','- identificacion: String','- nombres: String','- apellidos: String'],['+ registrar(): void','+ consultarHistorial(): List<Estadia>']),
 'RESERVA':('Reserva',['- id: int','- entrada: Date','- salida: Date','- cantidadPasajeros: int','- estado: EstadoReserva'],['+ registrar(): void','+ modificar(): void','+ cancelar(): void']),
 'ESTADIA':('Estadia',['- id: int','- entrada: Date','- salidaPrevista: Date','- salidaReal: Date [0..1]','- estado: EstadoEstadia','- nochesCobradas: int [0..1]'],['+ registrarCheckIn(): void','+ calcularCuenta(): Dinero','+ registrarCheckOut(): void']),
 'ESTADIA_HUESPED':('EstadiaHuesped',['- tarifaCLP: Dinero [0..1]','- costoCLP: Dinero [0..1]'],['+ calcularCosto(regla): Dinero'])}
class_layout={
 'ROL':(70,110,560),'USUARIO':(720,80,1600),
 'ADMIN':(200,520,850),'ENCARGADO':(1350,520,850),
 'HUESPED':(60,950,680),'RESERVA':(860,950,720),'HABITACION':(1720,950,620),
 'ESTADIA_HUESPED':(60,1900,740),'ESTADIA':(1450,1680,890)}
class_colors={'ROL':'#f1f3f4','USUARIO':'#d9efff','ADMIN':'#e8ddff','ENCARGADO':'#e8ddff','HABITACION':'#dff5e3','HUESPED':'#fff1c9','RESERVA':'#ffe0cf','ESTADIA':'#d9efff','ESTADIA_HUESPED':'#eadfff'}
for id,(x,y,w) in class_layout.items():
 title,attrs,methods=class_defs[id];d.node(id,title,x,y,w,100+(len(attrs)+len(methods))*42,'table',attrs,methods,fill=class_colors[id])
def classrel(a,b,source,target,points=None,sm='',tm='',kind='association',smpos=None,tmpos=None):
 d.edge(a,b,points=points,source=source,target=target,kind=kind,sm=sm,tm=tm,smpos=smpos,tmpos=tmpos)
classrel('ROL','USUARIO',(1,.5),(0,.5),sm='1',tm='0..*',kind='association',smpos=(655,225),tmpos=(695,225))
classrel('ADMIN','USUARIO',(.65,0),(.30,1),kind='general')
classrel('ENCARGADO','USUARIO',(.35,0),(.70,1),kind='general')

# Relaciones del negocio: todos los conectores quedan entre clases vecinas.
classrel('HUESPED','RESERVA',(1,.45),(0,.36),sm='1',tm='0..*',kind='association',smpos=(775,1165),tmpos=(825,1165))
classrel('RESERVA','HABITACION',(1,.44),(0,.55),sm='0..*',tm='1',kind='association',smpos=(1620,1170),tmpos=(1680,1170))
classrel('HABITACION','ESTADIA',(.72,1),(.80,0),sm='1',tm='0..*',kind='association',smpos=(2200,1350),tmpos=(2200,1635))
classrel('RESERVA','ESTADIA',(.72,1),(0,.20),[(1378,1560),(1400,1560),(1400,1776)],'0..1','0..1','association',(1340,1430),(1410,1820))
classrel('HUESPED','ESTADIA_HUESPED',(.25,1),(.25,0),sm='1',tm='0..*',kind='association',smpos=(270,1350),tmpos=(270,1860))
classrel('ESTADIA','ESTADIA_HUESPED',(0,.68),(1,.48),sm='1',tm='1..*',kind='composition',smpos=(1400,1970),tmpos=(850,1970))
d.note('1 = uno   ·   0..1 = opcional   ·   0..* = cero o muchos   ·   1..* = uno o muchos   ·   △ = herencia   ·   ◆ = composición',1200,2410,23)
for d in ALL:d.save()
(ROOT/'modelo/diagramas.json').write_text(json.dumps([dict(key=d.key,title=d.title,nodes=d.nodes,edges=d.edges) for d in ALL],ensure_ascii=False,indent=2))
(ROOT/'modelo/base-de-datos.json').write_text(json.dumps({'entidades':dbattrs,'relaciones':db_model.edges},ensure_ascii=False,indent=2))
