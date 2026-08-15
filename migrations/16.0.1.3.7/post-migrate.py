"""Restaura los enlaces de navegación de ambas webs."""
from odoo import api, SUPERUSER_ID


def _ensure_menu(env, website, name, url, sequence):
    menu = env['website.menu'].search([
        ('website_id', '=', website.id),
        ('url', '=', url),
    ], limit=1)
    if not menu:
        env['website.menu'].create({
            'name': name,
            'url': url,
            'parent_id': website.menu_id.id,
            'website_id': website.id,
            'sequence': sequence,
        })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    default_website = env.ref('website.default_website')
    asvetec_website = env.ref('web_asvetec.website_asvetec')

    _ensure_menu(env, default_website, 'Home', '/', 10)
    _ensure_menu(env, asvetec_website, 'Quiénes somos', '/asvetec#nosotros', 20)
    _ensure_menu(env, asvetec_website, 'Servicios', '/asvetec#servicios', 30)
