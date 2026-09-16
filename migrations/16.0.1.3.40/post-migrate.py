"""Migra website_ribbon_id de Many2one a Many2many sin perder cintas ya asignadas.

En este punto de la carga del modulo, el registro ORM ya trata
website_ribbon_id como Many2many (el esquema de product_template_asv_ribbon_rel
ya se creo), pero la columna entera vieja "website_ribbon_id" de
product_template todavia no fue tocada por nadie -- Odoo no la dropea
automaticamente al cambiar el tipo de un campo (confirmado leyendo
odoo/fields.py::Many2many.update_db, que solo crea la tabla de relacion si
falta, y odoo/addons/base/models/ir_model.py::_reflect_fields, que actualiza
la fila de ir_model_fields in place sin pasar por unlink()/_drop_column()).
Por eso se lee con SQL directo (el ORM ya no puede acceder al valor viejo) y,
una vez copiado, se elimina la columna huerfana para no dejar un rastro
confuso con el mismo nombre que el campo nuevo.
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

    env = api.Environment(cr, SUPERUSER_ID, {})
    for template_id, ribbon_id in rows:
        env['product.template'].browse(template_id).website_ribbon_id = [(4, ribbon_id)]
    env.flush_all()

    cr.execute('ALTER TABLE product_template DROP COLUMN website_ribbon_id')
