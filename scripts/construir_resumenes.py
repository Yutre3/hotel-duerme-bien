from pathlib import Path
import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'resumenes'
OUT.mkdir(exist_ok=True)

# Reutiliza el generador SVG/PDF/drawio del proyecto.
source = (ROOT / 'scripts/construir_modelado.py').read_text()
exec(source[:source.index('cases={')])


def png_from_pdf(pdf, output, dpi=150):
    doc = fitz.open(ROOT / pdf)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
    image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
    # Mantener RGB evita archivos de paleta truncados en imágenes UML grandes
    # y asegura que GitHub y los navegadores móviles puedan mostrarlos.
    image.save(OUT / output, format='PNG', optimize=True, compress_level=9)


# 1. Un único UML completo. Cada actor usa una zona propia y ninguna
# asociación atraviesa un óvalo. También se muestran include, extend y
# generalización, como pide la pauta de evaluación.
cases = {i: n for i, n, _ in MODEL['casos']}
d = D('sistema-casos-de-uso', 'Casos de uso completos · Hotel Duerme Bien', 2600, 2200)
d.node('system', 'Sistema de pasajeros', 420, 80, 2080, 2020, 'frame')
d.node('enc', 'Encargado', 90, 600, 180, 175, 'actor')
d.node('admin', 'Administrador', 90, 1680, 180, 175, 'actor')
d.edge('admin', 'enc', kind='general', source=(.5, 0), target=(.5, 1),
       points=[(180, 1500), (180, 930)])

operation_cases = [
    ('CU01', 150), ('CU03', 340), ('CU04', 530),
    ('CU09', 850), ('CU11', 1040), ('CU12', 1230), ('CU06', 1420)
]
for index, (case_id, y) in enumerate(operation_cases):
    d.node(case_id, case_id + '\n' + cases[case_id], 560, y, 590, 105, 'ellipse')
    d.edge('enc', case_id, kind='association',
           source=(1, .10 + index * .12), target=(0, .5))

# Flujo opcional válido de CU04: se usa solamente cuando no existe reserva.
d.node('EXT01', 'Ingreso directo\n(sin reserva)', 1430, 530, 540, 105, 'ellipse')
d.edge('EXT01', 'CU04', label='«extend» [sin reserva]', kind='include',
       source=(0, .5), target=(1, .5), labelpos=(1290, 535))

d.node('CU05', 'CU05\n' + cases['CU05'], 1570, 865, 590, 105, 'ellipse')
d.node('CU07', 'CU07\n' + cases['CU07'], 1570, 1420, 590, 105, 'ellipse')
d.edge('CU04', 'CU05', points=[(1270, 582), (1270, 895)],
       label='«include»', kind='include', source=(1, .5), target=(0, .25), labelpos=(1370, 785))
d.edge('CU09', 'CU05', label='«include»', kind='include',
       source=(1, .5), target=(0, .5), labelpos=(1360, 875))
d.edge('CU11', 'CU05', points=[(1320, 1092), (1320, 945)],
       label='«include»', kind='include', source=(1, .5), target=(0, .75), labelpos=(1420, 1020))
d.edge('CU06', 'CU07', label='«include»', kind='include',
       source=(1, .5), target=(0, .5), labelpos=(1360, 1445))

for index, (case_id, y) in enumerate([('CU02', 1640), ('CU08', 1790), ('CU10', 1940)]):
    d.node(case_id, case_id + '\n' + cases[case_id], 560, y, 590, 95, 'ellipse')
    d.edge('admin', case_id, kind='association',
           source=(1, .28 + index * .20), target=(0, .5))
d.note('Línea continua: asociación · Línea discontinua con flecha: include / extend · Triángulo: generalización',1550,2145,20)
d.save()


# 2. Un proceso completo con un carril central y alternativas separadas.
# Las etiquetas Sí/No tienen fondo blanco y no quedan encima de las flechas.
d = D('proceso-completo', 'Proceso completo · Reserva, estadía y salida', 2600, 2500)
main = [
    ('inicio', 'Inicio', 'ellipse', 80),
    ('acceso', 'Iniciar sesión y validar perfil', 'rect', 240),
    ('huesped', 'Registrar o seleccionar huésped', 'input', 400),
    ('solicitud', 'Ingresar fechas, habitación\ny cantidad de pasajeros', 'input', 560),
    ('disp', '¿Hay disponibilidad\ny capacidad suficiente?', 'diamond', 720),
    ('reserva', 'Registrar reserva REGISTRADA', 'rect', 900),
    ('cambio', '¿Modificar o cancelar\nantes del ingreso?', 'diamond', 1060),
    ('checkin', 'Confirmar huéspedes y registrar check-in', 'rect', 1240),
    ('estadia', 'Crear estadía ACTIVA\ny ocupar habitación', 'rect', 1400),
    ('checkout', 'Registrar fecha de salida real', 'input', 1560),
    ('cuenta', 'Calcular costo por pasajero y total', 'rect', 1720),
    ('confirma', '¿Cuenta y salida\nconfirmadas?', 'diamond', 1880),
    ('cierre', 'Guardar costos, finalizar estadía\ny liberar habitación', 'rect', 2060),
    ('informe', 'Actualizar informes de ocupación y reservas', 'rect', 2220),
    ('fin', 'Fin', 'ellipse', 2380),
]
for node_id, label, shape, y in main:
    d.node(node_id, label, 930, y, 740, 96, shape,
           stroke=RED if shape == 'ellipse' else TEAL if shape == 'input' else EDGE)
for current, following in zip(main, main[1:]):
    node_id, _, shape, y = current
    label = 'Sí' if node_id in ['disp', 'confirma'] else ('No' if node_id == 'cambio' else '')
    d.edge(node_id, following[0], label=label, labelpos=(1340, y + 135))

# Alternativa 1: sin disponibilidad.
d.node('sin-disp', 'Mostrar conflicto y solicitar\notras fechas o habitación', 1850, 720, 650, 100, 'rect', stroke=TEAL)
d.node('sin-disp-fin', 'Fin sin reserva', 1850, 900, 650, 95, 'ellipse', stroke=RED)
d.edge('disp', 'sin-disp', label='No', source=(1, .5), target=(0, .5), labelpos=(1760, 695))
d.edge('sin-disp', 'sin-disp-fin')

# Alternativa 2: modificar o cancelar una reserva antes del ingreso.
d.node('gestion', 'Seleccionar reserva REGISTRADA', 80, 1060, 650, 96, 'input', stroke=TEAL)
d.node('cancelar', '¿Cancelar reserva?', 80, 1230, 650, 96, 'diamond')
d.node('modificada', 'Guardar cambios y volver a\nvalidar disponibilidad', 80, 1410, 650, 100, 'rect')
d.node('cancelada', 'Marcar CANCELADA y\nliberar disponibilidad', 80, 1590, 650, 100, 'rect')
d.node('gestion-fin', 'Fin · reserva actualizada', 80, 1770, 650, 95, 'ellipse', stroke=RED)
d.edge('cambio', 'gestion', label='Sí', source=(0, .5), target=(1, .5), labelpos=(820, 1035))
d.edge('gestion', 'cancelar')
d.edge('cancelar', 'modificada', label='No', labelpos=(440, 1360))
d.edge('cancelar', 'cancelada', points=[(25, 1278), (25, 1640)],
       label='Sí', source=(0, .5), target=(0, .5), labelpos=(45, 1375))
d.edge('modificada', 'gestion-fin', points=[(760, 1460), (760, 1818)],
       target=(1, .5), labelpos=(795, 1620))
d.edge('cancelada', 'gestion-fin')

# Alternativa 3: el usuario no confirma la salida.
d.node('no-confirma', 'Mantener estadía ACTIVA\ny corregir la cuenta', 1850, 1880, 650, 100, 'rect', stroke=TEAL)
d.node('no-confirma-fin', 'Fin sin check-out', 1850, 2060, 650, 95, 'ellipse', stroke=RED)
d.edge('confirma', 'no-confirma', label='No', source=(1, .5), target=(0, .5), labelpos=(1760, 1855))
d.edge('no-confirma', 'no-confirma-fin')
d.save()


def interface(key, title, mockup):
    """Una sola vista integral del sistema, no una galería de pantallas."""
    d = D(key, title, 1800, 1220)
    soft = '#d9eaf1' if mockup else '#f1f3f4'
    dark = BLUE if mockup else '#ffffff'
    d.node('header', 'Hotel Duerme Bien · Sistema de pasajeros', 35, 70, 1730, 80,
           'rounded' if mockup else 'rect', fill=dark)
    if mockup:
        d.nodes['header']['color'] = WHITE
        d.nodes['header']['bold'] = True

    d.node('nav', 'MENÚ\n\nDisponibilidad\nHabitaciones\nHuéspedes\nReservas\nCheck-in\nCheck-out\nInformes\nUsuarios',
           35, 180, 280, 960, 'rect', fill=soft)

    cards = [('Disponibles', '8'), ('Ocupadas', '12'), ('Reservas', '5'), ('Estadías activas', '10')]
    for i, (label, value) in enumerate(cards):
        x = 350 + i * 345
        d.node('card' + str(i), label + '\n' + (value if mockup else '[ dato ]'), x, 180, 310, 120,
               'rounded' if mockup else 'rect', fill=soft if mockup else WHITE)
        d.nodes['card' + str(i)]['bold'] = mockup

    d.node('form-title', 'Registrar reserva / ingreso', 350, 335, 1380, 55, 'caption')
    d.nodes['form-title']['bold'] = True
    fields = [
        ('Titular', 'Ana Ejemplo'), ('Habitación', '201 · Capacidad 2'),
        ('Entrada', '01/10/2026'), ('Salida', '03/10/2026'),
        ('Pasajeros', '2'), ('Estado', 'REGISTRADA')
    ]
    for i, (label, value) in enumerate(fields):
        col, row = i % 3, i // 3
        x, y = 350 + col * 460, 410 + row * 110
        shown = label + '\n' + (value if mockup else '[ campo / selección ]')
        d.node('field' + str(i), shown, x, y, 420, 78, 'control' if mockup else 'rect')

    d.node('primary', 'Guardar reserva', 350, 650, 420, 65,
           'rounded' if mockup else 'rect', fill=BLUE if mockup else soft)
    d.node('secondary', 'Confirmar check-in', 810, 650, 420, 65,
           'rounded' if mockup else 'rect', fill=BLUE if mockup else soft)
    d.node('third', 'Calcular check-out', 1270, 650, 420, 65,
           'rounded' if mockup else 'rect', fill=BLUE if mockup else soft)
    if mockup:
        for node_id in ['primary', 'secondary', 'third']:
            d.nodes[node_id]['color'] = WHITE
            d.nodes[node_id]['bold'] = True

    attrs = [
        'Reserva | Titular | Habitación | Fechas | Pasajeros | Estado | Acción',
        ('#1 | Ana Ejemplo | 201 | 01/10–03/10 | 2 | REGISTRADA | Modificar / Cancelar'
         if mockup else '[ registro con estado y acciones ]'),
        ('#2 | Luis Ejemplo | 305 | 02/10–04/10 | 1 | CHECK_IN | Ver detalle'
         if mockup else '[ registro con estado y acciones ]')
    ]
    d.node('result', 'Reservas y estadías', 350, 760, 1380, 230, 'table', attrs=attrs)
    d.node('summary', 'Cuenta seleccionada: 2 pasajeros · 2 noches · Total $40.000 CLP',
           350, 1020, 1380, 78, 'rounded' if mockup else 'rect', fill=soft)
    d.save()


interface('wireframe-completo', 'Wireframe completo · Vista general', False)
interface('mockup-completo', 'Mockup completo · Vista general', True)

# Una imagen real y completa por formato.
png_from_pdf('diagramas/sistema-casos-de-uso.pdf', 'casos-de-uso.png')
png_from_pdf('diagramas/proceso-completo.pdf', 'procesos.png')
png_from_pdf('diagramas/diagrama-de-clases.pdf', 'clases.png')
png_from_pdf('diagramas/modelo-de-datos.pdf', 'base-de-datos.png')
png_from_pdf('diagramas/wireframe-completo.pdf', 'wireframe.png')
png_from_pdf('diagramas/mockup-completo.pdf', 'mockup.png')

# Elimina las láminas antiguas para evitar confundirlas con los nuevos diseños.
for old in ['modelos.png', 'wireframes.png', 'mockups.png']:
    path = OUT / old
    if path.exists():
        path.unlink()
