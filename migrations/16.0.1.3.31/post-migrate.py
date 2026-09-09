"""Elimina adornos vacíos del hero de las vistas guardadas por Website."""
from lxml import etree

from odoo import api, SUPERUSER_ID


_CLASS_XPATH = (
    "contains(concat(' ', normalize-space(@class), ' '), ' %s ')"
)
_REMOVED_CLASSES = ('asv-hero-badge', 'asv-hero-float-card')


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].with_context(active_test=False).search([
        ('arch_db', 'ilike', 's_asv_hero'),
    ])

    for view in views:
        try:
            root = etree.fromstring(view.arch_db.encode('utf-8'))
        except (etree.XMLSyntaxError, AttributeError):
            continue

        changed = False
        heroes = root.xpath("//*[%s]" % (_CLASS_XPATH % 's_asv_hero'))
        for hero in heroes:
            for class_name in _REMOVED_CLASSES:
                elements = hero.xpath(".//*[%s]" % (_CLASS_XPATH % class_name))
                for element in elements:
                    parent = element.getparent()
                    if parent is not None:
                        parent.remove(element)
                        changed = True

        if changed:
            view.with_context(lang=None).write({
                'arch_db': etree.tostring(root, encoding='unicode'),
            })
