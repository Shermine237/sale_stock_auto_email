# -*- coding: utf-8 -*-

from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    auto_confirmation_email_from = fields.Char(
        string="Website Confirmation Sender Email",
        help="Email address used as sender for this module's website checkout confirmation email.",
    )
