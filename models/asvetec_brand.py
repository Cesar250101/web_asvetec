from odoo import fields, models


class AsvetecBrand(models.Model):
    """Logo administrable para el carrusel de marcas del sitio ASVETEC."""

    _name = 'asvetec.brand'
    _description = 'Marca representada ASVETEC'
    _order = 'sequence, name, id'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    is_default_logo = fields.Boolean(
        string='Logo predeterminado', default=False, readonly=True,
        help='Identifica los nombres tipográficos incluidos inicialmente por ASVETEC.')
    website_id = fields.Many2one(
        'website', string='Sitio web', ondelete='cascade',
        help='Déjelo vacío para mostrar esta marca en todos los sitios web.')
    image_1920 = fields.Image(
        string='Logo', max_width=1920, max_height=1920, attachment=False,
        help='Suba preferentemente un PNG o SVG horizontal con fondo transparente.')
    website_url = fields.Char(string='Enlace de la marca')

    def write(self, vals):
        # Al subir una imagen sobre una marca predeterminada, esta pasa a ser
        # contenido propio y debe mostrarse aunque se oculten los respaldos.
        if vals.get('image_1920') and 'is_default_logo' not in vals:
            vals = dict(vals, is_default_logo=False)
        return super().write(vals)


class Website(models.Model):
    _inherit = 'website'

    asv_show_default_brand_logos = fields.Boolean(
        string='Mostrar logos predeterminados ASVETEC', default=False,
        help='Muestra los nombres tipográficos de ejemplo cuando aún no se ha cargado un logo.')
