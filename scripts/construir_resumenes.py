from pathlib import Path
import json, math
import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'resumenes';OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def render(pdf,dpi=115):
 doc=fitz.open(ROOT/pdf);page=doc[0];pix=page.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False)
 return Image.frombytes('RGB',(pix.width,pix.height),pix.samples)

def sheet(filename,title,items,cols,cell_w=760,cell_h=940):
 rows=math.ceil(len(items)/cols);pad=34;head=105
 canvas=Image.new('RGB',(pad+(cell_w+pad)*cols,pad+head+(cell_h+pad)*rows),(245,248,249))
 draw=ImageDraw.Draw(canvas);ft=ImageFont.truetype(BOLD,42);fl=ImageFont.truetype(BOLD,27)
 draw.text((pad,pad),title,font=ft,fill=(22,59,80))
 for i,(label,pdf) in enumerate(items):
  r,c=divmod(i,cols);x=pad+c*(cell_w+pad);y=pad+head+r*(cell_h+pad)
  draw.rounded_rectangle((x,y,x+cell_w,y+cell_h),radius=18,fill='white',outline=(205,219,225),width=3)
  draw.text((x+22,y+18),label,font=fl,fill=(22,59,80))
  im=render(pdf);im.thumbnail((cell_w-44,cell_h-90),Image.Resampling.LANCZOS)
  px=x+(cell_w-im.width)//2;py=y+70+(cell_h-80-im.height)//2
  canvas.paste(im,(px,py))
 canvas.save(OUT/filename,optimize=True)

sheet('casos-de-uso.png','Casos de uso',[
 ('Operación','diagramas/casos-de-uso.pdf'),('Administración','diagramas/casos-de-uso-administracion.pdf')],2,760,900)
sheet('procesos.png','Diagramas de procesos',[
 ('Registrar reserva','diagramas/flujo-reserva.pdf'),('Modificar o cancelar','diagramas/flujo-gestion-reservas.pdf'),
 ('Check-in','diagramas/flujo-check-in.pdf'),('Check-out','diagramas/flujo-check-out.pdf')],2,760,1050)
sheet('modelos.png','Modelos del sistema',[
 ('Diagrama de clases','diagramas/diagrama-de-clases.pdf'),('Modelo lógico de datos','diagramas/modelo-de-datos.pdf')],2,760,800)

screens=json.loads((ROOT/'modelo/sistema.json').read_text())['pantallas']
sheet('wireframes.png','Wireframes · 9 pantallas',[(name,f'mockups/wireframe-{key}.pdf') for key,name in screens],3,700,720)
sheet('mockups.png','Mockups · 9 pantallas',[(name,f'mockups/mockup-{key}.pdf') for key,name in screens],3,700,720)
