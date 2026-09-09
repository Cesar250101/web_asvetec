"""Actualiza las copias Website del footer ASVETEC creadas por el editor."""
from odoo import api, SUPERUSER_ID


_REPLACEMENTS = (
    (
        "website and website.name == 'ASVETEC'",
        "website and (website.name or '').lower() == 'asvetec'",
    ),
    ('href="/asvetec#nosotros"', 'href="/#nosotros"'),
    ('href="/asvetec#servicios"', 'href="/#servicios"'),
    ('href="/asvetec#contacto"', 'href="/#contacto"'),
    ('href="/asvetec"', 'href="/"'),
)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    footer_views = env['ir.ui.view'].with_context(active_test=False).search([
        ('key', '=', 'web_asvetec.asv_footer'),
    ])

    for view in footer_views:
        arch_db = view.arch_db
        updated_arch = arch_db
        for old, new in _REPLACEMENTS:
            updated_arch = updated_arch.replace(old, new)
        if updated_arch != arch_db:
            view.write({'arch_db': updated_arch})
