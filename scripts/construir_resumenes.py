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
    image.quantize(colors=128, method=Image.Quantize.MEDIANCUT).save(OUT / output, optimize=True)


# 1. Un único UML con todos los actores y los doce casos de uso.
cases = {i: n for i, n, _ in MODEL['casos']}
d = D('sistema-casos-de-uso', 'Casos de uso completos · Hotel Duerme Bien', 1460, 1740)
d.node('system', 'Sistema de pasajeros', 230, 90, 1050, 1560, 'frame')
d.node('enc', 'Encargado', 20, 570, 150, 175, 'actor')
d.node('admin', 'Administrador', 1290, 1160, 150, 175, 'actor')

# Casos principales en una columna: las asociaciones no atraviesan óvalos.
main_cases = ['CU01', 'CU03', 'CU04', 'CU09', 'CU11', 'CU12', 'CU06']
for i, case_id in enumerate(main_cases):
    y = 160 + i * 190
    d.node(case_id, case_id + '\n' + cases[case_id], 290, y, 430, 100, 'ellipse')
    d.edge('enc', case_id, kind='association', source=(1, .16 + i * .11), target=(0, .5))

# Los casos incluidos quedan al costado de sus casos principales.
d.node('CU05', 'CU05\n' + cases['CU05'], 800, 635, 410, 100, 'ellipse')
d.node('CU07', 'CU07\n' + cases['CU07'], 800, 1205, 410, 100, 'ellipse')
d.edge('CU04', 'CU05', label='«include»', kind='include', source=(1, .35), target=(0, .2))
d.edge('CU09', 'CU05', label='«include»', kind='include', source=(1, .5), target=(0, .5))
d.edge('CU11', 'CU05', label='«include»', kind='include', source=(1, .65), target=(0, .8))
d.edge('CU06', 'CU07', label='«include»', kind='include', source=(1, .5), target=(0, .5))

# Administración se mantiene en su propia zona, sin líneas cruzadas.
for i, case_id in enumerate(['CU02', 'CU08', 'CU10']):
    y = 1370 + i * 90
    d.node(case_id, case_id + '\n' + cases[case_id], 800, y, 410, 78, 'ellipse')
    d.edge('admin', case_id, kind='association', source=(0, .22 + i * .25), target=(1, .5))
d.save()


# 2. Un único proceso coherente que resume el ciclo completo del pasajero.
d = D('proceso-completo', 'Proceso completo · Reserva, estadía y salida', 1400, 2180)
steps = [
    ('inicio', 'Inicio', 'ellipse'),
    ('acceso', 'Iniciar sesión y validar perfil', 'rect'),
    ('huesped', 'Registrar o seleccionar huésped', 'input'),
    ('solicitud', 'Ingresar fechas, habitación\ny cantidad de pasajeros', 'input'),
    ('disp', '¿Hay disponibilidad\ny capacidad suficiente?', 'diamond'),
    ('reserva', 'Registrar reserva', 'rect'),
    ('cambio', '¿Se requiere modificar\no cancelar antes del ingreso?', 'diamond'),
    ('checkin', 'Confirmar huéspedes y registrar check-in', 'rect'),
    ('estadia', 'Mantener estadía ACTIVA\ny habitación OCUPADA', 'rect'),
    ('checkout', 'Registrar fecha de salida', 'input'),
    ('cuenta', 'Calcular cuenta por pasajero y total', 'rect'),
    ('confirma', '¿Cuenta y salida confirmadas?', 'diamond'),
    ('cierre', 'Guardar costos, finalizar estadía\ny liberar habitación', 'rect'),
    ('informe', 'Actualizar informes de ocupación y reservas', 'rect'),
    ('fin', 'Fin', 'ellipse'),
]
for i, (node_id, label, shape) in enumerate(steps):
    d.node(node_id, label, 400, 80 + i * 140, 600, 88, shape,
           stroke=RED if shape == 'ellipse' else TEAL if shape == 'input' else EDGE)
for i in range(len(steps) - 1):
    node_id, _, shape = steps[i]
    label = 'No' if node_id == 'cambio' else ('Sí' if shape == 'diamond' else '')
    d.edge(node_id, steps[i + 1][0], label=label)

d.node('sin', 'Fin · cambiar fechas\no habitación', 1030, 640, 340, 95, 'ellipse', stroke=RED)
d.edge('disp', 'sin', label='No', source=(1, .5), target=(0, .5))
d.node('gestion', 'Modificar reserva o marcarla\nCANCELADA', 20, 920, 340, 95, 'rect', stroke=TEAL)
d.edge('cambio', 'gestion', label='Sí', source=(0, .5), target=(1, .5))
d.node('gestion-fin', 'Fin · reserva actualizada', 20, 1060, 340, 90, 'ellipse', stroke=RED)
d.edge('gestion', 'gestion-fin')
d.node('rechazo', 'Fin · mantener estadía ACTIVA\ny corregir la cuenta', 1030, 1620, 340, 95, 'ellipse', stroke=RED)
d.edge('confirma', 'rechazo', label='No', source=(1, .5), target=(0, .5))
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
