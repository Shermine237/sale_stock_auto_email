# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        # Website / payment already send via context send_email →
        # _send_order_confirmation_mail (see _get_confirmation_template).
        # Backend confirmation has no send_email: send our mail here.
        if not self.env.context.get("send_email"):
            self.filtered(
                lambda o: o.state in ("sale", "done")
            )._send_auto_confirmation_email()
        return res

    def _get_confirmation_template(self):
        """Use our auto-email template for website + payment confirmations.

        Website payments call ``action_confirm`` with ``send_email=True``, which
        triggers ``_send_order_confirmation_mail`` → this method.
        """
        template = self.env.ref(
            "sale_stock_auto_email.mail_template_sale_order_confirmed",
            raise_if_not_found=False,
        )
        return template or super()._get_confirmation_template()

    def _get_auto_email_partner(self):
        """Prefer a partner that has an email (invoice contact as fallback)."""
        self.ensure_one()
        if self.partner_id.email:
            return self.partner_id
        if self.partner_invoice_id.email:
            return self.partner_invoice_id
        commercial = self.partner_id.commercial_partner_id
        if commercial.email:
            return commercial
        return self.partner_id

    def _send_auto_confirmation_email(self):
        """Send via native helper (handles sudo / SUPERUSER for website users)."""
        template = self.env.ref(
            "sale_stock_auto_email.mail_template_sale_order_confirmed",
            raise_if_not_found=False,
        )
        if not template:
            return

        for order in self:
            if not order._get_auto_email_partner().email:
                continue
            order._send_order_notification_mail(template)
