from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Redefine el campo nativo de website_sale (Many2one) como Many2many:
    # mismo nombre, para que todo el codigo del core que ya lo usa
    # (controllers/main.py, templates.xml, _get_website_ribbon) lo siga
    # encontrando sin cambios; el merge de definiciones de Odoo usa el tipo
    # de la ultima clase cargada (odoo/models.py::_setup_base, linea
    # "Field = type(fields_[-1])"), por lo que este addon, cargado despues de
    # website_sale, determina el tipo final del campo.
    website_ribbon_id = fields.Many2many(
        'product.ribbon',
        'product_template_asv_ribbon_rel',
        'product_template_id',
        'ribbon_id',
        string='Cintas',
        help='Cintas mostradas en el sitio web. Se permite seleccionar varias '
             '(antes era una unica cinta).',
    )

    def _get_website_ribbon(self):
        # website_ribbon_id ahora puede traer varias cintas. El resto del
        # core (grilla nativa de /shop, controllers/main.py) sigue esperando
        # una sola: acceder a un campo de un recordset con 2+ registros
        # lanza "Expected singleton". Se trunca a la primera para no romper
        # esas rutas; la seccion "Productos destacados" de ASVETEC itera
        # website_ribbon_id completo por su cuenta, sin pasar por este metodo.
        return super()._get_website_ribbon()[:1]
