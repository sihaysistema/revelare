# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _
import frappe


def get_data():
    return [
        {
            "label": _("Sales Estimates"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Item Availability Estimate",
                    "description": _("Item Availability Estimate lists"),
                    "onboard": 1,
                },
                {
                    "type": "report",
                    "name": "Sales Item Availability",
                    "description": _("Sales Item Availability Report"),
                    "is_query_report": True,
                    "onboard": 1,
                },
            ]

        },
        {
            "label": _("Cash Flow"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Budgeted Cash Flow",
                    "description": _("Entries budgeted cash flow."),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Budgeted Cash Flow Report",
                    "description": _("Report Cash Flow"),
                    "onboard": 1
                },
                {
                    "type": "doctype",
                    "name": "Category Cash Flow Group",
                    "link": "Tree/Category Cash Flow Group",
                    "description": _("Manage Categories Group Tree."),
                    "onboard": 1
                }
            ]
        },
        {
            "label": _("Analytics"),
            "items": [
                {
                    "type": "page",
                    "name": "sales-analytics-2",
                    "description": _("Sales Analytics 2.0"),
                    "onboard": 1,
                }
            ]
        },
        {
            "label": _("Reports"),
            "items": [
                {
                    "type": "report",
                    "name": "Purchase Ledger",
                    "description": _("Purchase Ledger"),
                    "is_query_report": True,
                    "onboard": 1,
                },
                {
                    "type": "report",
                    "name": "General Ledger Report",
                    "description": _("General Ledger Report"),
                    "is_query_report": True,
                    "onboard": 1,
                },
                {
                    "type": "report",
                    "name": "Daily Book Report",
                    "description": _("Daily Book Report"),
                    "is_query_report": True,
                    "onboard": 1,
                },
            ]
        },
        {
            "label": _("Agriculture Reports"),
            "items": [
                {
                    "type": "report",
                    "name": "Production Report",
                    "description": _("Production Report"),
                    "is_query_report": True,
                    "onboard": 1,
                }
            ]
        },
        {
            "label": _("Delivery Note by Item with 4 Item Column Totalization"),
            "items": [
                {
                    "type": "report",
                    "name": "Delivery Note By Item",
                    "description": _("Delivery Note By Item"),
                    "is_query_report": True,
                    "onboard": 1,
                }
            ]
        },
        {
            "label": _("Configuration"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Revelare Configuration",
                    "description": _("General Configuration for Revelare"),
                    "onboard": 1,
                }
            ]
        },
        {
            "label": _("Tabular Entry Tools"),
            "items": [
                {
                    "type": "report",
                    "name": "tabular-delivery-not",
                    "description": _("Delivery Note Tabular Entry"),
                    "is_query_report": True,
                    "onboard": 1,
                }
            ]
        },
        {
            "label": _("Sales Order per Stock Entry Item"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Sales Order per Stock Entry Detail",
                    "description": _("Sales Order per Stock Entry Detail"),
                    "onboard": 1,
                }
            ]
        },
    ]