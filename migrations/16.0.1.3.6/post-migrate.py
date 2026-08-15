"""Recupera la página raíz propia del sitio predeterminado."""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    default_website = env.ref('website.default_website')
    asvetec_home_page = env.ref('web_asvetec.asv_home_page')
    default_home_view = env['ir.ui.view'].search([
        ('key', '=', 'website.homepage'),
        ('website_id', '=', default_website.id),
    ], limit=1)

    default_home_page = env['website.page'].search([
        ('website_id', '=', default_website.id),
        ('url', '=', '/'),
    ], limit=1)
    if not default_home_page and default_home_view:
        default_home_page = env['website.page'].create({
            'url': '/',
            'view_id': default_home_view.id,
            'is_published': True,
        })

    # La página temporal quedó asociada a la plantilla ASVETEC durante la
    # reversión. La portada oficial de ASVETEC es /asvetec.
    duplicate_pages = env['website.page'].search([
        ('website_id', '=', asvetec_home_page.website_id.id),
        ('url', '=', '/'),
        ('view_id', '=', asvetec_home_page.view_id.id),
        ('id', '!=', asvetec_home_page.id),
    ])
    duplicate_pages.unlink()
