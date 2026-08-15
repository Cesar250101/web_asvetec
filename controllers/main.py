import base64

from odoo import http
from odoo.http import request


class AsvController(http.Controller):

    @staticmethod
    def _image_response(image):
        image = base64.b64decode(image)
        if image.startswith(b'\x89PNG'):
            mimetype = 'image/png'
        elif image.startswith(b'\xff\xd8'):
            mimetype = 'image/jpeg'
        elif image.startswith(b'GIF8'):
            mimetype = 'image/gif'
        elif image.lstrip().startswith(b'<svg'):
            mimetype = 'image/svg+xml'
        else:
            mimetype = 'image/webp'
        return request.make_response(image, headers=[
            ('Content-Type', mimetype),
            ('Cache-Control', 'public, max-age=3600'),
        ])

    @http.route('/asvetec/brands', type='json', auth='public', website=True)
    def brands(self):
        """Logos administrables del carrusel, filtrados por el sitio actual."""
        # El contexto del sitio puede pedir bin_size y devolver sólo el peso
        # del archivo. Para decidir y servir logos se necesita el binario real.
        brands = request.env['asvetec.brand'].sudo().with_context(bin_size=False).search([
            ('active', '=', True),
        ])
        visible_brands = brands.filtered(
            lambda brand: brand.image_1920
            or not brand.is_default_logo
            or request.website.asv_show_default_brand_logos
        )
        return {
            'brands': [{
                'id': brand.id,
                'name': brand.name,
                'image_url': (
                    '/asvetec/brand-logo/%s?v=%s' % (
                        brand.id, brand.write_date.strftime('%Y%m%d%H%M%S'),
                    )
                    if brand.image_1920 else False
                ),
                'website_url': brand.website_url or False,
            } for brand in visible_brands],
        }

    @http.route('/asvetec/brand-logo/<int:brand_id>', type='http', auth='public', website=True)
    def brand_logo(self, brand_id, **kwargs):
        """Entrega el logo al sitio público sin exponer el modelo de gestión."""
        brand = request.env['asvetec.brand'].sudo().with_context(
            bin_size=False,
        ).browse(brand_id).exists()
        if not brand or not brand.active or not brand.image_1920:
            return request.not_found()

        return self._image_response(brand.image_1920)

    @http.route('/asvetec/category-images', type='json', auth='public', website=True)
    def category_images(self):
        """Devuelve únicamente las imágenes cargadas por el usuario.

        Las imágenes marcadas como generadas por ASVETEC corresponden al
        respaldo de iconos y no deben reemplazar el SVG de la tarjeta.
        """
        categories = request.env['product.public.category'].sudo().search([
            ('image_1920', '!=', False),
        ])
        return {
            category.id: '/web/image/product.public.category/%s/image_1920' % category.id
            for category in categories
            if category._asv_has_uploaded_category_image()
        }

    @http.route('/asvetec/cotizar', type='http', auth='public', website=True,
                methods=['POST'], csrf=True)
    def cotizar(self, **kwargs):
        category = kwargs.get('category', '')
        message = kwargs.get('message', '')
        description = (
            'Categoría de interés: %s\n\n%s' % (category, message)
            if category else message
        )
        vals = {
            'name': 'Cotización web: %s' % kwargs.get('name', ''),
            'contact_name': kwargs.get('name', ''),
            'email_from': kwargs.get('email', ''),
            'phone': kwargs.get('phone', ''),
            'partner_name': kwargs.get('company', ''),
            'description': description,
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
