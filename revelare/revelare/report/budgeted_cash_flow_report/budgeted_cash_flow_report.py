# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, cint
from erpnext.accounts.report.financial_statements import get_period_list
import json


def execute(filters=None):

	# if str(filters.periodicity) == "Weekly":
	# 	frappe.msgprint(_(str(filters.periodicity)))
	# 	period_list = get_period_list_weekly(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, company=filters.company)		
	# else:
	# 	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, company=filters.company)

	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year, filters.periodicity, company=filters.company)
	
	# currency = filters.presentation_currency or frappe.get_cached_value('Company',  filters.company,  "default_currency")

	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, company=filters.company)

	# Datos iniciales para mostrar Saldo Inicial e Ingresos
	data = [{
		"total": 0,
		"currency": "GTQ",
		"party_cash_flow": "<b>Saldo Inicial</b>"
		# "dec_2019": 39.0,
	},
	{
		"currency": "GTQ",
		"party_cash_flow": "<b>INGRESOS</b>"
	}]

	# Datos para seccion que describe los Gastos
	gastos = [{
		"currency": "GTQ",
		"party_cash_flow": "<b>EGRESOS</b>"
	}]

	# Total cash flow
	total_cash_flow = [{
		"currency": "GTQ",
		"party_cash_flow": "<b>TOTAL CASH FLOW</b>"
	}]

	total_reporte = []

	no_cobrado = get_data_cash_flow_unpaid(filters.company)
	data_preparada = prepare_data(no_cobrado, period_list, 'GTQ')

	total_no_cobrado = add_total_row(data_preparada, period_list, 'GTQ')
	total_reporte.append(total_no_cobrado)
	data.extend(data_preparada)

	data.extend(gastos)

	cobrado = get_data_cash_flow_paid(filters.company)
	data_preparada_cobrado = prepare_data(cobrado, period_list, 'GTQ')

	total_cobrado = add_total_row(data_preparada_cobrado, period_list, 'GTQ')
	total_reporte.append(total_cobrado)
	data.extend(data_preparada_cobrado)

	data.extend(total_cash_flow)

	# data_prueba = add_total_row(total_cobrado, period_list, 'GTQ')
	# frappe.msgprint(_(str(data_preparada.extend(data_preparada_cobrado))))
	chart = get_chart_data(filters, columns, no_cobrado)

	# frappe.msgprint(_(str(json.dumps(total_reporte))))

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
		"width": 200
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
			"width": 100
		})
	if periodicity!="Yearly":
		if not accumulated_values:
			columns.append({
				"fieldname": "total",
				"label": _("Total"),
				"fieldtype": "Currency",
				"width": 100
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


def get_data_cash_flow_unpaid(company):
	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': company, 'status_payment': 'Unpaid'},
										fieldname=['name', 'party', 'paid_amount', 'posting_date',
												'due_date'], as_dict=1)

	return data_cash_flow


def get_data_cash_flow_paid(company):
	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': company, 'status_payment': 'Paid'},
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

	return total_row


def add_total_report(out, period_list, company_currency):
	total_row = {
		"party_cash_flow": "'" + _("<b>Total Cash Flow</b>") + "'",
		"currency": company_currency
	}

	for row in out:
		for period in period_list:
			total_row.setdefault(period.key, 0.0)
			total_row[period.key] -= row.get(period.key, 0.0)
			row[period.key] = row.get(period.key, 0.0)

		total_row.setdefault("total", 0.0)
		total_row["total"] += flt(row["total"])
		row["total"] = ""

	if "total" in total_row:
		out.append(total_row)

		# blank row after Total
		out.append({})


def get_period_list_weekly(from_fiscal_year, to_fiscal_year, periodicity, accumulated_values=False,
	company=None, reset_period_on_fy_change=True):
	"""Get a list of dict {"from_date": from_date, "to_date": to_date, "key": key, "label": label}
		Periodicity can be (Yearly, Quarterly, Monthly)"""

	fiscal_year = get_fiscal_year_data(from_fiscal_year, to_fiscal_year)
	validate_fiscal_year(fiscal_year, from_fiscal_year, to_fiscal_year)

	# start with first day, so as to avoid year to_dates like 2-April if ever they occur]
	year_start_date = getdate(fiscal_year.year_start_date)
	year_end_date = getdate(fiscal_year.year_end_date)

	months_to_add = {
		"Yearly": 12,
		"Half-Yearly": 6,
		"Quarterly": 3,
		"Monthly": 1
	}[periodicity]

	weeks_to_add = {
		"Weekly": 52
	}[periodicity]

	# Listado vacio, en donde iran los meses con los anos, o los trimestres con sus meses, etc.
	period_list = []

	start_date = year_start_date
	# Get months hace un recalculo y se asegura de obtener, solamente un numero de meses. En este caso 12 meses.
	# este estima la cantidad de meses que hay entre la fecha de inicio y fecha final
	months = get_months(year_start_date, year_end_date)
	
	# Usa el numero de meses "12"
	for i in range(months // months_to_add):
		period = frappe._dict({
			"from_date": start_date
		})

		to_date = add_months(start_date, months_to_add)
		start_date = to_date

		if to_date == get_first_day(to_date):
			# if to_date is the first day, get the last day of previous month
			to_date = add_days(to_date, -1)

		if to_date <= year_end_date:
			# the normal case
			period.to_date = to_date
		else:
			# if a fiscal year ends before a 12 month period
			period.to_date = year_end_date

		period.to_date_fiscal_year = get_fiscal_year(period.to_date, company=company)[0]
		period.from_date_fiscal_year_start_date = get_fiscal_year(period.from_date, company=company)[1]

		period_list.append(period)

		if period.to_date == year_end_date:
			break

	# Nuestra propia funcion, para obtener el numero de semanas que tiene ese año TODO:  Evaluar si ya hay una funcion de frappe que haga esto.
	weeks = get_weeks(year_start_date, year_end_date)


	# common processing
	for opts in period_list:
		key = opts["to_date"].strftime("%b_%Y").lower()
		if periodicity == "Monthly" and not accumulated_values:
			label = formatdate(opts["to_date"], "MMM YYYY")
		else:
			if not accumulated_values:
				label = get_label(periodicity, opts["from_date"], opts["to_date"])
			else:
				if reset_period_on_fy_change:
					label = get_label(periodicity, opts.from_date_fiscal_year_start_date, opts["to_date"])
				else:
					label = get_label(periodicity, period_list[0].from_date, opts["to_date"])

		opts.update({
			"key": key.replace(" ", "_").replace("-", "_"),
			"label": label,
			"year_start_date": year_start_date,
			"year_end_date": year_end_date
		})

	return period_list
