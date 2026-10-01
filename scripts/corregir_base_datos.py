from pathlib import Path
import json, xml.etree.ElementTree as ET
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'scripts/construir_modelado.py').read_text().split('cases={')[0]
src=src.replace('y+80+i*34,21','y+88+i*42,26')
exec(src)
d=D('modelo-de-datos','Base de datos · Hotel Duerme Bien',1200,3400)
fields={
 'ROL':['PK id_rol: INTEGER','nombre: VARCHAR(30) NOT NULL UNIQUE'],
 'USUARIO':['PK id_usuario: INTEGER','FK id_rol: INTEGER NOT NULL','nombre_usuario: VARCHAR(50) NOT NULL UNIQUE','hash_clave: VARCHAR(255) NOT NULL','activo: BOOLEAN NOT NULL'],
 'HABITACION':['PK id_habitacion: INTEGER','numero: VARCHAR(20) NOT NULL UNIQUE','capacidad: INTEGER NOT NULL, mayor que 0','orientacion: VARCHAR(30) NOT NULL'],
 'HUESPED':['PK id_huesped: INTEGER','identificacion: VARCHAR(50) NOT NULL UNIQUE','nombres: VARCHAR(100) NOT NULL','apellidos: VARCHAR(100) NOT NULL'],
 'RESERVA':['PK id_reserva: INTEGER','FK id_huesped_titular: INTEGER NOT NULL','FK id_habitacion: INTEGER NOT NULL','fecha_entrada: DATE NOT NULL','fecha_salida: DATE NOT NULL, posterior a entrada','cantidad_pasajeros: INTEGER NOT NULL, mayor que 0','estado: REGISTRADA, CHECK_IN o CANCELADA'],
 'ESTADIA':['PK id_estadia: INTEGER','FK id_habitacion: INTEGER NOT NULL','FK id_reserva: INTEGER NULL UNIQUE','fecha_entrada: DATE NOT NULL','fecha_salida_prevista: DATE NOT NULL, posterior a entrada','fecha_salida_real: DATE NULL','estado: ACTIVA o FINALIZADA','noches_cobradas: INTEGER NULL, mayor que 0'],
 'ESTADIA_HUESPED':['PK/FK id_estadia: INTEGER NOT NULL','PK/FK id_huesped: INTEGER NOT NULL','tarifa_clp: INTEGER NULL, mayor o igual a 0','costo_clp: INTEGER NULL, mayor o igual a 0']
}
positions={'ROL':(100,100),'USUARIO':(100,400),'HABITACION':(100,850),'HUESPED':(100,1250),'RESERVA':(100,1700),'ESTADIA':(100,2250),'ESTADIA_HUESPED':(100,2900)}
for name,attrs in fields.items():
 x,y=positions[name];d.node(name,name,x,y,1000,100+len(attrs)*42,'table',attrs=attrs,fill='#f7fafc')
def rel(a,b,sp,tp,points=None,sm='one',tm='zeromany'):
 d.edge(a,b,source=sp,target=tp,points=points,kind='er',sm=sm,tm=tm)
rel('ROL','USUARIO',(.5,1),(.5,0))
rel('HABITACION','RESERVA',(0,.25),(0,.25),[(40,917),(40,1798.5)])
rel('HABITACION','ESTADIA',(1,.25),(1,.25),[(1160,917),(1160,2359)])
rel('HUESPED','RESERVA',(.5,1),(.5,0))
rel('RESERVA','ESTADIA',(.5,1),(.5,0),sm='zeroone',tm='zeroone')
rel('ESTADIA','ESTADIA_HUESPED',(.5,1),(.5,0),tm='onemany')
rel('HUESPED','ESTADIA_HUESPED',(1,.75),(1,.5),[(1185,1451),(1185,3034)])
d.note('PK: clave primaria   ·   FK: clave foránea   ·   UNIQUE: valor único',600,3270,25)
d.note('NULL: dato opcional o pendiente   ·   NOT NULL: dato obligatorio',600,3310,25)
d.note('Una estadía puede iniciar sin reserva; cada pasajero tiene su costo individual.',600,3350,23)
d.save()
# Mantener el editor con la misma tipografía y separación de campos.
p=ROOT/'diagramas-editables/modelo-de-datos.drawio'
t=ET.parse(p)
for cell in t.findall('.//mxCell'):
 if cell.get('id','').endswith('-attrs'):
  cell.set('style',cell.get('style').replace('fontSize=21','fontSize=26'))
  geo=cell.find('mxGeometry');geo.set('y','68');geo.set('height',str(len(cell.get('value','').splitlines())*42))
ET.indent(t);t.write(p,encoding='utf-8',xml_declaration=True)
doc=fitz.open(ROOT/'diagramas/modelo-de-datos.pdf')
pix=doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
Image.frombytes('RGB',(pix.width,pix.height),pix.samples).quantize(colors=128,method=Image.Quantize.MEDIANCUT).save(ROOT/'resumenes/base-de-datos.png',optimize=True)
(ROOT/'modelo/base-de-datos.json').write_text(json.dumps({'entidades':fields,'relaciones':d.edges},ensure_ascii=False,indent=2))
