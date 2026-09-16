"""Corrige la migracion 16.0.1.3.40.

Un proceso Odoo con autoreload activo (VS Code/debugpy, ver
.vscode/launch.json) detecto los cambios de archivo de esa version y disparo
"-u web_asvetec" por su cuenta a las 19:25 del 2026-09-15, antes de que el
diseño quedara cerrado y sin pasar por ninguna autorizacion explicita. Corrio
con una version intermedia del codigo y dejo dos problemas, confirmados por
lectura directa de Postgres:

1. El script de 16.0.1.3.40 usa env['product.template'].search(...), que por
   defecto excluye productos archivados (active=False). De los 5 productos
   con website_ribbon_id seteado, 2 estaban archivados y quedaron fuera de la
   tabla de relacion nueva (product_template_asv_ribbon_rel tenia 3 filas en
   vez de 5).
2. Como el gate de version de Odoo solo dispara post-migrate una vez por
   numero de version, y ir_module_module ya habia quedado marcado en
   16.0.1.3.40 tras esa corrida automatica, un "-u" posterior con el codigo
   definitivo no volvio a ejecutar el script -- la columna entera vieja
   website_ribbon_id nunca llego a eliminarse.

Este script reconcilia la relacion Many2many con la columna vieja (incluyendo
productos archivados, via active_test=False) sin duplicar lo ya migrado, y
recien entonces elimina la columna huerfana.
"""
from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    cr.execute("""
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'product_template' AND column_name = 'website_ribbon_id'
    """)
    if not cr.fetchone():
        return

    cr.execute("""
        SELECT id, website_ribbon_id FROM product_template
        WHERE website_ribbon_id IS NOT NULL
    """)
    rows = cr.fetchall()

    env = api.Environment(cr, SUPERUSER_ID, {'active_test': False})
    for template_id, ribbon_id in rows:
        env['product.template'].browse(template_id).website_ribbon_id = [(4, ribbon_id)]
    env.flush_all()

    cr.execute('ALTER TABLE product_template DROP COLUMN website_ribbon_id')
