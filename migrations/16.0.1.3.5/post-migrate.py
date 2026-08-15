"""Restaura la separación entre la página predeterminada y ASVETEC.

Los snippets se registran globalmente en ``website.snippets``, por lo que se
pueden insertar desde el editor del sitio predeterminado sin reemplazar su
portada ni eliminar la web ASVETEC.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    default_website = env.ref('website.default_website')
    asvetec_website = env.ref('web_asvetec.website_asvetec')

    # Restaura la página raíz que pertenecía al sitio predeterminado.
    default_home_view = env['ir.ui.view'].search([
        ('key', '=', 'website.homepage'),
        ('website_id', '=', default_website.id),
    ], limit=1)
    default_home_page = env['website.page'].search([
        ('website_id', '=', default_website.id),
        ('url', '=', '/'),
    ], limit=1)
    if default_home_page and default_home_view:
        default_home_page.write({'view_id': default_home_view.id})
    default_website.write({'name': 'My Website', 'homepage_url': False})

    # El catálogo y la configuración de la compañía pertenecían a ASVETEC
    # antes de la migración revertida.
    for model_name in ('product.template', 'sale.order', 'res.company'):
        records = env[model_name].with_context(active_test=False).search([
            ('website_id', '=', default_website.id),
        ])
        if records:
            records.write({'website_id': asvetec_website.id})

    env['website.menu'].search([
        ('website_id', '=', default_website.id),
        ('url', 'in', ['/#nosotros', '/#servicios']),
    ]).unlink()

    asvetec_website.write({'homepage_url': '/asvetec'})
