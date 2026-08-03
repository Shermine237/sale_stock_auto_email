# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    auto_confirmation_mail_sent = fields.Boolean(
        string="Auto confirmation email sent",
        copy=False,
        help="Technical flag to avoid sending the confirmation email twice.",
    )

    def action_confirm(self):
        """Backend confirmation only — website status flow stays fully native."""
        res = super().action_confirm()
        if not self.env.context.get("send_email"):
            self.filtered(
                lambda o: o.state in ("sale", "done")
            )._send_auto_confirmation_email()
        return res

    def _get_confirmation_template(self):
        """Use our template when Odoo itself sends a confirmation mail."""
        template = self.env.ref(
            "sale_stock_auto_email.mail_template_sale_order_confirmed",
            raise_if_not_found=False,
        )
        return template or super()._get_confirmation_template()

    def _get_auto_email_partner(self):
        """Prefer a partner that has an email (invoice / shipping as fallback)."""
        self.ensure_one()
        if self.partner_id.email:
            return self.partner_id
        if self.partner_shipping_id.email:
            return self.partner_shipping_id
        if self.partner_invoice_id.email:
            return self.partner_invoice_id
        commercial = self.partner_id.commercial_partner_id
        if commercial.email:
            return commercial
        return self.partner_id

    def _send_auto_confirmation_email(self):
        """Send confirmation email once, only if a customer email is available.

        Does not change the order state.
        """
        template = self.env.ref(
            "sale_stock_auto_email.mail_template_sale_order_confirmed",
            raise_if_not_found=False,
        )
        if not template:
            return

        for order in self:
            if order.auto_confirmation_mail_sent:
                continue
            partner = order._get_auto_email_partner()
            if not partner.email:
                continue
            order._send_order_notification_mail(template)
            order.auto_confirmation_mail_sent = True
