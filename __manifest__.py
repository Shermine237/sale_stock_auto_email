# -*- coding: utf-8 -*-

{
    "name": "Sale & Delivery Auto Emails",
    "version": "18.0.1.4.0",
    "category": "Sales",
    "summary": "Send automatic emails on order confirmation and delivery validation",
    "depends": [
        "sale_management",
        "sale_stock",
        "stock",
        "mail",
        "website_sale",
    ],
    "data": [
        "data/mail_template.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
