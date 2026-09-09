"""Elimina la numeración decorativa de las categorías guardadas por Website."""
from lxml import etree

from odoo import api, SUPERUSER_ID


_CLASS_XPATH = (
    "contains(concat(' ', normalize-space(@class), ' '), ' %s ')"
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].with_context(active_test=False).search([
        ('arch_db', 'ilike', 's_asv_categories'),
    ])

    for view in views:
        try:
            root = etree.fromstring(view.arch_db.encode('utf-8'))
        except (etree.XMLSyntaxError, AttributeError):
            continue

        changed = False
        categories = root.xpath("//*[%s]" % (_CLASS_XPATH % 's_asv_categories'))
        for category_section in categories:
            numbers = category_section.xpath(
                ".//*[%s]" % (_CLASS_XPATH % 'asv-cat-num')
            )
            for number in numbers:
                parent = number.getparent()
                if parent is not None:
                    parent.remove(number)
                    changed = True

        if changed:
            view.with_context(lang=None).write({
                'arch_db': etree.tostring(root, encoding='unicode'),
            })
