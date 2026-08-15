"""Normaliza la comparación de imágenes binarias de Odoo."""
from odoo import api, SUPERUSER_ID

from odoo.addons.web_asvetec.hooks import _CAT_ICON_COLORS, _make_icon_png_pil


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid, color in _CAT_ICON_COLORS.items():
        category = env.ref(xmlid, raise_if_not_found=False)
        if not category or not category.image_1920:
            continue
        image = category.image_1920
        if isinstance(image, bytes):
            image = image.decode('ascii')
        category.write({
            'asv_generated_category_image': image == _make_icon_png_pil(*color),
        })
