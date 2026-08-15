from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    asv_svg_icon = fields.Text(default='')
    asv_generated_category_image = fields.Boolean(default=False)

    def write(self, vals):
        # Una imagen cargada desde la ficha de la categoría reemplaza el
        # recurso de respaldo generado por el módulo.
        if 'image_1920' in vals and 'asv_generated_category_image' not in vals:
            vals = dict(vals, asv_generated_category_image=False)
        return super().write(vals)

    def _asv_has_uploaded_category_image(self):
        """Distingue una imagen de usuario del PNG de respaldo del módulo."""
        from ..hooks import _CAT_ICON_COLORS, _make_icon_png_pil

        generated_images = {
            _make_icon_png_pil(*color)
            for color in _CAT_ICON_COLORS.values()
        }
        self.ensure_one()
        image = self.image_1920
        if isinstance(image, bytes):
            image = image.decode('ascii')
        return bool(image and image not in generated_images)
