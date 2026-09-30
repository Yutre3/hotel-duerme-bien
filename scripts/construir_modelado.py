from pathlib import Path
import json,html,math,xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1]
MODEL=json.loads((ROOT/'modelo/sistema.json').read_text())
BLUE='#163b50';INK='#253747';EDGE='#546778';LIGHT='#edf4f7';WHITE='#ffffff'
ALL=[]
class D:
 def __init__(self,key,title,w,h):self.key=key;self.title=title;self.w=w;self.h=h;self.nodes={};self.edges=[];self.notes=[];ALL.append(self)
 def node(self,id,label,x,y,w=400,h=90,shape='rect',attrs=None,methods=None,fill=WHITE):
  self.nodes[id]=dict(id=id,label=label,x=x,y=y,w=w,h=h,shape=shape,attrs=attrs or [],methods=methods or [],fill=fill);return id
 def edge(self,a,b,points=None,label='',kind='arrow',source=(.5,1),target=(.5,0),sm='',tm='',labelpos=None):
  A=self.nodes[a];B=self.nodes[b];p=(A['x']+A['w']*source[0],A['y']+A['h']*source[1]);q=(B['x']+B['w']*target[0],B['y']+B['h']*target[1]);self.edges.append(dict(a=a,b=b,points=[p]+(points or [])+[q],label=label,kind=kind,sm=sm,tm=tm,source=source,target=target,labelpos=labelpos))
 def note(self,text,x,y,size=16):self.notes.append((text,x,y,size))
 def save(self):
  svg=[];c=canvas.Canvas(str(ROOT/'diagramas'/f'{self.key}.pdf'),pagesize=(self.w,self.h));c.setTitle(self.title)
  def text(t,x,y,size=18,anchor='middle',bold=False,color=INK):
   svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}" font-weight="{"bold" if bold else "normal"}">{html.escape(str(t))}</text>');c.setFillColor(colors.HexColor(color));c.setFont('Helvetica-Bold' if bold else 'Helvetica',size);fn=c.drawCentredString if anchor=='middle' else c.drawString;fn(x,self.h-y,str(t))
  def path(pts,fill='none',dash=False,closed=False):
   d='M'+' L'.join(f'{x},{y}' for x,y in pts)+(' Z' if closed else '');svg.append(f'<path d="{d}" fill="{fill}" stroke="{EDGE}" stroke-width="2"'+(' stroke-dasharray="8 6"' if dash else '')+'/>');c.setStrokeColor(colors.HexColor(EDGE));c.setLineWidth(2);c.setDash(8,6) if dash else c.setDash();p=c.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1]);[p.lineTo(x,self.h-y) for x,y in pts[1:]]
   if closed:p.close()
   if fill!='none':c.setFillColor(colors.HexColor(fill))
   c.drawPath(p,fill=int(fill!='none'),stroke=1);c.setDash()
  def ellipse(x,y,w,h,fill=WHITE):
   svg.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{EDGE}" stroke-width="2"/>');c.setStrokeColor(colors.HexColor(EDGE));c.setFillColor(colors.HexColor(fill));c.ellipse(x,self.h-y-h,x+w,self.h-y,fill=1)
  def mark(tip,other,kind):
   x,y=tip;dx,dy=other[0]-x,other[1]-y;l=math.hypot(dx,dy) or 1;u,v=dx/l,dy/l
   def p(a,b):return (x+u*a-v*b,y+v*a+u*b)
   if kind=='arrow':path([p(13,-6),tip,p(13,6)])
   elif kind=='general':path([tip,p(19,-11),p(19,11)],WHITE,closed=True)
   elif kind=='composition':path([tip,p(10,-7),p(20,0),p(10,7)],EDGE,closed=True)
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
   if e['kind']=='composition':mark(pts[0],pts[1],'composition')
   if e['kind']=='er':mark(pts[0],pts[1],e['sm']);mark(pts[-1],pts[-2],e['tm'])
   if e['label']:
    pos=e['labelpos'] or ((pts[0][0]+pts[-1][0])/2,(pts[0][1]+pts[-1][1])/2-13);text(e['label'],*pos,16)
   if e['kind']!='er':
    for t,p,o in [(e['sm'],pts[0],pts[1]),(e['tm'],pts[-1],pts[-2])]:
     if t:
      dx,dy=o[0]-p[0],o[1]-p[1];l=math.hypot(dx,dy) or 1;text(t,p[0]+dx/l*37+(-18 if dy else 0),p[1]+dy/l*37-12,17)
  for n in self.nodes.values():
   x,y,w,h=n['x'],n['y'],n['w'],n['h'];sh=n['shape'];fill=n['fill']
   if sh=='frame':continue
   if sh=='caption':
    text(n['label'],x+4,y+h/2+6,17,'start',color=n.get('color',INK));continue
   if sh=='actor':
    ellipse(x+w/2-16,y,32,32);cx=x+w/2;path([(cx,y+32),(cx,y+90)]);path([(cx-35,y+57),(cx+35,y+57)]);path([(cx,y+90),(cx-30,y+135)]);path([(cx,y+90),(cx+30,y+135)]);text(n['label'],cx,y+162,20);continue
   if sh in ['rounded','control']:
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{EDGE}" stroke-width="1.3"/>');c.setFillColor(colors.HexColor(fill));c.setStrokeColor(colors.HexColor(EDGE));c.roundRect(x,self.h-y-h,w,h,8,fill=1)
   elif sh=='ellipse':ellipse(x,y,w,h,fill)
   elif sh=='diamond':path([(x+w/2,y),(x+w,y+h/2),(x+w/2,y+h),(x,y+h/2)],fill,closed=True)
   elif sh=='input':path([(x+25,y),(x+w,y),(x+w-25,y+h),(x,y+h)],fill,closed=True)
   else:path([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],fill,closed=True)
   if sh=='table':
    path([(x,y+44),(x+w,y+44)]);text(n['label'],x+w/2,y+30,20,bold=True)
    for i,t in enumerate(n['attrs']):text(t,x+14,y+72+i*28,17,'start')
    sy=y+55+len(n['attrs'])*28
    if n['methods']:
     path([(x,sy),(x+w,sy)])
     for i,t in enumerate(n['methods']):text(t,x+14,sy+27+i*28,17,'start')
   elif sh=='frame':text(n['label'],x+20,y+30,20,'start',True)
   else:
    lines=n['label'].split('\n');size=19 if sh!='diamond' else 18
    for i,t in enumerate(lines):text(t,x+15 if sh=='control' else x+w/2,y+h/2+(i-(len(lines)-1)/2)*25+7,size,anchor='start' if sh=='control' else 'middle',bold=n.get('bold',False) or sh=='ellipse' and n['id'].startswith('CU'),color=n.get('color',INK))
  for t,x,y,size in self.notes:text(t,x,y,size)
  (ROOT/'diagramas'/f'{self.key}.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><rect width="100%" height="100%" fill="white"/><g font-family="Arial,sans-serif">'+''.join(svg)+'</g></svg>');c.save()
  mx=ET.Element('mxfile',host='app.diagrams.net');dia=ET.SubElement(mx,'diagram',id=self.key,name=self.title);g=ET.SubElement(dia,'mxGraphModel',grid='1',gridSize='10',page='1',pageWidth=str(self.w),pageHeight=str(self.h));root=ET.SubElement(g,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0')
  def vertex(id,value,style,x,y,w,h,parent='1'):
   c=ET.SubElement(root,'mxCell',id=id,value=value,style=style,vertex='1',parent=parent);ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
  for n in self.nodes.values():
   sh=n['shape'];styles={'caption':'text;strokeColor=none;fillColor=none;align=left;','control':'rounded=1;align=left;spacingLeft=15;','rounded':'rounded=1;','rect':'rounded=0;','ellipse':'ellipse;','input':'shape=parallelogram;fixedSize=1;size=25;','diamond':'rhombus;','actor':'shape=umlActor;','frame':'rounded=0;verticalAlign=top;align=left;spacing=18;','table':'shape=swimlane;startSize=44;horizontal=1;collapsible=0;'}
   title=n['label'];style=styles[sh]+f'html=0;whiteSpace=wrap;strokeColor={EDGE};strokeWidth=2;fillColor={n["fill"]};fontColor={n.get('color',INK)};fontSize=19;'+('fontStyle=1;' if sh=='table' or n.get('bold') else '')
   if sh=='caption':style+='strokeColor=none;fillColor=none;'
   vertex(n['id'],title,style,n['x'],n['y'],n['w'],n['h'])
   if sh=='table':
    vertex(n['id']+'-attrs','\n'.join(n['attrs']),f'text;html=0;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=14;fontSize=17;',0,54,n['w'],len(n['attrs'])*28,n['id'])
    if n['methods']:
     sy=55+len(n['attrs'])*28;vertex(n['id']+'-methods','\n'.join(n['methods']),f'text;html=0;strokeColor=none;fillColor=none;align=left;verticalAlign=top;spacingLeft=14;fontSize=17;',0,sy+13,n['w'],len(n['methods'])*28,n['id']);vertex(n['id']+'-line','',f'shape=line;strokeColor={EDGE};',0,sy,n['w'],1,n['id'])
  for i,e in enumerate(self.edges):
   sa='none';ea='none';kind=e['kind']
   if kind in ['arrow','include']:ea='open'
   if kind=='general':ea='block'
   if kind=='composition':sa='diamond'
   er={'one':'ERmandOne','zeroone':'ERzeroToOne','many':'ERmany','zeromany':'ERzeroToMany','onemany':'ERoneToMany'}
   if kind=='er':sa=er[e['sm']];ea=er[e['tm']]
   style=f'html=0;edgeStyle=none;rounded=0;strokeWidth=2;strokeColor={EDGE};fontSize=16;endArrow={ea};endFill=0;startArrow={sa};startFill={1 if kind=="composition" else 0};exitX={e["source"][0]};exitY={e["source"][1]};exitPerimeter=0;entryX={e["target"][0]};entryY={e["target"][1]};entryPerimeter=0;'+('dashed=1;' if kind=='include' else '')
   c=ET.SubElement(root,'mxCell',id='edge'+str(i),value=e['label'],style=style,edge='1',source=e['a'],target=e['b'],parent='1');geo=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});arr=ET.SubElement(geo,'Array',attrib={'as':'points'})
   for x,y in e['points'][1:-1]:ET.SubElement(arr,'mxPoint',x=str(x),y=str(y))
   if kind!='er':
    for j,(label,t) in enumerate([(e['sm'],-.9),(e['tm'],.9)]):
     if label:
      v=ET.SubElement(root,'mxCell',id=f'edge{i}-label{j}',value=label,style='edgeLabel;html=0;align=center;fontSize=17;',vertex='1',connectable='0',parent='edge'+str(i));gg=ET.SubElement(v,'mxGeometry',x=str(t),y='-1',relative='1',attrib={'as':'geometry'});ET.SubElement(gg,'mxPoint',y='-10',attrib={'as':'offset'})
  for i,(t,x,y,size) in enumerate(self.notes):vertex('note'+str(i),t,'text;html=0;strokeColor=none;fillColor=none;fontSize='+str(size)+';',x-450,y-25,900,35)
  ET.indent(mx);ET.ElementTree(mx).write(ROOT/'diagramas-editables'/f'{self.key}.drawio',encoding='utf-8',xml_declaration=True)

cases={i:n for i,n,_ in MODEL['casos']}
d=D('casos-de-uso','Casos de uso · Operación del hotel',1650,1640)
d.node('limit','Duerme Bien',260,85,1330,1470,'frame');d.node('enc','Encargado',35,600,165,175,'actor')
ys={'CU01':170,'CU03':345,'CU04':520,'CU09':695,'CU11':870,'CU12':1045,'CU06':1280}
for id,y in ys.items():d.node(id,id+'\n'+cases[id],340,y,440,90,'ellipse');d.edge('enc',id,kind='association',source=(.5,.35),target=(0,.5))
d.node('CU05','CU05\n'+cases['CU05'],1070,685,440,90,'ellipse');d.node('CU07','CU07\n'+cases['CU07'],1070,1280,440,90,'ellipse')
for id in ['CU04','CU09','CU11']:d.edge(id,'CU05',label='«include»',kind='include',source=(1,.5),target=(0,.5),labelpos=(900,ys[id]+30))
d.edge('CU06','CU07',label='«include»',kind='include',source=(1,.5),target=(0,.5),labelpos=(925,1305))
# Consulta independiente, además de la operación incluida.
d.edge('enc','CU05',points=[(225,661),(225,285),(1550,285),(1550,730)],kind='association',source=(.5,.35),target=(1,.5))
d.note('Asociación: línea continua. Inclusión: línea discontinua hacia el caso obligatorio.',825,1598)
d=D('casos-de-uso-administracion','Casos de uso · Administración',1320,1020)
d.node('limit','Duerme Bien',420,85,820,850,'frame');d.node('enc','Encargado',115,100,165,175,'actor');d.node('admin','Administrador',115,550,165,175,'actor');d.edge('admin','enc',kind='general',source=(.5,0),target=(.5,1))
for i,id in enumerate(['CU02','CU08','CU10']):
 d.node(id,id+'\n'+cases[id],585,290+i*220,470,95,'ellipse');d.edge('admin',id,kind='association',source=(.5,.35),target=(0,.5))
d.note('Administrador hereda las interacciones de Encargado en esta propuesta de permisos.',660,975)

# Flujos con rutas de validación, rechazo, cancelación y confirmación.
def flow(key,title,steps,branches):
 h=180+len(steps)*165;d=D(key,title,1660,h)
 for i,(id,t,sh) in enumerate(steps):d.node(id,t,450,95+i*165,480,95,sh)
 for i in range(len(steps)-1):
  id=steps[i][0];label='Sí' if steps[i][2]=='diamond' else '';d.edge(id,steps[i+1][0],label=label,labelpos=(720,95+i*165+130))
 for i,(origin,text,back) in enumerate(branches):
  n=d.nodes[origin];side='error'+str(i);d.node(side,text,1090,n['y'],330,95);d.edge(origin,side,label='No',source=(1,.5),target=(0,.5),labelpos=(1010,n['y']+32))
  if back:
   target=d.nodes[back];corridor=1460+i*40;d.edge(side,back,points=[(corridor,n['y']+47.5),(corridor,target['y']-30),(690,target['y']-30)],source=(1,.5),target=(.5,0))
  else:
   d.node(side+'fin','Fin sin cambios',1090,n['y']+125,330,70,'ellipse');d.edge(side,side+'fin')
 return d
flow('flujo-reserva','Registrar reserva · CU09',[
 ('inicio','Inicio','ellipse'),('datos','Capturar titular, habitación,\nfechas y cantidad de pasajeros','input'),('validar','¿Titular registrado y\ndatos completos y válidos?','diamond'),('consultar','Consultar disponibilidad\npara intervalo y capacidad · CU05','rect'),('disponible','¿Habitación disponible\ny capacidad suficiente?','diamond'),('confirmar','¿Confirma la reserva?','diamond'),('guardar','Guardar reserva REGISTRADA','rect'),('respuesta','Mostrar número y resumen\nde reserva registrada','input'),('fin','Fin','ellipse')], [('validar','Mostrar campos\nque requieren corrección','datos'),('disponible','Mostrar conflicto y\notras habitaciones','datos'),('confirmar','Cancelar la operación',None)])
flow('flujo-check-in','Check-in y asignación · CU04',[
 ('inicio','Inicio','ellipse'),('datos','Seleccionar reserva o ingreso directo;\nhabitación, fechas y todos los huéspedes','input'),('origen','¿Sin reserva o reserva\nREGISTRADA?','diamond'),('identificar','Validar huéspedes registrados\ny cantidad de pasajeros','rect'),('validar','¿Fechas y pasajeros válidos,\nsin estadía activa previa?','diamond'),('consulta','Revisar capacidad, reservas\ny ocupación actual · CU05','rect'),('disponible','¿Habitación disponible y\ncapacidad suficiente?','diamond'),('confirmar','¿Confirma el ingreso?','diamond'),('guardar','Crear estadía ACTIVA\ny registrar ESTADIA_HUESPED','rect'),('actualizar','Si hay reserva: pasar a CHECK_IN;\nmostrar habitación OCUPADA','rect'),('respuesta','Mostrar estadía y\nlista de pasajeros asignados','input'),('fin','Fin','ellipse')], [('origen','Informar reserva inválida\no ya utilizada','datos'),('validar','Identificar pasajeros faltantes\no corregir sus datos','datos'),('disponible','Mostrar conflicto; elegir\nfechas o habitación distintas','datos'),('confirmar','Cancelar la operación',None)])
flow('flujo-check-out','Check-out y cuenta · CU06',[
 ('inicio','Inicio','ellipse'),('seleccionar','Seleccionar estadía\ny fecha de salida real','input'),('activa','¿Estadía ACTIVA y\nsalida posterior a entrada?','diamond'),('pasajeros','Recuperar huéspedes asignados\ny parámetros de cobro','rect'),('regla','¿Regla de cobro y\ntarifa válidas y definidas?','diamond'),('cuenta','Calcular costo por pasajero\ny total de cuenta · CU07','rect'),('detalle','Mostrar detalle por huésped,\nperíodo, costos y total','input'),('confirmar','¿Confirma la cuenta\ny la salida?','diamond'),('conflicto','¿Salida sin conflicto con\nreservas posteriores?','diamond'),('guardar','Guardar costo de cada pasajero\ny estadía FINALIZADA','rect'),('liberar','Cerrar reserva asociada, si existe;\nliberar ocupación de habitación','rect'),('fin','Fin','ellipse')], [('activa','Informar estadía\no fecha inválidas','seleccionar'),('regla','Solicitar definición o\ncorrección del cobro','pasajeros'),('confirmar','Mantener estadía ACTIVA',None),('conflicto','Resolver fecha de salida\ny conflicto de reserva','seleccionar')])
# Gestión de reservas: separar las dos operaciones para evitar mezclar sus reglas.
d=D('flujo-gestion-reservas','Modificar o cancelar reserva · CU11 / CU12',1500,1700)
for id,t,x,y,sh in [('inicio','Inicio',525,85,'ellipse'),('select','Seleccionar reserva',525,240,'input'),('estado','¿Reserva REGISTRADA?',525,405,'diamond'),('op','¿Modificar o cancelar?',525,580,'diamond'),('mod','Modificar fechas,\nhabitación o cantidad',120,790,'input'),('disp','Validar datos y disponibilidad',120,950,'rect'),('ok','¿Cambio válido?',120,1110,'diamond'),('save','Guardar cambios',120,1340,'rect'),('cancel','Confirmar cancelación',930,790,'diamond'),('canceled','Marcar CANCELADA;\nliberar disponibilidad',930,1030,'rect'),('fin','Fin',525,1510,'ellipse'),('invalid','Informar que no se puede\nmodificar ni cancelar',1060,400,'rect')]:d.node(id,t,x,y,400,90,sh)
for a,b in [('inicio','select'),('select','estado'),('estado','op'),('mod','disp'),('disp','ok'),('ok','save')]:d.edge(a,b,label='Sí' if a in ['estado','ok'] else '')
d.edge('estado','invalid',source=(1,.5),target=(0,.5),label='No');d.edge('invalid','fin',points=[(1470,445),(1470,1555)],source=(1,.5),target=(1,.5))
d.edge('op','mod',points=[(320,710)],label='Modificar',labelpos=(340,705));d.edge('op','cancel',points=[(1130,710)],label='Cancelar',labelpos=(1120,705))
d.edge('ok','mod',points=[(65,1155),(65,835)],source=(0,.5),target=(0,.5),label='No: corregir',labelpos=(180,1040));d.edge('save','fin',points=[(320,1555)],target=(0,.5));d.edge('cancel','canceled',label='Sí');d.edge('cancel','fin',points=[(1400,835),(1400,1470),(725,1470)],source=(1,.5),target=(.5,0),label='No',labelpos=(1360,900));d.edge('canceled','fin',points=[(1130,1555)],target=(1,.5))

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
 'ROL':['PK id_rol : INTEGER','UQ nombre : VARCHAR(30)'],
 'USUARIO':['PK id_usuario : INTEGER','FK id_rol : INTEGER NOT NULL','UQ nombre_usuario : VARCHAR(50)','hash_clave : VARCHAR(255)','activo : BOOLEAN'],
 'HABITACION':['PK id_habitacion : INTEGER','UQ numero : VARCHAR(20)','capacidad : INTEGER CHECK > 0','orientacion : VARCHAR(30)'],
 'HUESPED':['PK id_huesped : INTEGER','UQ identificacion : VARCHAR(50)','nombres : VARCHAR(100)','apellidos : VARCHAR(100)'],
 'RESERVA':['PK id_reserva : INTEGER','FK id_huesped_titular : INTEGER','FK id_habitacion : INTEGER','fecha_entrada : DATE','fecha_salida : DATE','cantidad_pasajeros : INTEGER > 0','estado : VARCHAR(20)'],
 'ESTADIA':['PK id_estadia : INTEGER','FK id_habitacion : INTEGER','FK/UQ id_reserva : INTEGER NULL','fecha_entrada : DATE','fecha_salida_prevista : DATE','fecha_salida_real : DATE NULL','estado : VARCHAR(20)','noches_cobradas : INTEGER NULL > 0'],
 'ESTADIA_HUESPED':['PK/FK id_estadia : INTEGER','PK/FK id_huesped : INTEGER','tarifa_clp : INTEGER NULL >= 0','costo_clp : INTEGER NULL >= 0']}
layout={'ROL':(75,110),'USUARIO':(800,110),'HABITACION':(1525,110),'HUESPED':(75,690),'RESERVA':(800,690),'ESTADIA':(1525,690),'ESTADIA_HUESPED':(800,1350)}
for key,title,cl in [('diagrama-de-clases','Clases de dominio · Duerme Bien',True),('modelo-de-datos','Modelo lógico de datos · 3FN',False)]:
 d=D(key,title,2200,1810)
 for id,(x,y) in layout.items():
  n,attrs,methods=tables[id];attrs=['- '+v for v in attrs] if cl else dbattrs[id];methods=['+ '+v for v in methods] if cl else [];h=70+(len(attrs)+len(methods))*28;d.node(id,n if cl else id,x,y,490,h,'table',attrs,methods)
 def rel(a,b,source,target,points=None,sm='1',tm='0..*',composition=False):d.edge(a,b,points=points,source=source,target=target,kind='composition' if composition else 'association' if cl else 'er',sm=sm if cl else {'1':'one','0..1':'zeroone'}[sm],tm=tm if cl else {'0..*':'zeromany','1..*':'onemany','0..1':'zeroone'}[tm])
 rel('ROL','USUARIO',(1,.35),(0,.22))
 rel('HABITACION','ESTADIA',(.8,1),(.8,0))
 rel('HABITACION','RESERVA',(0,.25),(.5,0),[(1430,175),(1430,590),(1045,590)])
 rel('HUESPED','RESERVA',(1,.3),(0,.3))
 rel('RESERVA','ESTADIA',(1,.7),(0,.7),sm='0..1',tm='0..1')
 rel('HUESPED','ESTADIA_HUESPED',(.5,1),(0,.5),[(320,1480)])
 rel('ESTADIA','ESTADIA_HUESPED',(.7,1),(1,.5),[(1868,1480)],tm='1..*',composition=cl)
 d.note('Una habitación por reserva y estadía. Los pasajeros se identifican en ESTADIA_HUESPED.',1100,1700)
 d.note('Tarifa y noches: datos históricos del cálculo de demostración; la regla real se valida con el hotel.',1100,1735)
 d.note('Estados reserva: REGISTRADA / CHECK_IN / CANCELADA / FINALIZADA. Estadía: ACTIVA / FINALIZADA.',1100,1770)
for d in ALL:d.save()
(ROOT/'modelo/diagramas.json').write_text(json.dumps([dict(key=d.key,title=d.title,nodes=d.nodes,edges=d.edges) for d in ALL],ensure_ascii=False,indent=2))
