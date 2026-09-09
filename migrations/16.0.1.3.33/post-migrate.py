"""Corrige la traducción española de la cinta de disponibilidad ASVETEC."""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    ribbons = env['product.ribbon'].with_context(lang='en_US').search([
        ('html', 'ilike', 'en stock'),
    ])

    for ribbon in ribbons:
        # html es traducible. Copiar el HTML fuente conserva cualquier marcado
        # de la cinta y evita que el sitio es_ES muestre "Fuera de stock".
        ribbon.with_context(lang='es_ES').write({
            'html': ribbon.with_context(lang='en_US').html,
        })
