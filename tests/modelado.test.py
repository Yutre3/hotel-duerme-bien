"""Comprobar incoherencias reales entre RF, CU, diagramas y archivos editables."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
r=Path(__file__).resolve().parents[1]
model=json.loads((r/'modelo/sistema.json').read_text());scenes=json.loads((r/'modelo/diagramas.json').read_text());trace=json.loads((r/'modelo/trazabilidad.json').read_text())
canonical={id:name for id,name,rf in model['casos']}
assert canonical['CU08']=='Gestionar usuarios' and canonical['CU10']=='Generar informes'
seen={}
for d in scenes:
 for id,n in d['nodes'].items():
  if id.startswith('CU'):
   assert n['label'].split('\n',1)[1]==canonical[id],(id,n['label'])
   seen[id]=True
  if n['shape']=='diamond':assert len([e for e in d['edges'] if e['a']==id])==2,(d['key'],id)
 for e in d['edges']:
  assert e['a'] in d['nodes'] and e['b'] in d['nodes']
  for n in d['nodes'].values():
   if n['id'] in [e['a'],e['b']] or n['shape'] in ['frame','actor']:continue
   for a,b in zip(e['points'],e['points'][1:]):
    for i in range(1,100):
     t=i/100;x=a[0]+t*(b[0]-a[0]);y=a[1]+t*(b[1]-a[1])
     assert not(n['x']+2<x<n['x']+n['w']-2 and n['y']+2<y<n['y']+n['h']-2),(d['key'],e['a'],e['b'],n['id'])
 tree=ET.parse(r/'diagramas-editables'/f'{d["key"]}.drawio')
 for edge in tree.findall('.//mxCell[@edge="1"]'):assert edge.get('source') and edge.get('target')
assert set(canonical)==set(seen),'Caso de uso sin diagrama'
assert len(trace)==9
for rf in trace:
 assert all(c.strip() in canonical for c in rf['casos'].split(','))
for key,name in model['pantallas']:
 for mode in ['wireframe','mockup']:
  for ext in ['svg','pdf']:assert (r/'mockups'/f'{mode}-{key}.{ext}').stat().st_size>0
  ET.parse(r/'diagramas-editables'/f'{mode}-{key}.drawio')
assert len(ET.parse(r/'diagramas-editables/interfaces.drawio').findall('diagram'))==19

# Las imágenes publicadas en el README deben ser PNG completos. Un archivo
# truncado puede conservar su cabecera y dimensiones, pero GitHub sólo muestra
# la parte anterior al corte.
png_end=b'\x00\x00\x00\x00IEND\xaeB`\x82'
for filename in ['casos-de-uso.png','procesos.png','clases.png','base-de-datos.png','wireframe.png','mockup.png']:
 data=(r/'resumenes'/filename).read_bytes()
 assert data.startswith(b'\x89PNG\r\n\x1a\n'),filename+' no tiene cabecera PNG'
 assert data.endswith(png_end),filename+' está truncado'

# El modelo conceptual usa herencia para los dos perfiles. ROL pertenece al
# modelo relacional y no se duplica como clase junto a Administrador/Encargado.
class_scene=next(d for d in scenes if d['key']=='diagrama-de-clases')
expected_classes={'USUARIO','ADMIN','ENCARGADO','INFORME','HUESPED','RESERVA','HABITACION','ESTADIA','ESTADIA_HUESPED'}
assert set(class_scene['nodes'])==expected_classes,(set(class_scene['nodes']),expected_classes)
assert 'ROL' not in class_scene['nodes'],'Rol duplica la herencia de Administrador y Encargado'
assert any({e['a'],e['b']}=={'ADMIN','INFORME'} for e in class_scene['edges']),'Falta relación Administrador-Informe'
for edge in class_scene['edges']:
 if edge['kind']!='general':
  assert edge['label'].strip(),(edge['a'],edge['b'],'relación sin verbo')
all_class_text=' '.join(n['label']+' '+' '.join(n['attrs'])+' '+' '.join(n['methods']) for n in class_scene['nodes'].values())
assert ': Sesion' not in all_class_text,'Tipo Sesion usado sin clase definida'
# Ningún conector del diagrama de clases debe escapar por el borde de la
# página ni usar recorridos tan largos que separen visualmente la relación.
for edge in class_scene['edges']:
 for x,y in edge['points'][1:-1]:
  assert x >= 40,(edge['a'],edge['b'],'conector pegado al borde')
 for (x1,y1),(x2,y2) in zip(edge['points'],edge['points'][1:]):
  assert max(abs(x2-x1),abs(y2-y1)) <= 900,(edge['a'],edge['b'],'tramo demasiado largo')

# Las siete entidades requeridas y sus restricciones esenciales deben quedar
# visibles en la fuente que genera el diagrama de base de datos.
db=json.loads((r/'modelo/base-de-datos.json').read_text())['entidades']
assert set(db)=={'ROL','USUARIO','HABITACION','HUESPED','RESERVA','ESTADIA','ESTADIA_HUESPED'}
assert any('fecha_salida > fecha_entrada' in x for x in db['RESERVA'])
assert any('REGISTRADA' in x and 'CANCELADA' in x for x in db['RESERVA'])
assert any('ACTIVA' in x and 'FINALIZADA' in x for x in db['ESTADIA'])
print('Modelado aprobado: CU/RF coherentes, 12 casos representados, decisiones completas, conectores unidos, sin cruces con cajas y 9 interfaces en ambos niveles.')
