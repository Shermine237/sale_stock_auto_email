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
        res = super().action_confirm()
        # Website checkout without online payment uses
        # _send_payment_succeeded_for_order_mail (pending transaction).
        # Online payment / free cart uses send_email → native confirmation mail.
        # Backend confirm (no send_email): send here.
        if not self.env.context.get("send_email"):
            self.filtered(
                lambda o: o.state in ("sale", "done")
            )._send_auto_confirmation_email()
        return res

    def _get_confirmation_template(self):
        """Use our template when Odoo sends a confirmation mail (e.g. free orders)."""
        template = self.env.ref(
            "sale_stock_auto_email.mail_template_sale_order_confirmed",
            raise_if_not_found=False,
        )
        return template or super()._get_confirmation_template()

    def _send_payment_succeeded_for_order_mail(self):
        """Website place-order (no online payment → pending tx).

        In that flow the SO is NOT confirmed; Odoo marks it as quotation sent and
        calls this method. Send our confirmation email here (if the customer
        provided an email), instead of the generic payment email.
        """
        website_orders = self.filtered("website_id")
        other_orders = self - website_orders

        if website_orders:
            website_orders.with_context(
                force_user_recomputation=True
            )._compute_user_id()
            website_orders._send_auto_confirmation_email()

        if other_orders:
            super(SaleOrder, other_orders)._send_payment_succeeded_for_order_mail()

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
        """Send confirmation email once, only if a customer email is available."""
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
