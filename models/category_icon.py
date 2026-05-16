from odoo import fields, models


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    asv_svg_icon = fields.Text(default='')
