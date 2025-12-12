# -*- coding: utf-8 -*-

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        res = super().button_validate()
        template = self.env.ref(
            "sale_stock_auto_email.mail_template_picking_done",
            raise_if_not_found=False,
        )
        if template:
            for picking in self:
                # Only for outgoing deliveries (customer shipments)
                if picking.picking_type_code != "outgoing":
                    continue

                partner = picking.partner_id
                if not partner or not partner.email:
                    continue

                template.send_mail(picking.id, force_send=True, raise_exception=False)
        return res
