from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'scripts/construir_modelado.py').read_text();exec(s[:s.index('cases={')])
# La misma navegación y los mismos datos del prototipo; ejemplos ficticios.
F={
'acceso':(['Usuario de demostración\nadmin_demo','Perfil asignado\nAdministrador'],'Entrar', ['Seleccionar un usuario activo.','Los permisos se toman del perfil; no se edita el rol al ingresar.']),
'disponibilidad':(['Entrada\n01/10/2026','Salida\n03/10/2026','Cantidad de pasajeros\n2'],'Consultar disponibilidad',['Habitación | Capacidad | Orientación | Disponibilidad','201               2                 Norte             Disponible','305               3                 Este              Disponible']),
'habitaciones':(['Número\n201','Capacidad\n2','Orientación\nNorte'],'Guardar habitación',['Número | Capacidad | Orientación | Estado actual | Acción','201            2                Norte            Disponible         Editar','202            2                Sur               Ocupada            Editar']),
'huespedes':(['Identificación\nDEMO-01','Nombres\nAna','Apellidos\nEjemplo'],'Guardar huésped',['Identificación | Nombres | Apellidos','DEMO-01            Ana            Ejemplo','DEMO-02            Luis             Ejemplo']),
'reservas':(['Titular\nAna Ejemplo','Habitación\n201 · Capacidad 2','Entrada\n01/10/2026','Salida\n03/10/2026','Cantidad de pasajeros\n2'],'Guardar reserva',['Reserva | Titular | Habitación | Fechas | Pasajeros | Estado | Acciones','#1     Ana Ejemplo     201    01/10–03/10     2     REGISTRADA    Modificar / Cancelar']),
'checkin':(['Origen\nReserva #1 / Sin reserva','Habitación\n201 · Capacidad 2','Entrada\n01/10/2026','Salida prevista\n03/10/2026','Pasajeros identificados\n[x] Ana Ejemplo · DEMO-01','Pasajeros identificados\n[x] Luis Ejemplo · DEMO-02'],'Confirmar check-in',['Estadía | Habitación | Pasajeros | Entrada | Salida prevista | Estado','#1     201      Ana Ejemplo / Luis Ejemplo      01/10–03/10      ACTIVA']),
'checkout':(['Estadía activa\n#1 · Habitación 201','Fecha de salida real\n03/10/2026','Tarifa de prueba por pasajero/noche (CLP)\n10.000','Cuenta revisada\n[x] Confirmar cuenta y salida'],'Confirmar check-out',['Pasajero | Noches | Tarifa de prueba CLP | Costo CLP','Ana Ejemplo        2                $10.000                $20.000','Luis Ejemplo         2                $10.000                $20.000','TOTAL                                                           $40.000']),
'informes':(['Desde\n01/10/2026','Hasta (exclusiva)\n03/10/2026'],'Generar informes',['Ocupación: Estadía | Hab. | Entrada | Salida | Pasajeros | Estado','#1                  201      01/10–03/10          2           ACTIVA','Reservas: Reserva | Titular | Hab. | Entrada | Salida | Estado','#1        Ana Ejemplo     201     01/10–03/10     CHECK_IN']),
'usuarios':(['Nombre de usuario\nencargado_demo','Perfil\nEncargado','Estado del usuario\n[x] Activo'],'Guardar usuario',['Usuario | Perfil | Estado | Acción','admin_demo                  Administrador          Activo         Editar','encargado_demo          Encargado                 Activo         Editar'])}
GRID={
 'acceso':([],[]),
 'disponibilidad':(['Habitación','Capacidad','Orientación','Disponibilidad'],[['201','2','Norte','Disponible'],['305','3','Este','Disponible']]),
 'habitaciones':(['Número','Capacidad','Orientación','Estado','Acción'],[['201','2','Norte','Disponible','Editar'],['202','2','Sur','Ocupada','Editar']]),
 'huespedes':(['Identificación','Nombres','Apellidos'],[['DEMO-01','Ana','Ejemplo'],['DEMO-02','Luis','Ejemplo']]),
 'reservas':(['Reserva','Titular','Habitación','Fechas','Pasajeros','Estado','Acciones'],[['#1','Ana Ejemplo','201','01/10/2026 – 03/10/2026','2','REGISTRADA','Modificar / Cancelar']]),
 'checkin':(['Estadía','Habitación','Pasajeros','Entrada','Salida prevista','Estado'],[['#1','201','Ana Ejemplo / Luis Ejemplo','01/10/2026','03/10/2026','ACTIVA']]),
 'checkout':(['Pasajero','Noches','Tarifa CLP','Costo CLP'],[['Ana Ejemplo','2','$10.000','$20.000'],['Luis Ejemplo','2','$10.000','$20.000'],['TOTAL','','','$40.000']]),
 'informes':(['Informe','Registro','Hab.','Fechas','Pasajeros','Estado'],[['Ocupación','Estadía #1','201','01/10 – 03/10','2','ACTIVA'],['Reservas','Reserva #1','201','01/10 – 03/10','2','CHECK_IN']]),
 'usuarios':(['Usuario','Perfil','Estado','Acción'],[['admin_demo','Administrador','Activo','Editar'],['encargado_demo','Encargado','Activo','Editar']])}
import textwrap
assets=[]
for mode in ['wireframe','mockup']:
 for key,name in MODEL['pantallas']:
  d=D(mode+'-'+key,('Wireframe' if mode=='wireframe' else 'Mockup')+' · '+name,1500,1190)
  accent='#eef1f3' if mode=='wireframe' else '#d9eaf1'
  d.node('header','Hotel Duerme Bien · Sistema de pasajeros',35,75,1430,80,fill=accent if mode=='wireframe' else BLUE)
  if mode=='mockup':d.nodes['header']['color']=WHITE;d.nodes['header']['bold']=True
  for i,(k,n) in enumerate(MODEL['pantallas']):
   d.node('nav-'+k,n,35,185+i*84,240,65,shape='rounded' if mode=='mockup' else 'rect',fill=accent if k==key else WHITE)
   if k==key:d.nodes['nav-'+k]['bold']=True
  d.node('title',name,315,175,1140,65,shape='caption' if mode=='mockup' else 'rect',fill=accent);d.nodes['title']['bold']=True
  fields,button,rows=F[key]
  for i,t in enumerate(fields):
   x=335+(i%2)*570;y=265+(i//2)*115
   if mode=='wireframe':d.node('field'+str(i),t.split('\n')[0]+'\n[ campo / selección ]',x,y,535,90,'rect')
   else:
    label,value=t.split('\n',1);d.node('label'+str(i),label,x,y,535,30,'caption');d.node('field'+str(i),value,x,y+35,535,50,'control')
  y=265+math.ceil(len(fields)/2)*115
  shape='rounded' if mode=='mockup' else 'rect';fill=BLUE if mode=='mockup' else accent
  if key=='checkout':d.node('quote','Calcular cuenta',335,y,360,65,shape,fill=fill);d.node('submit',button,920,y,520,65,shape,fill=fill)
  else:d.node('submit',button,335,y,535,65,shape,fill=fill)
  if mode=='mockup':
   d.nodes['submit']['color']=WHITE;d.nodes['submit']['bold']=True
   if key=='checkout':d.nodes['quote']['color']=WHITE
  y+=105
  if mode=='wireframe':d.node('result','Cuenta por pasajero' if key=='checkout' else 'Resultados / registros',315,y,1140,70+len(rows)*28,'table',attrs=[rows[0]]+['[ registro / resultado ]']*(len(rows)-1))
  else:
   heads,values=GRID[key]
   if heads:
    cw=1140/len(heads)
    for row,values_row in enumerate([heads]+values):
     for col,value in enumerate(values_row):
      content='\n'.join(textwrap.wrap(value,width=max(10,int(cw/11))))
      d.node(f'table-{row}-{col}',content,315+col*cw,y+row*80,cw,80,fill=accent if row==0 else WHITE)
      if row==0:d.nodes[f'table-{row}-{col}']['bold']=True
  d.note('Datos ficticios para el diseño. Las decisiones de permisos y cobro se detallan en el informe.',880,1145,16)
  d.save();assets.append(d.key)
  for ext in ['svg','pdf']:(ROOT/'diagramas'/f'{d.key}.{ext}').replace(ROOT/'mockups'/f'{d.key}.{ext}')
d=D('sketch','Sketch · Distribución inicial de la interfaz',1200,900)
d.node('header','Hotel Duerme Bien',40,90,1120,80)
d.node('nav','NAVEGACIÓN\nAcceso\nDisponibilidad\nHabitaciones\nHuéspedes\nReservas\nCheck-in\nCheck-out\nInformes\nUsuarios',40,200,250,570)
for i,t in enumerate(['Habitaciones','Ocupación','Disponibilidad']):d.node('card'+str(i),t,330+i*275,200,245,100)
d.node('form','ÁREA DE TRABAJO\nCampos del proceso seleccionado',330,350,830,170)
d.node('actions','Consultar / Guardar / Confirmar',330,565,830,70)
d.node('list','LISTADO O RESULTADO\nRegistros, estados y acciones',330,680,830,130);d.save()
for ext in ['svg','pdf']:(ROOT/'diagramas'/f'sketch.{ext}').replace(ROOT/'mockups'/f'sketch.{ext}')
# Un archivo con todas las vistas para editar sin recrearlas.
bundle=ET.Element('mxfile',host='app.diagrams.net')
for key in ['sketch']+assets:bundle.append(ET.parse(ROOT/'diagramas-editables'/f'{key}.drawio').getroot().find('diagram'))
ET.indent(bundle);ET.ElementTree(bundle).write(ROOT/'diagramas-editables/interfaces.drawio',encoding='utf-8',xml_declaration=True)
(ROOT/'mockups/assets.json').write_text(json.dumps(assets,ensure_ascii=False))
# Galería completa: cambiar entre estructura y diseño; cada vista tiene su enlace de edición.
links=lambda key:'https://app.diagrams.net/?mode=device#Uhttps%3A%2F%2Fraw.githubusercontent.com%2FYutre3%2Fhotel-duerme-bien%2Fmain%2Fdiagramas-editables%2F'+key+'.drawio'
buttons=''.join(f'<button data-page="{k}">{n}</button>' for k,n in MODEL['pantallas'])
script="""const names=Object.fromEntries(PAGES);let page='acceso',mode='mockup';function show(){document.querySelector('#screen').src=mode+'-'+page+'.svg';document.querySelector('#screen').alt=names[page];document.querySelector('#edit').href=EDIT+mode+'-'+page+'.drawio';document.querySelector('#pdf').href=mode+'-'+page+'.pdf';document.querySelectorAll('[data-page]').forEach(b=>b.setAttribute('aria-current',b.dataset.page===page?'page':'false'));document.querySelector('#toggle').textContent=mode==='mockup'?'Ver wireframe':'Ver mockup';document.querySelector('#heading').textContent=names[page]}document.querySelectorAll('[data-page]').forEach(b=>b.onclick=()=>{page=b.dataset.page;show()});document.querySelector('#toggle').onclick=()=>{mode=mode==='mockup'?'wireframe':'mockup';show()};show();"""
script=script.replace('PAGES',json.dumps(MODEL['pantallas'],ensure_ascii=False)).replace('EDIT',json.dumps(links('')[:-7]))
page='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Duerme Bien · Wireframes y mockups</title><style>body{font-family:Arial,sans-serif;margin:30px auto;max-width:1300px;padding:0 20px;color:#163b50}nav{display:flex;gap:10px;flex-wrap:wrap}button,a{padding:10px;font:inherit}button[aria-current=page]{background:#163b50;color:white}img{max-width:100%;border:1px solid #d9e3e9}a{color:#126479}.tools{display:flex;align-items:center;gap:20px;flex-wrap:wrap}</style></head><body><h1>Wireframes y mockups · Duerme Bien</h1><nav>'''+buttons+'''</nav><div class="tools"><h2 id="heading"></h2><button id="toggle">Ver wireframe</button><a id="edit" target="_blank" rel="noopener">Editar en diagrams.net</a><a id="pdf">PDF</a><a href="../prototipo/">Abrir prototipo</a></div><img id="screen"><script>'''+script+'''</script></body></html>'''
(ROOT/'mockups/index.html').write_text(page)
