from odoo import http
from odoo.http import request


class AsvController(http.Controller):

    @http.route('/asvetec', type='http', auth='public', website=True)
    def home(self):
        # Renderizamos usando el ID numérico del view (via env.ref) en lugar del
        # xml_id string, para evitar que el mecanismo COW del editor de Odoo
        # rompa la búsqueda por key cuando la página tiene website_id asignado.
        view = request.env.ref('web_asvetec.asv_home')
        return request.render(view.id)

    @http.route('/asvetec/cotizar', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def cotizar(self, **kwargs):
        vals = {
            'name': 'Cotización web: %s' % kwargs.get('name', ''),
            'contact_name': kwargs.get('name', ''),
            'email_from': kwargs.get('email', ''),
            'phone': kwargs.get('phone', ''),
            'partner_name': kwargs.get('company', ''),
            'description': kwargs.get('message', ''),
            'tag_ids': [],
        }
        try:
            request.env['crm.lead'].sudo().create(vals)
        except Exception:
            request.env['mail.mail'].sudo().create({
                'subject': 'Cotización web ASVETEC — %s' % kwargs.get('name', ''),
                'body_html': '<p>%s</p>' % kwargs.get('message', ''),
                'email_to': 'ventas@asvetec.cl',
                'email_from': kwargs.get('email', ''),
            }).send()
        return request.render('web_asvetec.asv_cotizar_ok')
