# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns, get_data)

def execute(filters=None):
	# columns, data = [{
	# 	"fieldname": "party",
	# 	"label": _("Party"),
	# 	"fieldtype": "Data",
	# 	"options": "Budgeted Cash Flow",
	# 	"width": 300
	# }], []
	# # [1, 2, 3, 4, 4, 5, 6, 7, 8, 9]
	# return columns, data

	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
		filters.periodicity, company=filters.company)

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, company=filters.company)
	data = []
	return columns, data