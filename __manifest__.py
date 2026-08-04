# -*- coding: utf-8 -*-

{
    "name": "Sale & Delivery Auto Emails",
    "version": "18.0.1.6.0",
    "category": "Sales",
    "summary": "Auto emails on website delivery address confirm and delivery validation",
    "depends": [
        "sale_management",
        "sale_stock",
        "stock",
        "mail",
        "website_sale",
    ],
    "data": [
        "data/mail_template.xml",
        "views/res_config_settings_views.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
