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
print('Modelado aprobado: CU/RF coherentes, 12 casos representados, decisiones completas, conectores unidos, sin cruces con cajas y 9 interfaces en ambos niveles.')
