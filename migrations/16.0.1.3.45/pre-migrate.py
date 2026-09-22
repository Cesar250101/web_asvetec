"""Adopta bajo un id externo fijo la cinta 'En stock' que usa
s_asv_featured_products.xml, para dejar de identificarla por texto.

Hasta esta version, el snippet "Productos destacados" ubicaba la cinta con
env['product.ribbon'].search([('html', 'ilike', 'en stock')]) (con
lang='en_US', ver migrations/16.0.1.3.33). Esa cinta se creo a mano desde el
backend en su momento y nunca tuvo un ir.model.data asociado, asi que
renombrar su texto desde Comercio electronico > Productos > Cintas rompia
silenciosamente la seccion (dejaba de encontrarla y la grilla quedaba vacia).

Este script corre en pre-migrate, es decir ANTES de que Odoo cargue
data/product_ribbon_data.xml (que declara <record id="ribbon_en_stock">).
Si encuentra la cinta existente por el criterio de busqueda viejo y todavia
no existe el id externo nuevo, crea el ir.model.data que la adopta. Cuando el
cargador de datos llegue al record de data/product_ribbon_data.xml va a
encontrar ese id ya registrado, reusar el mismo res_id y, por noupdate=1, no
tocar el texto/colores reales ya configurados. Idempotente: no hace nada si
el id externo ya existe (reinstalaciones o -u repetidos) ni si no hay ninguna
cinta que matchee el criterio viejo (instalacion nueva sin esa cinta).
"""
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

_XMLID_MODULE = 'web_asvetec'
_XMLID_NAME = 'ribbon_en_stock'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    existing = env['ir.model.data'].search([
        ('module', '=', _XMLID_MODULE),
        ('name', '=', _XMLID_NAME),
    ], limit=1)
    if existing:
        _logger.info(
            "web_asvetec: %s.%s ya existe (res_id=%s); nada que adoptar.",
            _XMLID_MODULE, _XMLID_NAME, existing.res_id,
        )
        return

    ribbon = env['product.ribbon'].with_context(lang='en_US').search([
        ('html', 'ilike', 'en stock'),
    ], order='id asc', limit=1)
    if not ribbon:
        _logger.info(
            "web_asvetec: no se encontro ninguna cinta 'en stock' que adoptar "
            "bajo %s.%s (instalacion nueva); data/product_ribbon_data.xml "
            "creara una cinta propia con ese id.",
            _XMLID_MODULE, _XMLID_NAME,
        )
        return

    env['ir.model.data'].create({
        'module': _XMLID_MODULE,
        'name': _XMLID_NAME,
        'model': 'product.ribbon',
        'res_id': ribbon.id,
        'noupdate': True,
    })
    _logger.info(
        "web_asvetec: cinta product.ribbon(%s) adoptada bajo %s.%s.",
        ribbon.id, _XMLID_MODULE, _XMLID_NAME,
    )
