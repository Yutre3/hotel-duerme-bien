from pathlib import Path
import xml.etree.ElementTree as ET
import html
ROOT=Path(__file__).resolve().parents[1]
screens={'Acceso':(['Usuario de prueba','Perfil de prueba'],'Entrar a la maqueta'),'Disponibilidad':(['Entrada','Salida','Cantidad de pasajeros'],'Consultar'),'Habitaciones':(['Número de habitación','Capacidad','Orientación'],'Simular guardado'),'Huéspedes':(['Identificación','Nombres','Apellidos'],'Simular registro'),'Reservas':(['Titular de ejemplo','Habitación de ejemplo','Entrada','Salida','Pasajeros'],'Simular reserva'),'Check-in':(['Reserva de origen','Habitación de ejemplo','Entrada','Salida','Pasajeros','Identificación del huésped'],'Simular check-in'),'Check-out':(['Estadía de ejemplo','Pasajeros de prueba','Tarifa por pasajero y noche (CLP)','Noches de prueba'],'Simular cálculo'),'Informes':(['Tipo de informe','Fecha de referencia'],'Consultar ejemplo'),'Usuarios':(['Nombre de usuario','Perfil'],'Simular asignación')}
mx=ET.Element('mxfile',host='app.diagrams.net')
for mode in ['Wireframe','Mockup']:
 for name,(fields,button) in screens.items():
  dia=ET.SubElement(mx,'diagram',name=f'{mode} · {name}');model=ET.SubElement(dia,'mxGraphModel',page='1',pageWidth='1100',pageHeight='800');root=ET.SubElement(model,'root');ET.SubElement(root,'mxCell',id='0');ET.SubElement(root,'mxCell',id='1',parent='0');idx=2;parts=[];accent='#333333' if mode=='Wireframe' else '#15394d'
  def box(t,x,y,w,h,fill='#ffffff',color='#19374b',border='#a7bcc6',size=16):
   global idx
   c=ET.SubElement(root,'mxCell',id=str(idx),value=t,style=f'html=0;whiteSpace=wrap;rounded=0;fillColor={fill};fontColor={color};strokeColor={border};fontSize={size};',vertex='1',parent='1');idx+=1;ET.SubElement(c,'mxGeometry',x=str(x),y=str(y),width=str(w),height=str(h),attrib={'as':'geometry'})
   parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{border}"/><text x="{x+w/2}" y="{y+h/2+6}" text-anchor="middle" fill="{color}" font-size="{size}">{html.escape(t)}</text>')
  box('Duerme Bien',0,0,1100,85,accent,'#ffffff',accent,24)
  for i,n in enumerate(screens):box(n,15,110+i*57,195,47,'#e3f0f3' if n==name else '#ffffff')
  box(name,250,110,800,50,border='#ffffff',size=26)
  for i,f in enumerate(fields):
   x=265+(i%2)*400;y=200+(i//2)*125;box(f,x,y,365,35,border='#ffffff',size=14);box('',x,y+40,365,50)
  box(button,265,200+((len(fields)+1)//2)*125,365,50,accent,'#ffffff',accent)
  if name=='Acceso':
   (ROOT/'mockups'/f'{mode.lower()}.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="800" viewBox="0 0 1100 800"><rect width="1100" height="800" fill="white"/><g font-family="Arial,sans-serif">'+''.join(parts)+'</g></svg>')
ET.indent(mx);ET.ElementTree(mx).write(ROOT/'diagramas-editables/interfaces.drawio',encoding='utf-8',xml_declaration=True)
