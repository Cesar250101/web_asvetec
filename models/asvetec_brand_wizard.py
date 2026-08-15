from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AsvetecBrandImportWizard(models.TransientModel):
    _name = 'asvetec.brand.import.wizard'
    _description = 'Carga múltiple de logos ASVETEC'

    website_id = fields.Many2one(
        'website', string='Sitio web',
        help='Déjelo vacío para mostrar los logos en todos los sitios web.')
    attachment_ids = fields.Many2many('ir.attachment', string='Archivos de logos', required=True)

    @api.model
    def _default_website(self):
        return self.env['website'].get_current_website()

    def action_import(self):
        self.ensure_one()
        if not self.attachment_ids:
            raise UserError(_('Seleccione al menos un logo.'))
        Brand = self.env['asvetec.brand']
        for attachment in self.attachment_ids:
            filename = attachment.name or _('Marca')
            name = filename.rsplit('.', 1)[0]
            Brand.create({
                'name': name,
                'website_id': self.website_id.id,
                'image_1920': attachment.datas,
                'is_default_logo': False,
            })
        return {'type': 'ir.actions.act_window_close'}


class AsvetecBrandSettingsWizard(models.TransientModel):
    _name = 'asvetec.brand.settings.wizard'
    _description = 'Ajustes de logos ASVETEC'

    website_id = fields.Many2one('website', string='Sitio web', required=True,
                                 default=lambda self: self._default_website())
    show_default_logos = fields.Boolean(string='Mostrar logos predeterminados')

    @api.model
    def _default_website(self):
        return self.env['website'].get_current_website()

    @api.model
    def default_get(self, fields_list):
        values = super().default_get(fields_list)
        website = self.env['website'].browse(values.get('website_id'))
        if website:
            values['show_default_logos'] = website.asv_show_default_brand_logos
        return values

    def action_save(self):
        self.ensure_one()
        self.website_id.asv_show_default_brand_logos = self.show_default_logos
        return {'type': 'ir.actions.act_window_close'}
