from odoo import api, SUPERUSER_ID
from odoo.addons.web_asvetec.hooks import assign_category_icons


def migrate(cr, version):
    """Assign coloured PNG icons to ASVETEC public categories.
    Runs when upgrading the module to version 16.0.1.1.0."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    assign_category_icons(env)
