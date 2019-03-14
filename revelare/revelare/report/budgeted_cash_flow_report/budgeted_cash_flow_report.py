# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	columns, data = [{
		"fieldname": "party",
		"label": ("Party"),
		"fieldtype": "Data",
		"options": "Budgeted Cash Flow",
		"width": 300
	}], []
	# [1, 2, 3, 4, 4, 5, 6, 7, 8, 9]
	return columns, data
