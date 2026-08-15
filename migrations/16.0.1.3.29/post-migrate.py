"""Hace visible en el panel derecho la imagen elegida en el editor web."""
from lxml import etree

from odoo import api, SUPERUSER_ID


_CLASS_XPATH = (
    "contains(concat(' ', normalize-space(@class), ' '), ' %s ')"
)


def _set_background_image(style, value):
    declarations = []
    for declaration in (style or '').split(';'):
        declaration = declaration.strip()
        if declaration and not declaration.lower().startswith('background-image:'):
            declarations.append(declaration)
    declarations.append('background-image: %s' % value)
    return '; '.join(declarations) + ';'


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].with_context(active_test=False).search([
        ('arch_db', 'ilike', 'asv-hero-photo'),
    ])

    for view in views:
        try:
            root = etree.fromstring(view.arch_db.encode('utf-8'))
        except (etree.XMLSyntaxError, AttributeError):
            continue

        changed = False
        heroes = root.xpath("//*[%s]" % (_CLASS_XPATH % 's_asv_hero'))
        for hero in heroes:
            photos = hero.xpath(".//*[%s]" % (_CLASS_XPATH % 'asv-hero-photo'))
            for photo in photos:
                new_style = _set_background_image(photo.get('style'), 'inherit')
                if photo.get('style') != new_style:
                    photo.set('style', new_style)
                    changed = True

        if changed:
            view.with_context(lang=None).write({
                'arch_db': etree.tostring(root, encoding='unicode'),
            })
