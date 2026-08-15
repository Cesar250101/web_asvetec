"""Propaga el fondo editable del Hero hasta el panel fotográfico."""
from lxml import etree

from odoo import api, SUPERUSER_ID


def _has_class(element, class_name):
    return class_name in (element.get('class') or '').split()


def _set_background_inherit(element):
    declarations = []
    for declaration in (element.get('style') or '').split(';'):
        declaration = declaration.strip()
        if declaration and not declaration.lower().startswith('background-image:'):
            declarations.append(declaration)
    declarations.append('background-image: inherit')
    element.set('style', '; '.join(declarations) + ';')


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    views = env['ir.ui.view'].with_context(active_test=False).search([
        ('arch_db', 'ilike', 'asv-hero-grid'),
    ])

    for view in views:
        try:
            root = etree.fromstring(view.arch_db.encode('utf-8'))
        except (etree.XMLSyntaxError, AttributeError):
            continue

        changed = False
        for hero in root.iter():
            if not _has_class(hero, 's_asv_hero'):
                continue
            for element in hero.iterdescendants():
                if _has_class(element, 'asv-hero-grid'):
                    old_style = element.get('style')
                    _set_background_inherit(element)
                    changed = changed or element.get('style') != old_style

        if changed:
            view.with_context(lang=None).write({
                'arch_db': etree.tostring(root, encoding='unicode'),
            })
