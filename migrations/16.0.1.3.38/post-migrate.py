"""Alinea el menú principal de ASVETEC con la navegación del footer."""
from odoo import api, SUPERUSER_ID


_MENU_ITEMS = (
    ('Inicio', '/', 10, ('Inicio',)),
    ('Catálogo', '/shop', 20, ('Catálogo', 'Tienda')),
    ('Quiénes somos', '/#nosotros', 30, ('Quiénes somos',)),
    ('Servicios', '/#servicios', 40, ('Servicios',)),
    ('Contacto', '/#contacto', 50, ('Contacto', 'Contáctenos')),
)


def _find_menu(menu_model, website, root_menu, url, names):
    menu = menu_model.search([
        ('website_id', '=', website.id),
        ('parent_id', '=', root_menu.id),
        ('url', '=', url),
    ], limit=1)
    if not menu:
        menu = menu_model.search([
            ('website_id', '=', website.id),
            ('parent_id', '=', root_menu.id),
            ('name', 'in', names),
        ], order='sequence, id', limit=1)
    return menu


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    website_model = env['website']
    menu_model = env['website.menu']
    websites = website_model.search([]).filtered(
        lambda website: (website.name or '').lower() == 'asvetec'
    )

    for website in websites:
        root_menu = menu_model.search([
            ('website_id', '=', website.id),
            ('parent_id', '=', False),
        ], order='id', limit=1)
        if not root_menu:
            continue

        for name, url, sequence, names in _MENU_ITEMS:
            menu = _find_menu(menu_model, website, root_menu, url, names)
            values = {
                'name': name,
                'url': url,
                'sequence': sequence,
                'website_id': website.id,
                'parent_id': root_menu.id,
            }
            if menu:
                menu.write(values)
            else:
                menu_model.create(values)
