from pathlib import Path
import html, json, re, xml.etree.ElementTree as ET
from reportlab.pdfgen import canvas
from reportlab.lib import colors
ROOT=Path(__file__).resolve().parents[1]
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
        self.elements.append(f'<circle cx="{x}" cy="{y}" r="13" fill="white" stroke="#263545"/>')
        self.c.circle(x,self.h-y,13);self.line(x,y+13,x,y+53);self.line(x-23,y+30,x+23,y+30);self.line(x,y+53,x-23,y+82);self.line(x,y+53,x+23,y+82);self.text(x,y+109,label,16)
    def save(self):
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M1,1 L9,5 L1,9" fill="none" stroke="#263545"/></marker></defs><rect width="100%" height="100%" fill="white"/><g font-family="Arial, sans-serif" fill="#182b3b">'+''.join(self.elements)+'</g></svg>'
        (ROOT/'diagramas'/f'{self.name}.svg').write_text(svg);self.c.showPage();self.c.save()


def route(d,points,label='',arrow=False,dashed=False):
 for i,(a,b) in enumerate(zip(points,points[1:])): d.line(*a,*b,dashed=dashed,arrow=arrow and i==len(points)-2)
 if label:
  a,b=points[len(points)//2-1:len(points)//2+1];d.text((a[0]+b[0])/2+20,(a[1]+b[1])/2-12,label,14)

d=Diagram('casos-de-uso',1500,1060)
d.box(250,60,1050,940,[]);d.text(775,100,'Sistema de Pasajeros - Duerme Bien',25,bold=True)
d.actor(105,390,'Encargado');d.actor(1410,780,'Administrador')
cases=[('CU01','Iniciar sesión',650,140),('CU03','Registrar huéspedes',310,280),('CU09','Registrar reserva',310,410),('CU04','Registrar check-in',310,540),('CU06','Registrar check-out',310,670),('CU05','Consultar disponibilidad',850,470),('CU07','Calcular cuenta',850,670),('CU02','Gestionar habitaciones',850,800),('CU10','Gestionar usuarios',850,900),('CU08','Generar informes',310,900)]
for i,n,x,y in cases:d.box(x,y,320,70,[i,n],'ellipse')
for y in [315,445,575,705]:d.line(130,430,310,y)
route(d,[(130,430),(210,430),(210,175),(650,175)])
for y in [835,935]:d.line(1385,820,1170,y)
route(d,[(1385,820),(1330,820),(1330,175),(970,175)])
route(d,[(1385,820),(1330,820),(1330,1030),(190,1030),(190,935),(310,935)])
route(d,[(630,445),(740,445),(740,505),(850,505)],arrow=True,dashed=True);d.text(730,429,'<<include>>',15)
route(d,[(630,575),(780,575),(780,505),(850,505)],arrow=True,dashed=True);d.text(705,600,'<<include>>',15)
d.line(630,705,850,705,'<<include>>',True,True)
d.save()

for name,title,steps in [
 ('flujo-check-in','Check-in',[('Inicio','ellipse'),('Capturar fechas y pasajeros','input'),('¿Datos válidos?','diamond'),('Consultar disponibilidad','rect'),('¿Habitación disponible?','diamond'),('Asignar habitación y huéspedes','rect'),('Guardar estadía activa','rect'),('Fin','ellipse')]),
 ('flujo-reserva','Registro de reserva',[('Inicio','ellipse'),('Capturar titular, fechas y pasajeros','input'),('¿Datos válidos?','diamond'),('Consultar disponibilidad','rect'),('¿Habitación disponible?','diamond'),('Seleccionar habitación','rect'),('Guardar reserva','rect'),('Fin','ellipse')]),
 ('flujo-check-out','Check-out',[('Inicio','ellipse'),('Seleccionar estadía y salida','input'),('¿Estadía activa?','diamond'),('Consultar regla de cobro','rect'),('¿Regla de cobro definida?','diamond'),('Calcular cuenta por pasajero','rect'),('Confirmar salida y liberar habitación','rect'),('Fin','ellipse')])]:
 d=Diagram(name,1000,1200);d.text(470,40,title,26,bold=True)
 for i,(t,shape) in enumerate(steps):
  y=80+i*140;d.box(240,y,460,82,[t],shape)
  if i<7:
   d.line(470,y+82,470,y+140,arrow=True)
   if shape=='diamond':d.text(500,y+111,'Sí',14)
 route(d,[(240,401),(90,401),(90,261),(250,261)],arrow=True);d.text(160,389,'No',14)
 route(d,[(700,681),(850,681),(850,765)],arrow=True);d.text(790,669,'No',14)
 d.box(735,765,230,82,['Fin sin guardar'],'ellipse');d.save()

entities=[('ROL',['id_rol PK','nombre UNIQUE']),('USUARIO',['id_usuario PK','id_rol FK','nombre_usuario UNIQUE','hash_clave']),('HABITACION',['id_habitacion PK','numero UNIQUE','capacidad','orientacion']),('HUESPED',['id_huesped PK','identificacion UNIQUE','nombres','apellidos']),('RESERVA',['id_reserva PK','id_huesped_titular FK','id_habitacion FK','fecha_entrada','fecha_salida','cantidad_pasajeros','estado']),('ESTADIA',['id_estadia PK','id_habitacion FK','id_reserva FK UNIQUE, opcional','fecha_entrada','fecha_salida_prevista','fecha_salida_real, opcional','estado']),('ESTADIA_HUESPED',['id_estadia PK/FK','id_huesped PK/FK','costo_calculado_clp, opcional'])]
d=Diagram('modelo-de-datos',1500,1200);d.text(750,40,'Modelo de datos - 3FN',26,bold=True)
ep={'ROL':(60,80),'USUARIO':(550,80),'HABITACION':(1050,80),'HUESPED':(60,430),'RESERVA':(550,430),'ESTADIA':(1050,430),'ESTADIA_HUESPED':(550,950)}
for n,attrs in entities:
 x,y=ep[n];h=55+len(attrs)*27;d.box(x,y,350,h,[]);d.text(x+175,y+28,n,18,bold=True);d.line(x,y+43,x+350,y+43)
 for i,a in enumerate(attrs):d.text(x+12,y+69+i*27,a,14,'start')
# Las relaciones se trazan por los espacios entre tablas.
d.line(410,125,550,125,'1 : 0..*')
route(d,[(1050,185),(975,185),(975,355),(725,355),(725,430)]);d.text(850,340,'1 : 0..*',14)
d.line(1225,243,1225,430,'1 : 0..*')
d.line(410,490,550,490,'1 : 0..*')
d.line(900,600,1050,600,'0..1 : 0..1')
route(d,[(235,593),(235,1020),(550,1020)]);d.text(390,1003,'1 : 0..*',14)
route(d,[(1225,674),(1225,1020),(900,1020)]);d.text(1070,1003,'1 : 1..*',14)
d.save()

classes=[('Usuario',80,90,['- id: int','- nombreUsuario: String','- hashClave: String'],['+ iniciarSesion()','+ cerrarSesion()']),('Administrador',50,460,[],['+ gestionarUsuarios()','+ gestionarHabitaciones()','+ generarInformes()']),('Encargado',450,460,[],['+ registrarHuesped()','+ registrarCheckIn()','+ registrarCheckOut()','+ gestionarReservas()']),('Huesped',880,90,['- id: int','- identificacion: String','- nombres: String','- apellidos: String'],['+ registrar()','+ actualizarDatos()']),('Habitacion',1450,90,['- id: int','- numero: String','- capacidad: int','- orientacion: String'],['+ consultarDisponibilidad()','+ actualizarDatos()']),('Reserva',880,500,['- id: int','- fechaEntrada: Date','- fechaSalida: Date','- cantidadPasajeros: int','- estado: String'],['+ registrar()','+ modificar()']),('Estadia',1450,500,['- id: int','- fechaEntrada: Date','- fechaSalidaPrevista: Date','- fechaSalidaReal: Date?','- estado: String'],['+ registrarCheckIn()','+ calcularCuenta()','+ registrarCheckOut()']),('EstadiaHuesped',1130,1030,['- costoCalculadoCLP: Decimal?'],['+ calcularCosto(reglaCobro)'])]
d=Diagram('diagrama-de-clases',1900,1250);d.text(950,40,'Diagrama de clases - Duerme Bien',26,bold=True)
for n,x,y,attrs,methods in classes:
 h=58+(len(attrs)+len(methods))*24;d.box(x,y,340,h,[]);d.text(x+170,y+28,n,19,bold=True);d.line(x,y+42,x+340,y+42)
 for i,a in enumerate(attrs):d.text(x+12,y+65+i*24,a,15,'start')
 sy=y+50+len(attrs)*24;d.line(x,sy,x+340,sy)
 for i,a in enumerate(methods):d.text(x+12,sy+24+i*24,a,15,'start')
# Generalización con una unión común y triángulo hueco hacia Usuario.
route(d,[(220,460),(220,365),(620,365),(620,460)])
d.line(250,365,250,282)
d.elements.append('<polygon points="250,268 239,284 261,284" fill="white" stroke="#263545"/>')
p=d.c.beginPath();p.moveTo(250,d.h-268);p.lineTo(239,d.h-284);p.lineTo(261,d.h-284);p.close();d.c.setFillColor(colors.white);d.c.drawPath(p,fill=1);d.c.setFillColor(colors.HexColor('#182b3b'))
d.line(1050,292,1050,500,'1 titular / 0..*')
d.line(1620,292,1620,500,'1 / 0..*')
route(d,[(1450,205),(1350,205),(1350,410),(1200,410),(1200,500)]);d.text(1300,394,'1 / 0..*',14)
d.line(1220,700,1450,700,'0..1 / 0..1')
route(d,[(880,205),(830,205),(830,1100),(1130,1100)]);d.text(990,1080,'1 / 0..*',14)
route(d,[(1620,774),(1620,1090),(1470,1090)]);d.text(1560,1070,'1 / 1..*',14)
d.elements.append('<polygon points="1620,750 1611,762 1620,774 1629,762" fill="#263545"/>')
p=d.c.beginPath();p.moveTo(1620,d.h-750);p.lineTo(1611,d.h-762);p.lineTo(1620,d.h-774);p.lineTo(1629,d.h-762);p.close();d.c.setFillColor(colors.HexColor('#263545'));d.c.drawPath(p,fill=1)
d.save()

# Archivos editables: conservar símbolos, líneas y puntas de flecha.
for file in (ROOT/'diagramas').glob('*.svg'):
 svg=ET.parse(file).getroot();mx=ET.Element('mxfile',host='app.diagrams.net');dia=ET.SubElement(mx,'diagram',name=file.stem);model=ET.SubElement(dia,'mxGraphModel',page='1',pageWidth=svg.get('width'),pageHeight=svg.get('height'),grid='1',gridSize='10');root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0');idx=2
 def cell(value,style,x,y,w,h):
  global idx
  c=ET.SubElement(root,'mxCell',id=str(idx),value=value,style=style,vertex='1',parent='1');idx+=1;ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'});return c
 for e in svg.find('{http://www.w3.org/2000/svg}g').iter():
  tag=e.tag.split('}')[-1];style='html=0;strokeColor=#263545;fillColor='+e.get('fill','#ffffff')+';'
  if tag=='rect' and e.get('width')!='100%':cell('',style+'shape=rectangle;',float(e.get('x',0)),float(e.get('y',0)),float(e.get('width')),float(e.get('height')))
  elif tag in ('ellipse','circle'):
   rx=float(e.get('rx',e.get('r',0)));ry=float(e.get('ry',e.get('r',0)));cell('',style+'shape=ellipse;',float(e.get('cx'))-rx,float(e.get('cy'))-ry,2*rx,2*ry)
  elif tag=='polygon':
   pts=[tuple(map(float,v.split(','))) for v in e.get('points').split()];xs,ys=zip(*pts);x,y,w,h=min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)
   shape='triangle;direction=north;' if len(pts)==3 else ('parallelogram;fixedSize=1;size=20;' if pts[0][1]==pts[1][1] else 'rhombus;')
   cell('',style+'shape='+shape,x,y,w,h)
  elif tag=='text':
   size=float(e.get('font-size',15));t=''.join(e.itertext());w=max(40,len(t)*size*.6);x=float(e.get('x'));y=float(e.get('y'));anchor=e.get('text-anchor','middle');x=x-w/2 if anchor=='middle' else x
   cell(t,'text;html=0;whiteSpace=wrap;strokeColor=none;fillColor=none;align='+('center' if anchor=='middle' else 'left')+';fontSize='+str(size)+';fontStyle='+('1' if e.get('font-weight')=='bold' else '0')+';',x,y-size,w,size*1.4)
  elif tag=='path' and e.get('d','').startswith('M') and e.get('stroke'):
   d=e.get('d');tokens=re.findall(r'[MLHV]|-?\d+(?:\.\d+)?',d);pts=[];i=0;cur=(0,0)
   while i<len(tokens):
    cmd=tokens[i];i+=1
    if cmd in ('M','L'):cur=(float(tokens[i]),float(tokens[i+1]));i+=2
    elif cmd=='H':cur=(float(tokens[i]),cur[1]);i+=1
    elif cmd=='V':cur=(cur[0],float(tokens[i]));i+=1
    pts.append(cur)
   # Actor strokes have separate M commands; preserve each subpath.
   for a,b in zip(pts,pts[1:]):
    c=ET.SubElement(root,'mxCell',id=str(idx),edge='1',parent='1',style='html=0;strokeColor=#263545;endArrow='+('open' if e.get('marker-end') else 'none')+';'+('dashed=1;' if e.get('stroke-dasharray') else ''));idx+=1;g=ET.SubElement(c,'mxGeometry',relative='1',attrib={'as':'geometry'});ET.SubElement(g,'mxPoint',x=str(a[0]),y=str(a[1]),attrib={'as':'sourcePoint'});ET.SubElement(g,'mxPoint',x=str(b[0]),y=str(b[1]),attrib={'as':'targetPoint'})
 ET.indent(mx);ET.ElementTree(mx).write(ROOT/'diagramas-editables'/f'{file.stem}.drawio',encoding='utf-8',xml_declaration=True)

# Actualizar el informe con los diagramas revisados.
import fitz
out=fitz.open(ROOT/'informe/requerimientos-y-modelado.pdf')
for name in ['casos-de-uso','flujo-check-in','flujo-check-out','flujo-reserva','diagrama-de-clases','modelo-de-datos']:
 src=fitz.open(ROOT/'diagramas'/f'{name}.pdf');page=out.new_page(width=595,height=842);page.insert_text((40,40),name.replace('-',' ').title(),fontsize=17);page.show_pdf_page(fitz.Rect(30,70,565,790),src,0);src.close()
out.save(ROOT/'informe/informe-con-diagramas.pdf');out.close()
