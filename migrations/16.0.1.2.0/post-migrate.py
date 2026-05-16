"""Migración 1.2.0 — fuerza la asignación de íconos PNG a las categorías.

Razones del force=True:
 - La migración 1.1.0 generaba PNGs con struct/zlib manual; PIL puede
   haberlos rechazado silenciosamente en algunos entornos.
 - En 1.2.0 generamos los PNGs con Pillow (mismo motor que valida Odoo),
   por lo que la asignación es garantizada.
"""
from odoo import api, SUPERUSER_ID
from odoo.addons.web_asvetec.hooks import assign_category_icons


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    assign_category_icons(env, force=True)
