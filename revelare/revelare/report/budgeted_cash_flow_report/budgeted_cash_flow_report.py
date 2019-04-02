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
	# }], [['A']]
	# # [1, 2, 3, 4, 4, 5, 6, 7, 8, 9]
	# return columns, data

	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, company=filters.company)

	# currency = filters.presentation_currency or frappe.get_cached_value('Company',  filters.company,  "default_currency")

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, company=filters.company)
	data = [{
		"year_end_date": "2019-12-31",
		"parent_account": "",
		"dec_2019": 39.0,
		"account_type": "",
		"year_start_date": "2019-01-01",
		"has_value": True,
		"is_group": 1,
		"account": "1000 - UTILIZACI\xd3N DE FONDOS (ACTIVOS) - S",
		"currency": "GTQ",
		"total": "",
		"indent": 0.0,
		"include_in_gross": 0,
		"account_name": "1000 - UTILIZACI\xd3N DE FONDOS (ACTIVOS)",
		"opening_balance": 0.0
	},
	{
		"year_end_date": "2019-12-31",
		"parent_account": "1300 - Cuentas por cobrar - S",
		"dec_2019": 39.0,
		"account_type": "Receivable",
		"year_start_date": "2019-01-01",
		"has_value": True,
		"is_group": 0,
		"account": "1310 - DEUDORES VARIOS - S",
		"currency": "GTQ",
		"total": 39.0,
		"indent": 2.0,
		"include_in_gross": 0,
		"account_name": "1310 - DEUDORES VARIOS",
		"opening_balance": 0.0
	},
	{
		"total": 39.0,
		"currency": "GTQ",
		"account": "Total Asset (Debit)",
		"dec_2019": 39.0,
		"account_name": "Total Asset (Debit)"
	}]

	# chart = get_chart_data(filters, columns, asset, liability, equity)
	# frappe.msgprint(_(str(columns)))
	return columns, data


def get_chart_data(filters, columns, asset, liability, equity):
	labels = [d.get("label") for d in columns[2:]]

	asset_data, liability_data, equity_data = [], [], []

	for p in columns[2:]:
		if asset:
			asset_data.append(asset[-2].get(p.get("fieldname")))
		if liability:
			liability_data.append(liability[-2].get(p.get("fieldname")))
		if equity:
			equity_data.append(equity[-2].get(p.get("fieldname")))

	datasets = []
	if asset_data:
		datasets.append({'name':'Assets', 'values': asset_data})
	if liability_data:
		datasets.append({'name':'Liabilities', 'values': liability_data})
	if equity_data:
		datasets.append({'name':'Equity', 'values': equity_data})

	chart = {
		"data": {
			'labels': labels,
			'datasets': datasets
		}
	}

	if not filters.accumulated_values:
		chart["type"] = "bar"
	else:
		chart["type"] = "line"

	return chart