# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint
from erpnext.accounts.report.financial_statements import (get_period_list, get_data)

def execute(filters=None):

	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, company=filters.company)

	# currency = filters.presentation_currency or frappe.get_cached_value('Company',  filters.company,  "default_currency")

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, company=filters.company)
	data = [{
		"total": 0,
		"currency": "GTQ",
		"party_cash_flow": "<b>Saldo Inicial</b>",
		# "dec_2019": 39.0,
	},
	{
		"currency": "GTQ",
		"party_cash_flow": "<b>INGRESOS</b>",
	}
	# {
	# 	"year_end_date": "2019-12-31",
	# 	"parent_account": "",
	# 	"dec_2019": 39.0,
	# 	"account_type": "",
	# 	"year_start_date": "2019-01-01",
	# 	"has_value": True,
	# 	"is_group": 1,
	# 	"party_cash_flow": "1000 - UTILIZACI\xd3N DE FONDOS (ACTIVOS) - S",
	# 	"currency": "GTQ",
	# 	"total": "",
	# 	"indent": 0.0,
	# 	"include_in_gross": 0,
	# 	"account_name": "1000 - UTILIZACI\xd3N DE FONDOS (ACTIVOS)",
	# 	"opening_balance": 0.0
	# },
	# {
	# 	"year_end_date": "2019-12-31",
	# 	"parent_account": "1300 - Cuentas por cobrar - S",
	# 	"dec_2019": 39.0,
	# 	"account_type": "Receivable",
	# 	"year_start_date": "2019-01-01",
	# 	"has_value": True,
	# 	"is_group": 0,
	# 	"party_cash_flow": "1310 - DEUDORES VARIOS - S",
	# 	"currency": "GTQ",
	# 	"total": 39.0,
	# 	"indent": 1.0,
	# 	"include_in_gross": 0,
	# 	"account_name": "1310 - DEUDORES VARIOS",
	# 	"opening_balance": 0.0
	# },
	# {
	# 	"total": 39.0,
	# 	"currency": "GTQ",
	# 	"party_cash_flow": "Total Ingresos",
	# 	"dec_2019": 39.0
	# }
	]

	datos_registro = get_data_cash_flow(filters.company)
	data_preparada = prepare_data(datos_registro, period_list, 'GTQ')
	add_total_row(data_preparada, period_list, 'GTQ')
	data.extend(data_preparada)

	chart = get_chart_data(filters, columns, datos_registro)

	return columns, data, chart


def get_chart_data(filters, columns, datos_registro):
	labels = [d.get("label") for d in columns[2:]]

	asset_data, liability_data, equity_data = [], [], []

	# for p in columns[2:]:
	# 	asset_data.append()


	datasets = []
	# if asset_data:
	datasets.append({'name':'Assets', 'values': ['A', 'B', 'C', 'D']})
	# if liability_data:
	# 	datasets.append({'name':'Liabilities', 'values': liability_data})
	# if equity_data:
	# 	datasets.append({'name':'Equity', 'values': equity_data})

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


def get_columns(periodicity, period_list, accumulated_values=1, company=None):
	columns = [{
		"fieldname": "party_cash_flow",
		"label": _("Party Cash Flow"),
		"fieldtype": "Link",
		"options": "Budgeted Cash Flow",
		"width": 300
	}]
	if company:
		columns.append({
			"fieldname": "currency",
			"label": _("Currency"),
			"fieldtype": "Link",
			"options": "Currency",
			"hidden": 1
		})
	for period in period_list:
		columns.append({
			"fieldname": period.key,
			"label": period.label,
			"fieldtype": "Currency",
			"options": "currency",
			"width": 150
		})
	if periodicity!="Yearly":
		if not accumulated_values:
			columns.append({
				"fieldname": "total",
				"label": _("Total"),
				"fieldtype": "Currency",
				"width": 150
			})

	return columns


def prepare_data(reg_chash_flow, period_list, company_currency):
	data = []
	year_start_date = period_list[0]["year_start_date"].strftime("%Y-%m-%d")
	year_end_date = period_list[-1]["year_end_date"].strftime("%Y-%m-%d")

	for d in reg_chash_flow:
		# add to output
		has_value = False
		total = 0
		row = frappe._dict({
			"party_cash_flow": _(d.party),
			"indent": flt(1),
			"year_start_date": year_start_date,
			"year_end_date": year_end_date,
			"currency": company_currency,
			"is_group": 0,
			# "opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be=="Debit" else -1),
			"total": d.paid_amount,
		})
		for period in period_list:
			if d.get(period.key):
				# change sign based on Debit or Credit, since calculation is done using (debit - credit)
				d[period.key] *= -1

			if d.posting_date <= period.to_date:
				row[period.key] = flt(d.paid_amount)
				# frappe.msgprint(_(str(row[period.key])))
			else:
				row[period.key] = 0

		row["has_value"] = has_value
		row["total"] = total
		data.append(row)

	return data


def get_data_cash_flow(company):
	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': company, 'status_payment': 'Unpaid'},
										fieldname=['name', 'party', 'paid_amount', 'posting_date',
												'due_date'], as_dict=1)

	return data_cash_flow


def add_total_row(out, period_list, company_currency):
	total_row = {
		"party_cash_flow": "'" + _("<b>Total</b>") + "'",
		"currency": company_currency
	}

	for row in out:
		for period in period_list:
			total_row.setdefault(period.key, 0.0)
			total_row[period.key] += row.get(period.key, 0.0)
			row[period.key] = row.get(period.key, 0.0)

		total_row.setdefault("total", 0.0)
		total_row["total"] += flt(row["total"])
		row["total"] = ""

	if "total" in total_row:
		out.append(total_row)

		# blank row after Total
		out.append({})
