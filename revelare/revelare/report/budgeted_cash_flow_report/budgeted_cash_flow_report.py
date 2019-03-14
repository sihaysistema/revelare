# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [{
	"fieldname": "budgeted_cash",
	"label": ("Budgeted Cash"),
	"fieldtype": "Link",
	"options": "Budgeted Cash Flow",
	"width": 300
	}], []
	return columns, data
