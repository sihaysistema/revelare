# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Cash Flow"),
			"items": [
				{
					"type": "doctype",
					"name": "Budgeted Cash Flow",
					"description": _("Entries budgeted cash flow.")
				}
			]
		},
		{
			"label": _("Setup"),
			"icon": "fa fa-cog",
			"items": [
				{
					"type": "doctype",
					"name": "Configuration",
					"description": _("General Configuration to Revelare.")
				}
			]
		},
		{
			"label": _("Analytics"),
			"icon": "fa fa-table",
			"items": [
				{
					"type": "page",
					"name": "sales-analytics-2",
					"label": _("Sales Analytics 2"),
					"icon": "fa fa-bar-chart",
				}
			]
		},
	]