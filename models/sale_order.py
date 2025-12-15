# -*- coding: utf-8 -*-

import base64

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
                    attachment_id = False
                    report = self.env.ref("sale.action_report_saleorder", raise_if_not_found=False)
                    if report:
                        pdf_content, _content_type = report._render_qweb_pdf([order.id])
                        attachment = self.env["ir.attachment"].create(
                            {
                                "name": f"{order.name}.pdf",
                                "type": "binary",
                                "datas": base64.b64encode(pdf_content),
                                "mimetype": "application/pdf",
                                "res_model": order._name,
                                "res_id": order.id,
                            }
                        )
                        attachment_id = attachment.id

                    email_values = None
                    if attachment_id:
                        email_values = {"attachment_ids": [(4, attachment_id)]}

                    template.send_mail(
                        order.id,
                        force_send=True,
                        raise_exception=False,
                        email_values=email_values,
                    )
        return res
