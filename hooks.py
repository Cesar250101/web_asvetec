import base64
import io
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

# Color de acento por categoría (xmlid → RGB)
_CAT_ICON_COLORS = {
    'web_asvetec.cat_limpieza_industrial': (15, 159, 230),
    'web_asvetec.cat_equipos_taller':      (232,  77,  28),
    'web_asvetec.cat_generadores':         (245, 166,  35),
    'web_asvetec.cat_arriendo':            ( 39, 174,  96),
    'web_asvetec.cat_hogar_jardin':        ( 22, 160, 133),
    'web_asvetec.cat_herramientas':        ( 44,  44,  97),
    'web_asvetec.cat_accesorios':          (142,  68, 173),
    'web_asvetec.cat_insumos':             ( 26, 188, 156),
}


def _make_icon_png_pil(r, g, b, size=128):
    """Genera un PNG válido usando Pillow (dependencia de Odoo).
    Fondo azul claro + círculo del color de acento."""
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        _logger.warning("Pillow no disponible — no se pueden generar iconos PNG")
        return False

    img = Image.new('RGB', (size, size), (240, 247, 254))
    draw = ImageDraw.Draw(img)
    radius = size // 3
    cx = cy = size // 2
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        fill=(r, g, b),
    )
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def assign_category_icons(env, force=False):
    """Asigna un PNG icono a image_1920 de cada categoría ASVETEC.
    Si force=True, sobreescribe imágenes existentes (útil en migraciones)."""
    assigned = 0
    for xmlid, color in _CAT_ICON_COLORS.items():
        cat = env.ref(xmlid, raise_if_not_found=False)
        if not cat:
            _logger.warning("No se encontró la categoría %s", xmlid)
            continue
        if cat.image_1920 and not force:
            continue
        png_b64 = _make_icon_png_pil(*color)
        if not png_b64:
            continue
        try:
            cat.write({
                'image_1920': png_b64,
                'asv_generated_category_image': True,
            })
            assigned += 1
        except Exception as exc:
            _logger.error("Fallo al asignar icono a %s: %s", xmlid, exc)
    _logger.info("ASVETEC: %s iconos de categoría asignados", assigned)
    return assigned


def post_init_hook(cr, registry):
    """Se ejecuta una sola vez al instalar el módulo."""
    env = api.Environment(cr, SUPERUSER_ID, {})

    assign_category_icons(env, force=False)

    website = env['website'].search([('name', '=', 'ASVETEC')], limit=1)
    if not website:
        return

    lang_es = (
        env['res.lang'].search([('code', '=', 'es_CL')], limit=1)
        or env['res.lang'].search([('code', '=', 'es')], limit=1)
    )

    vals = {'homepage_url': '/asvetec'}
    if lang_es:
        vals['language_ids'] = [(6, 0, [lang_es.id])]
        vals['default_lang_id'] = lang_es.id
    website.write(vals)

    Menu = env['website.menu']
    top_menu = website.menu_id
    for label, url, seq in [
        ('Catálogo', '/shop', 10),
        ('Quiénes somos', '/asvetec#nosotros', 20),
        ('Servicios', '/asvetec#servicios', 30),
        ('Contáctenos', '/contactus', 90),
    ]:
        if top_menu and not Menu.search([
            ('website_id', '=', website.id),
            ('url', '=', url),
        ], limit=1):
            Menu.create({
                'name': label,
                'url': url,
                'parent_id': top_menu.id,
                'website_id': website.id,
                'sequence': seq,
            })
