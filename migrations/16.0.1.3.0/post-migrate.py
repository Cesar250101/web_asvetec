"""Migración 1.3.0 — elimina el ítem de menú 'Contacto → /asvetec#contacto'
del sitio ASVETEC para dejar solo el formulario nativo /contactus."""
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    website = env['website'].search([('name', '=', 'ASVETEC')], limit=1)
    if not website:
        return

    # Elimina el ítem de menú que apuntaba al snippet interno /asvetec#contacto
    old_menu = env['website.menu'].search([
        ('website_id', '=', website.id),
        ('url', '=', '/asvetec#contacto'),
    ])
    if old_menu:
        old_menu.unlink()
        _logger.info('ASVETEC: eliminado ítem de menú /asvetec#contacto')

    # Si no existe ya un ítem apuntando a /contactus, lo crea
    existing = env['website.menu'].search([
        ('website_id', '=', website.id),
        ('url', '=', '/contactus'),
    ], limit=1)
    if not existing:
        top_menu = website.menu_id
        if top_menu:
            env['website.menu'].create({
                'name': 'Contáctenos',
                'url': '/contactus',
                'parent_id': top_menu.id,
                'website_id': website.id,
                'sequence': 90,
            })
            _logger.info('ASVETEC: creado ítem de menú /contactus')
