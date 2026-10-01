from pathlib import Path
import json, xml.etree.ElementTree as ET
import fitz
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'scripts/construir_modelado.py').read_text().split('cases={')[0]
src=src.replace('y+72+i*28,17','y+82+i*36,22')
exec(src)
d=D('modelo-de-datos','Base de datos · Hotel Duerme Bien',1580,2240)
fields={
 'ROL':['PK id_rol: INTEGER','nombre: VARCHAR(30) NOT NULL UNIQUE'],
 'USUARIO':['PK id_usuario: INTEGER','FK id_rol: INTEGER NOT NULL','nombre_usuario: VARCHAR(50) NOT NULL UNIQUE','hash_clave: VARCHAR(255) NOT NULL','activo: BOOLEAN NOT NULL'],
 'HABITACION':['PK id_habitacion: INTEGER','numero: VARCHAR(20) NOT NULL UNIQUE','capacidad: INTEGER NOT NULL, mayor que 0','orientacion: VARCHAR(30) NOT NULL'],
 'HUESPED':['PK id_huesped: INTEGER','identificacion: VARCHAR(50) NOT NULL UNIQUE','nombres: VARCHAR(100) NOT NULL','apellidos: VARCHAR(100) NOT NULL'],
 'RESERVA':['PK id_reserva: INTEGER','FK id_huesped_titular: INTEGER NOT NULL','FK id_habitacion: INTEGER NOT NULL','fecha_entrada: DATE NOT NULL','fecha_salida: DATE NOT NULL','cantidad_pasajeros: INTEGER NOT NULL, > 0','estado: VARCHAR(20) NOT NULL'],
 'ESTADIA':['PK id_estadia: INTEGER','FK id_habitacion: INTEGER NOT NULL','FK id_reserva: INTEGER NULL UNIQUE','fecha_entrada: DATE NOT NULL','fecha_salida_prevista: DATE NOT NULL','fecha_salida_real: DATE NULL','estado: VARCHAR(20) NOT NULL','noches_cobradas: INTEGER NULL, > 0'],
 'ESTADIA_HUESPED':['PK/FK id_estadia: INTEGER NOT NULL','PK/FK id_huesped: INTEGER NOT NULL','tarifa_clp: INTEGER NULL, mayor o igual a 0','costo_clp: INTEGER NULL, mayor o igual a 0']
}
positions={'ROL':(60,100),'USUARIO':(880,100),'HABITACION':(60,480),'HUESPED':(880,480),'RESERVA':(60,970),'ESTADIA':(880,970),'ESTADIA_HUESPED':(470,1690)}
for name,attrs in fields.items():
 x,y=positions[name];d.node(name,name,x,y,640,90+len(attrs)*36,'table',attrs=attrs,fill='#f7fafc')
def rel(a,b,sp,tp,points=None,sm='one',tm='zeromany'):
 d.edge(a,b,source=sp,target=tp,points=points,kind='er',sm=sm,tm=tm)
rel('ROL','USUARIO',(1,.5),(0,.25))
rel('HABITACION','RESERVA',(.35,1),(.35,0))
rel('HABITACION','ESTADIA',(1,.2),(0,.2),[(785,527),(785,1062)])
rel('HUESPED','RESERVA',(0,.8),(1,.18),[(815,667),(815,1032)])
rel('RESERVA','ESTADIA',(1,.65),(0,.65),sm='zeroone',tm='zeroone')
rel('ESTADIA','ESTADIA_HUESPED',(.55,1),(1,.65),[(1232,1580),(1190,1580),(1190,1842)],tm='onemany')
rel('HUESPED','ESTADIA_HUESPED',(1,.55),(.75,0),[(1545,609),(1545,1620),(950,1620)])
d.note('PK: clave primaria   ·   FK: clave foránea   ·   UNIQUE: valor único',790,2050,23)
d.note('NULL: dato opcional o pendiente   ·   NOT NULL: dato obligatorio',790,2090,23)
d.note('Una estadía puede iniciar sin reserva; cada pasajero tiene su costo individual.',790,2130,21)
d.save()
# Mantener el editor con la misma tipografía y separación de campos.
p=ROOT/'diagramas-editables/modelo-de-datos.drawio'
t=ET.parse(p)
for cell in t.findall('.//mxCell'):
 if cell.get('id','').endswith('-attrs'):
  cell.set('style',cell.get('style').replace('fontSize=17','fontSize=22'))
  geo=cell.find('mxGeometry');geo.set('y','62');geo.set('height',str(len(cell.get('value','').splitlines())*36))
ET.indent(t);t.write(p,encoding='utf-8',xml_declaration=True)
doc=fitz.open(ROOT/'diagramas/modelo-de-datos.pdf')
pix=doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(ROOT/'resumenes/base-de-datos.png')
(ROOT/'modelo/base-de-datos.json').write_text(json.dumps({'entidades':fields,'relaciones':d.edges},ensure_ascii=False,indent=2))
