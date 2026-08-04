# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_auto_confirmation_email_from = fields.Char(
        string="Website Confirmation Sender Email",
        related="website_id.auto_confirmation_email_from",
        readonly=False,
    )
