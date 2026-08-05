# -*- coding: utf-8 -*-

import json
import logging

from odoo.http import request, route
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.tools import str2bool

_logger = logging.getLogger(__name__)


class WebsiteSaleAutoEmail(WebsiteSale):
    """Send confirmation email when the delivery address is confirmed on the website.

    Native checkout / order status is unchanged — only an email is sent.
    """

    @route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def shop_confirm_order(self, **post):
        """Checkout "Confirm" after delivery address — send email if available."""
        # Keep a reference before super(): some flows may alter the session cart.
        order_sudo = request.website.sale_get_order()

        res = super().shop_confirm_order(**post)

        if not order_sudo:
            order_sudo = request.website.sale_get_order()
        if not order_sudo:
            last_order_id = request.session.get('sale_last_order_id')
            if last_order_id:
                order_sudo = request.env['sale.order'].sudo().browse(last_order_id).exists()

        if order_sudo:
            try:
                _logger.info(
                    "sale_stock_auto_email: shop_confirm_order trigger for order %s (%s)",
                    order_sudo.id,
                    order_sudo.name,
                )
                order_sudo._send_auto_confirmation_email()
            except Exception:
                _logger.exception(
                    "Failed to send auto confirmation email for order %s",
                    order_sudo.id,
                )
        else:
            _logger.warning(
                "sale_stock_auto_email: shop_confirm_order with no order found"
            )
        return res

    @route(
        '/shop/address/submit',
        type='http',
        methods=['POST'],
        auth='public',
        website=True,
        sitemap=False,
    )
    def shop_address_submit(
        self,
        partner_id=None,
        address_type='billing',
        use_delivery_as_billing=None,
        callback=None,
        required_fields=None,
        **form_data,
    ):
        """After a successful delivery address submit, send email if present."""
        use_delivery_as_billing_bool = str2bool(use_delivery_as_billing or 'false')
        is_delivery_step = (
            address_type == 'delivery'
            or use_delivery_as_billing_bool
        )

        result = super().shop_address_submit(
            partner_id=partner_id,
            address_type=address_type,
            use_delivery_as_billing=use_delivery_as_billing,
            callback=callback,
            required_fields=required_fields,
            **form_data,
        )

        if not is_delivery_step:
            return result

        order_sudo = request.website.sale_get_order()
        if not order_sudo:
            return result

        try:
            payload = json.loads(result)
        except (TypeError, ValueError, json.JSONDecodeError):
            return result

        # Native success response contains redirectUrl; errors do not.
        if not payload.get('redirectUrl'):
            return result

        try:
            _logger.info(
                "sale_stock_auto_email: address/submit trigger for order %s (%s)",
                order_sudo.id,
                order_sudo.name,
            )
            order_sudo._send_auto_confirmation_email()
        except Exception:
            _logger.exception(
                "Failed to send auto confirmation email for order %s",
                order_sudo.id,
            )
        return result
