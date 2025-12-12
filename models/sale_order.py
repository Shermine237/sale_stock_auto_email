# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        template = self.env.ref(
            "sale_stock_auto_email.mail_template_sale_order_confirmed",
            raise_if_not_found=False,
        )
        if template:
            for order in self:
                if order.partner_id and order.partner_id.email:
                    template.send_mail(order.id, force_send=True, raise_exception=False)
        return res
