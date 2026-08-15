"""Distingue los iconos de respaldo de las imágenes subidas por el usuario."""
from odoo import api, SUPERUSER_ID

from odoo.addons.web_asvetec.hooks import _CAT_ICON_COLORS, _make_icon_png_pil


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid, color in _CAT_ICON_COLORS.items():
        category = env.ref(xmlid, raise_if_not_found=False)
        if not category or not category.image_1920:
            continue
        generated = _make_icon_png_pil(*color)
        category.write({
            'asv_generated_category_image': category.image_1920 == generated,
        })
