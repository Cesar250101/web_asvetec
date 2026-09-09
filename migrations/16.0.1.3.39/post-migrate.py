"""Recrea la navegación ASVETEC desde el menú raíz efectivo del sitio."""
from odoo import api, SUPERUSER_ID


_MENU_ITEMS = (
    ('Inicio', '/', 10),
    ('Catálogo', '/shop', 20),
    ('Quiénes somos', '/#nosotros', 30),
    ('Servicios', '/#servicios', 40),
    ('Contacto', '/#contacto', 50),
)
_MANAGED_NAMES = frozenset(
    ('Inicio', 'Tienda', 'Catálogo', 'Contáctenos', 'Contacto',
     'Quiénes somos', 'Servicios')
)
_MANAGED_URLS = frozenset(
    ('/', '/shop', '/contactus', '/#nosotros', '/#servicios', '/#contacto')
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu_model = env['website.menu']
    websites = env['website'].search([]).filtered(
        lambda website: (website.name or '').lower() == 'asvetec'
    )

    for website in websites:
        root_menu = website.menu_id
        if not root_menu:
            continue

        managed_children = root_menu.child_id.filtered(
            lambda menu: menu.name in _MANAGED_NAMES or menu.url in _MANAGED_URLS
        )
        managed_children.unlink()

        for name, url, sequence in _MENU_ITEMS:
            menu_model.create({
                'name': name,
                'url': url,
                'sequence': sequence,
                'website_id': website.id,
                'parent_id': root_menu.id,
            })
