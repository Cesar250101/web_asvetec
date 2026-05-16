"""
Generador de brochure PDF para ASVETEC.
Ejecutar una sola vez: python generate_brochure.py
Requiere: reportlab, Pillow
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from PIL import Image as PilImage

# ── Colores de marca ───────────────────────────────────────────────────────────
NAVY    = HexColor('#2c2c61')
NAVY_D  = HexColor('#1c1a44')
NAVY_L  = HexColor('#342f5e')
CYAN    = HexColor('#0f9fe6')
CYAN_L  = HexColor('#7ed0f5')
PAPER   = HexColor('#f7f8fa')
INK     = HexColor('#1a1a1f')
MUTE    = HexColor('#8a8e96')
SUCCESS = HexColor('#2faa5b')

W, H = A4   # 595.27 x 841.89 pts

BASE = os.path.dirname(__file__)
IMG  = os.path.join(BASE, 'src', 'img')
OUT  = os.path.join(BASE, 'src', 'pdf', 'brochure_asvetec.pdf')
os.makedirs(os.path.dirname(OUT), exist_ok=True)


# ── Helpers ────────────────────────────────────────────────────────────────────

def stripe(c, x, y, width, h=3*mm):
    """Franja degradada cyan→azul."""
    steps = 40
    for i in range(steps):
        t = i / steps
        r = int(15 + t * (81 - 15))
        g = int(159 + t * (138 - 159))
        b = int(230 + t * (188 - 230))
        c.setFillColorRGB(r/255, g/255, b/255)
        c.rect(x + i * width/steps, y, width/steps + 1, h, fill=1, stroke=0)


def place_image(c, path, x, y, w, h, cover=True):
    """Coloca una imagen recortada al centro (simula object-fit: cover)."""
    if not os.path.exists(path):
        c.setFillColor(NAVY_L)
        c.rect(x, y, w, h, fill=1, stroke=0)
        return
    try:
        img = PilImage.open(path)
        iw, ih = img.size
        ratio_w = w / iw
        ratio_h = h / ih
        if cover:
            ratio = max(ratio_w, ratio_h)
        else:
            ratio = min(ratio_w, ratio_h)
        nw = iw * ratio * 2.83465   # px → pt approx
        nh = ih * ratio * 2.83465
        # Center
        ox = x + (w - nw) / 2
        oy = y + (h - nh) / 2
        c.saveState()
        c.clipPath(c.beginPath(), stroke=0, fill=0)
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        c.drawImage(path, ox, oy, nw, nh, preserveAspectRatio=False)
        c.restoreState()
    except Exception:
        c.setFillColor(NAVY_L)
        c.rect(x, y, w, h, fill=1, stroke=0)


def draw_image_clipped(c, path, x, y, w, h):
    """Dibuja imagen recortada al rectángulo dado."""
    if not os.path.exists(path):
        c.setFillColor(NAVY_L)
        c.rect(x, y, w, h, fill=1, stroke=0)
        return
    try:
        c.saveState()
        p = c.beginPath()
        p.rect(x, y, w, h)
        c.clipPath(p, stroke=0, fill=0)
        # calcula escala para cubrir el rect
        from reportlab.lib.utils import ImageReader
        ir = ImageReader(path)
        iw, ih = ir.getSize()
        ratio_w = w / iw
        ratio_h = h / ih
        ratio = max(ratio_w, ratio_h)
        nw = iw * ratio
        nh = ih * ratio
        ox = x + (w - nw) / 2
        oy = y + (h - nh) / 2
        c.drawImage(path, ox, oy, nw, nh, preserveAspectRatio=False, mask='auto')
        c.restoreState()
    except Exception:
        c.setFillColor(NAVY_L)
        c.rect(x, y, w, h, fill=1, stroke=0)


def text(c, txt, x, y, font='Helvetica', size=10, color=INK, align='left'):
    c.setFont(font, size)
    c.setFillColor(color)
    if align == 'center':
        c.drawCentredString(x, y, txt)
    elif align == 'right':
        c.drawRightString(x, y, txt)
    else:
        c.drawString(x, y, txt)


def wrapped_text(c, txt, x, y, width, font='Helvetica', size=10, color=INK,
                 leading=14, align=TA_LEFT):
    style = ParagraphStyle('s', fontName=font, fontSize=size, leading=leading,
                            textColor=color, alignment=align)
    p = Paragraph(txt, style)
    pw, ph = p.wrap(width, 9999)
    p.drawOn(c, x, y - ph)
    return ph


def service_block(c, x, y, w, h, icon_lines, title, desc, tag):
    """Dibuja una tarjeta de servicio."""
    # Fondo blanco con borde
    c.setStrokeColor(HexColor('#e4e6eb'))
    c.setFillColor(white)
    c.roundRect(x, y, w, h, 4*mm, fill=1, stroke=1)
    # Tag
    c.setFillColor(CYAN)
    c.roundRect(x+4*mm, y+h-8*mm, len(tag)*2*mm + 4*mm, 5*mm, 2*mm, fill=1, stroke=0)
    text(c, tag, x+6*mm, y+h-5.8*mm, 'Helvetica-Bold', 6.5, white)
    # Icono fondo
    c.setFillColor(HexColor('#eaf6fd'))
    c.roundRect(x+4*mm, y+h-20*mm, 12*mm, 12*mm, 2*mm, fill=1, stroke=0)
    # Título
    text(c, title, x+4*mm, y+h-26*mm, 'Helvetica-Bold', 10, NAVY)
    # Descripción
    wrapped_text(c, desc, x+4*mm, y+h-30*mm, w-8*mm, 'Helvetica', 8, MUTE, 11)


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 1 — PORTADA
# ══════════════════════════════════════════════════════════════════════════════
def page_cover(c):
    # Fondo navy oscuro
    c.setFillColor(NAVY_D)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Imagen de fondo (warehouse) con overlay
    draw_image_clipped(c, os.path.join(IMG, 'hero-workshop.jpg'), 0, 0, W, H)

    # Overlay oscuro
    c.setFillColorRGB(0.11, 0.10, 0.27, alpha=0.82)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Franja cyan top
    stripe(c, 0, H - 4*mm, W, 4*mm)

    # Logo si existe
    logo_path = os.path.join(IMG, 'logo-asvetec.png')
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 18*mm, H - 36*mm, width=50*mm, height=18*mm,
                        preserveAspectRatio=True, mask='auto')
        except Exception:
            text(c, 'ASVETEC', 18*mm, H - 30*mm, 'Helvetica-Bold', 22, white)
    else:
        text(c, 'ASVETEC', 18*mm, H - 30*mm, 'Helvetica-Bold', 22, white)

    # Año
    text(c, '2024–2025', W - 18*mm, H - 24*mm, 'Helvetica', 9, CYAN_L, align='right')

    # Línea decorativa cyan
    c.setStrokeColor(CYAN)
    c.setLineWidth(2)
    c.line(18*mm, H*0.52, 60*mm, H*0.52)

    # Título principal
    text(c, 'Brochure de Servicios', 18*mm, H*0.54, 'Helvetica', 11, CYAN_L)

    # Headline
    c.setFont('Helvetica-Bold', 32)
    c.setFillColor(white)
    lines = ['Asesoría técnica', 'para la industria', 'del norte de Chile.']
    for i, line in enumerate(lines):
        c.drawString(18*mm, H*0.46 - i*36, line)

    # Sub
    wrapped_text(c, 'Equipos industriales · Servicio en terreno · Arriendo · Instalaciones',
                 18*mm, H*0.335, W - 36*mm, 'Helvetica', 11, CYAN_L, 16)

    # Separador
    c.setStrokeColor(HexColor('#ffffff30'))
    c.setLineWidth(0.5)
    c.line(18*mm, H*0.28, W - 18*mm, H*0.28)

    # Datos de contacto en la base
    contact_items = [
        ('📞', '+56 55 293 6063'),
        ('✉', 'ventas@asvetec.cl'),
        ('📍', 'Antofagasta, II Región · Chile'),
        ('🌐', 'asvetec.cl'),
    ]
    cx = 18*mm
    for icon, val in contact_items:
        text(c, val, cx, H*0.22, 'Helvetica', 9, white)
        cx += c.stringWidth(val, 'Helvetica', 9) + 18*mm

    # Nota acreditación
    wrapped_text(c, 'Personal con acreditaciones para acceso a sitios mineros. Empresas &amp; '
                    'Contratistas CODELCO, BHP, Antofagasta Minerals.',
                 18*mm, H*0.16, W - 36*mm, 'Helvetica', 8, HexColor('#9999bb'), 12)

    # Franja navy bottom
    c.setFillColor(NAVY)
    c.rect(0, 0, W, 14*mm, fill=1, stroke=0)
    text(c, 'RyS ASVETEC ltda. · Todos los derechos reservados', W/2, 5*mm,
         'Helvetica', 7.5, HexColor('#6666aa'), align='center')


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 2 — QUIÉNES SOMOS
# ══════════════════════════════════════════════════════════════════════════════
def page_about(c):
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header navy
    c.setFillColor(NAVY)
    c.rect(0, H - 32*mm, W, 32*mm, fill=1, stroke=0)
    stripe(c, 0, H - 4*mm, W, 4*mm)
    text(c, 'QUIÉNES SOMOS', 18*mm, H - 15*mm, 'Helvetica-Bold', 9, CYAN_L)
    text(c, 'RyS ASVETEC ltda.', 18*mm, H - 24*mm, 'Helvetica-Bold', 18, white)

    # Foto izquierda (portrait office / warehouse)
    draw_image_clipped(c, os.path.join(IMG, 'portrait-office.jpg'),
                       18*mm, H - 32*mm - 80*mm, 80*mm, 80*mm)

    # Texto derecha
    tx = 18*mm + 80*mm + 8*mm
    tw = W - tx - 18*mm

    wrapped_text(c,
        '<b>RyS ASVETEC</b> es una empresa de la Segunda Región enfocada en '
        'brindar soluciones en terreno rápidas y confiables.',
        tx, H - 38*mm, tw, 'Helvetica', 10, INK, 15)

    wrapped_text(c,
        'Con más de <b>10 años de experiencia</b> entregando equipos para taller y '
        'sistemas de <b>Automatización Neumática y Electrónica</b>, somos el '
        'proveedor de confianza para la minería e industria del norte de Chile.',
        tx, H - 55*mm, tw, 'Helvetica', 9.5, INK, 14)

    wrapped_text(c,
        'Nuestro nombre lo dice todo: ASVETEC = <b>AS</b>esorías y '
        '<b>VE</b>ntas <b>TEC</b>nicas. Más que vender equipos, asesoramos '
        'a cada cliente para que obtenga la solución exacta que su operación necesita.',
        tx, H - 78*mm, tw, 'Helvetica', 9.5, INK, 14)

    # Tarjeta estadística
    c.setFillColor(CYAN)
    c.roundRect(tx, H - 115*mm, tw, 26*mm, 3*mm, fill=1, stroke=0)
    text(c, '10+', tx + tw/2, H - 97*mm, 'Helvetica-Bold', 26, white, align='center')
    text(c, 'años desarrollando contratos para empresas mineras e industriales',
         tx + tw/2, H - 108*mm, 'Helvetica', 8, white, align='center')

    # Puntos clave
    ky = H - 32*mm - 95*mm
    points = [
        ('Personal calificado',
         'Técnicos con experiencia en mantenimiento\nindustrial y minero.'),
        ('Equipamiento propio',
         'Talleres en Antofagasta y unidades\nmóviles para faena.'),
        ('Representaciones oficiales',
         'Distribuidores de marcas nacionales\ne internacionales.'),
        ('Respuesta rápida',
         'Cotización, diagnóstico y despacho\ndentro de la jornada hábil.'),
    ]
    col_w = (W - 36*mm) / 2
    for idx, (title, desc) in enumerate(points):
        col = idx % 2
        row = idx // 2
        px = 18*mm + col * col_w
        py = ky - row * 28*mm
        # Check icon
        c.setFillColor(SUCCESS)
        c.circle(px + 4*mm, py - 3*mm, 3.5*mm, fill=1, stroke=0)
        c.setFont('Helvetica-Bold', 8)
        c.setFillColor(white)
        c.drawCentredString(px + 4*mm, py - 4.5*mm, '✓')
        # Title
        text(c, title, px + 10*mm, py, 'Helvetica-Bold', 9.5, NAVY)
        # Desc
        for li, line in enumerate(desc.split('\n')):
            text(c, line, px + 10*mm, py - 6*mm - li*5.5*mm, 'Helvetica', 8, MUTE)

    # Imagen warehouse abajo derecha
    draw_image_clipped(c, os.path.join(IMG, 'warehouse.jpg'),
                       W/2 + 9*mm, 16*mm, W/2 - 27*mm, 45*mm)

    # Footer
    c.setFillColor(NAVY)
    c.rect(0, 0, W, 14*mm, fill=1, stroke=0)
    text(c, 'ventas@asvetec.cl  ·  +56 55 293 6063  ·  Antofagasta, Chile',
         W/2, 5*mm, 'Helvetica', 7.5, HexColor('#6666aa'), align='center')


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 3 — SERVICIOS
# ══════════════════════════════════════════════════════════════════════════════
def page_services(c):
    c.setFillColor(PAPER)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header navy
    c.setFillColor(NAVY)
    c.rect(0, H - 32*mm, W, 32*mm, fill=1, stroke=0)
    stripe(c, 0, H - 4*mm, W, 4*mm)
    text(c, 'SERVICIOS EN TERRENO', 18*mm, H - 15*mm, 'Helvetica-Bold', 9, CYAN_L)
    text(c, 'Donde esté su faena, llegamos.', 18*mm, H - 24*mm, 'Helvetica-Bold', 18, white)

    # Sub header
    wrapped_text(c,
        'Combinamos talleres en Antofagasta con servicio en terreno desde Arica hasta Atacama. '
        'Diseñamos contratos de prestación de servicios adaptados a las necesidades de cada cliente.',
        18*mm, H - 38*mm, W - 36*mm, 'Helvetica', 9.5, MUTE, 14)

    # Grid 2x2 de servicios
    services = [
        {
            'tag': 'Antofagasta',
            'title': 'Talleres Propios',
            'desc': (
                'Mantención y reparación de equipos en nuestros talleres en Antofagasta, '
                'con bancos de prueba y repuestos en stock para reducir tiempos de parada.'
            ),
            'features': ['Diagnóstico técnico rápido', 'Banco de prueba presión/caudal',
                         'Repuestos en stock', 'Garantía de reparación'],
        },
        {
            'tag': 'Sitio minero',
            'title': 'Faenas Mineras',
            'desc': (
                'Servicio técnico programado y de emergencia en faena. Personal con '
                'acreditaciones para acceso a sitio minero CODELCO, BHP, Antofagasta Minerals.'
            ),
            'features': ['Personal acreditado faena', 'Respuesta 24h en emergencias',
                         'Unidades móviles equipadas', 'Contratos de mantención'],
        },
        {
            'tag': 'Llave en mano',
            'title': 'Instalaciones Industriales',
            'desc': (
                'Implementación de líneas de aire comprimido, sistemas de limpieza industrial '
                'y automatización neumática y electrónica. Proyectos llave en mano.'
            ),
            'features': ['Líneas de aire comprimido', 'Automatización neumática',
                         'Sistemas de limpieza', 'Planos y certificación'],
        },
        {
            'tag': 'Disponibilidad inmediata',
            'title': 'Arriendo de Equipos',
            'desc': (
                'Generadores, compresores e hidrolavadoras disponibles por día, mes o '
                'contrato de faena. Entrega en sitio con o sin operador calificado.'
            ),
            'features': ['Generadores 10–200 kVA', 'Compresores 25–185 PCM',
                         'Hidrolavadoras industriales', 'Con o sin operador'],
        },
    ]

    card_w = (W - 46*mm) / 2
    card_h = 88*mm
    margin_x = 18*mm

    for idx, svc in enumerate(services):
        col = idx % 2
        row = idx // 2
        cx = margin_x + col * (card_w + 10*mm)
        cy = H - 68*mm - row * (card_h + 6*mm)

        # Fondo tarjeta
        c.setFillColor(white)
        c.setStrokeColor(HexColor('#e4e6eb'))
        c.setLineWidth(0.5)
        c.roundRect(cx, cy - card_h, card_w, card_h, 3*mm, fill=1, stroke=1)

        # Tag
        c.setFillColor(CYAN)
        tag_w = c.stringWidth(svc['tag'], 'Helvetica-Bold', 7) + 8*mm
        c.roundRect(cx + 4*mm, cy - 8*mm, tag_w, 5*mm, 1.5*mm, fill=1, stroke=0)
        text(c, svc['tag'], cx + 6*mm, cy - 5.5*mm, 'Helvetica-Bold', 7, white)

        # Título
        text(c, svc['title'], cx + 4*mm, cy - 16*mm, 'Helvetica-Bold', 12, NAVY)

        # Línea cyan
        c.setStrokeColor(CYAN)
        c.setLineWidth(1.5)
        c.line(cx + 4*mm, cy - 18*mm, cx + 4*mm + 12*mm, cy - 18*mm)

        # Descripción
        wrapped_text(c, svc['desc'], cx + 4*mm, cy - 22*mm, card_w - 8*mm,
                     'Helvetica', 8.5, INK, 13)

        # Features
        for fi, feat in enumerate(svc['features']):
            fy = cy - 50*mm - fi * 8*mm
            c.setFillColor(CYAN)
            c.circle(cx + 6.5*mm, fy + 1.5*mm, 1.5*mm, fill=1, stroke=0)
            text(c, feat, cx + 10*mm, fy, 'Helvetica', 8, MUTE)

    # Footer
    c.setFillColor(NAVY)
    c.rect(0, 0, W, 14*mm, fill=1, stroke=0)
    text(c, 'Solicite cotización en ventas@asvetec.cl o llame al +56 55 293 6063',
         W/2, 5*mm, 'Helvetica', 7.5, HexColor('#6666aa'), align='center')


# ══════════════════════════════════════════════════════════════════════════════
# PÁGINA 4 — CATEGORÍAS DE PRODUCTOS + CONTACTO
# ══════════════════════════════════════════════════════════════════════════════
def page_products_contact(c):
    c.setFillColor(white)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Header navy
    c.setFillColor(NAVY)
    c.rect(0, H - 32*mm, W, 32*mm, fill=1, stroke=0)
    stripe(c, 0, H - 4*mm, W, 4*mm)
    text(c, 'PRODUCTOS Y CONTACTO', 18*mm, H - 15*mm, 'Helvetica-Bold', 9, CYAN_L)
    text(c, 'Equipos en stock para despacho inmediato.', 18*mm, H - 24*mm, 'Helvetica-Bold', 18, white)

    # Categorías de productos (grid 4 x 2)
    categories = [
        ('Limpieza Industrial', 'Hydrolavadoras, aspiradoras,\nequipos de limpieza de alta presión.'),
        ('Equipos de Taller', 'Prensas, elevadores, llaves\nneumáticas y herramientas.'),
        ('Generadores', 'Grupos electrógenos 10–200 kVA,\nnafta, diésel y gas.'),
        ('Arriendo', 'Generadores y compresores\npor día, mes o faena.'),
        ('Hogar y Jardín', 'Motobombas, cortadoras,\nmotosierras y accesorios.'),
        ('Herramientas', 'Herramientas neumáticas,\neléctricas e hidráulicas.'),
        ('Accesorios', 'Repuestos, filtros, aceites\ny consumibles industriales.'),
        ('Insumos', 'Productos de limpieza,\nlubricantes y sellantes.'),
    ]

    cat_w = (W - 46*mm) / 4
    cat_h = 30*mm

    for idx, (name, desc) in enumerate(categories):
        col = idx % 4
        row = idx // 4
        cx = 18*mm + col * (cat_w + 3*mm)
        cy = H - 42*mm - row * (cat_h + 4*mm)

        c.setFillColor(PAPER)
        c.setStrokeColor(HexColor('#e4e6eb'))
        c.setLineWidth(0.5)
        c.roundRect(cx, cy - cat_h, cat_w, cat_h, 2*mm, fill=1, stroke=1)

        # Línea de color top
        c.setFillColor(CYAN)
        c.roundRect(cx, cy - 2*mm, cat_w, 2*mm, 1*mm, fill=1, stroke=0)

        text(c, name, cx + 3*mm, cy - 8*mm, 'Helvetica-Bold', 8, NAVY)
        for li, line in enumerate(desc.split('\n')):
            text(c, line, cx + 3*mm, cy - 14*mm - li * 5*mm, 'Helvetica', 7, MUTE)

    # Imagen right col separado
    # (foto de workshop en zona de contacto)
    draw_image_clipped(c, os.path.join(IMG, 'hero-workshop.jpg'),
                       W - 18*mm - 65*mm, 18*mm, 65*mm, 50*mm)
    # Overlay
    c.setFillColorRGB(0.17, 0.18, 0.38, alpha=0.55)
    c.rect(W - 18*mm - 65*mm, 18*mm, 65*mm, 50*mm, fill=1, stroke=0)
    text(c, 'Visítenos', W - 18*mm - 65*mm/2, 52*mm, 'Helvetica-Bold', 10, white, align='center')
    text(c, 'Antofagasta, II Región', W - 18*mm - 65*mm/2, 44*mm, 'Helvetica', 8, CYAN_L, align='center')

    # Sección de contacto
    contact_y = H - 42*mm - 2*(cat_h + 4*mm) - 14*mm
    c.setFillColor(NAVY)
    c.roundRect(18*mm, 18*mm, W - 36*mm - 65*mm - 8*mm, contact_y - 18*mm, 3*mm, fill=1, stroke=0)

    ty = contact_y - 4*mm
    text(c, 'Contáctenos', 28*mm, ty, 'Helvetica-Bold', 13, white)
    ty -= 8*mm
    stripe(c, 28*mm, ty, 20*mm, 1.5*mm)

    contact_data = [
        ('Teléfono:', '+56 55 293 6063'),
        ('WhatsApp:', '+56 9 XXXX XXXX'),
        ('Email:', 'ventas@asvetec.cl'),
        ('Dirección:', 'Antofagasta, II Región, Chile'),
        ('Sitio web:', 'www.asvetec.cl'),
        ('Horario:', 'Lun–Vie 8:30–18:00'),
    ]
    ty -= 6*mm
    for label, val in contact_data:
        text(c, label, 28*mm, ty, 'Helvetica-Bold', 8, CYAN_L)
        text(c, val, 55*mm, ty, 'Helvetica', 8.5, white)
        ty -= 7*mm

    # CTA
    ty -= 4*mm
    c.setFillColor(CYAN)
    cta_w = W - 36*mm - 65*mm - 24*mm
    c.roundRect(28*mm, ty - 9*mm, cta_w, 9*mm, 2*mm, fill=1, stroke=0)
    text(c, 'Solicitar cotización →', 28*mm + cta_w/2, ty - 6*mm,
         'Helvetica-Bold', 9, white, align='center')

    # Footer
    c.setFillColor(NAVY_D)
    c.rect(0, 0, W, 14*mm, fill=1, stroke=0)
    stripe(c, 0, 13.5*mm, W, 1*mm)
    text(c, 'RyS ASVETEC ltda.  ·  Antofagasta, Chile  ·  ventas@asvetec.cl  ·  +56 55 293 6063  ·  asvetec.cl',
         W/2, 5*mm, 'Helvetica', 7, HexColor('#6666aa'), align='center')


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    c = canvas.Canvas(OUT, pagesize=A4)
    c.setTitle('Brochure de Servicios — ASVETEC')
    c.setAuthor('RyS ASVETEC ltda.')
    c.setSubject('Equipos industriales y servicios en terreno, norte de Chile')

    print('Generando portada...')
    page_cover(c)
    c.showPage()

    print('Generando Quiénes Somos...')
    page_about(c)
    c.showPage()

    print('Generando Servicios...')
    page_services(c)
    c.showPage()

    print('Generando Productos y Contacto...')
    page_products_contact(c)
    c.showPage()

    c.save()
    size_kb = os.path.getsize(OUT) // 1024
    print(f'\n✓ Brochure generado: {OUT}')
    print(f'  Tamaño: {size_kb} KB  |  4 páginas A4')


if __name__ == '__main__':
    main()
