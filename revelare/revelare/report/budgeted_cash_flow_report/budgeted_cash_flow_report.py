# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json

from frappe.utils import flt, cint, getdate
from frappe import _, scrub
import datetime
from datetime import datetime

from erpnext.stock.report.stock_balance.stock_balance import (get_stock_ledger_entries, get_item_details)
from erpnext.accounts.utils import get_fiscal_year
from six import iteritems

def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = get_columns(filters)

	data = [{
		"total": 0,
		"name": "<b>Saldo Inicial</b>"
	},
	{
		"name": "<b>INGRESOS</b>"
	}]

	# Data Ingresos
	prepare_data = prepare_data_unpaid(filters)
	data.extend(prepare_data)
	# Agregar total de Ingresos
	total_unpaid = add_total_row(prepare_data, filters, True)
	data.extend(total_unpaid)

	# Data Egresos
	data.append({
		"name": "<b>EGRESOS</b>"
	})

	prepare_data_p = prepare_data_paid(filters)
	data.extend(prepare_data_p)
	total_paid = add_total_row(prepare_data_p, filters, False)
	data.extend(total_paid)

	with open('dataTest.json', 'w') as f:
		f.write(str(json.dumps(total_paid, indent=2)))

	total_cash_flow = add_total_row_report(total_unpaid, total_paid, filters)
	data.extend(total_cash_flow)

	chart = get_chart_data(columns)

	return columns, data, None, chart


def get_columns(filters):
	columns = [{
		"fieldname": "name",
		"label": _("Party Cash Flow"),
		"fieldtype": "Link",
		"options": "Budgeted Cash Flow",
		"width": 200
	}]

	ranges = get_period_date_ranges(filters)

	for dummy, end_date in ranges:
		period = get_period(end_date, filters)

		columns.append({
			"label": _(period),
			"fieldname":scrub(period),
			"fieldtype": "Float",
			"width": 120
		})

	return columns


def get_period_date_ranges(filters):
		from dateutil.relativedelta import relativedelta
		from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)

		increment = {
			"Monthly": 1,
			"Quarterly": 3,
			"Half-Yearly": 6,
			"Yearly": 12
		}.get(filters.range,1)

		periodic_daterange = []
		for dummy in range(1, 53, increment):
			if filters.range == "Weekly":
				period_end_date = from_date + relativedelta(days=6)
			else:
				period_end_date = from_date + relativedelta(months=increment, days=-1)

			if period_end_date > to_date:
				period_end_date = to_date
			periodic_daterange.append([from_date, period_end_date])

			from_date = period_end_date + relativedelta(days=1)
			if period_end_date == to_date:
				break

		return periodic_daterange


def get_period(posting_date, filters):
	months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

	if filters.range == 'Weekly':
		period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
	elif filters.range == 'Monthly':
		period = str(months[posting_date.month - 1]) + " " + str(posting_date.year)
	elif filters.range == 'Quarterly':
		period = "Quarter " + str(((posting_date.month-1)//3)+1) +" " + str(posting_date.year)
	else:
		year = get_fiscal_year(posting_date, company=filters.company)
		period = str(year[2])

	return period


def prepare_data_unpaid(filters):
	data = []
	# items = get_reg_unpaid(filters)
	# sle = get_stock_ledger_entries(filters, items)
	# item_details = get_item_details(items, sle, filters)
	item_details = get_reg_unpaid(filters)
	# periodic_data = get_periodic_data(sle, filters)
	ranges = get_period_date_ranges(filters)

	for item_data in item_details:

		row = frappe._dict({
			"name": _(item_data.party),
			"indent": flt(1)
		})

		total = 0
		for dummy, end_date in ranges:
			period = get_period(end_date, filters)
			fecha_registro = conversion_fechas(item_data.posting_date, filters)

			# frappe.msgprint(_(period))
			if fecha_registro == period:
				amount = flt(item_data.paid_amount)
				row[scrub(period)] = amount
				total += amount
			else:
				amount = 0.00
				row[scrub(period)] = amount
				total += amount

		row["total"] = total
		data.append(row)

	return data


def prepare_data_paid(filters):
	data = []
	# items = get_reg_unpaid(filters)
	# sle = get_stock_ledger_entries(filters, items)
	# item_details = get_item_details(items, sle, filters)
	item_details = get_reg_paid(filters)
	# periodic_data = get_periodic_data(sle, filters)
	ranges = get_period_date_ranges(filters)

	for item_data in item_details:

		row = frappe._dict({
			"name": _(item_data.party),
			"indent": flt(1)
		})

		total = 0
		for dummy, end_date in ranges:
			period = get_period(end_date, filters)
			fecha_registro = conversion_fechas(item_data.posting_date, filters)

			# frappe.msgprint(_(period))
			if fecha_registro == period:
				amount = flt(item_data.paid_amount)
				row[scrub(period)] = amount
				total += amount
			else:
				amount = 0.00
				row[scrub(period)] = amount
				total += amount

		row["total"] = total
		data.append(row)

	return data


def get_chart_data(columns):
	labels = [d.get("label") for d in columns[1:]]
	chart = {
		"data": {
			'labels': labels,
			'datasets':[]
		}
	}
	chart["type"] = "line"

	return chart


def get_reg_unpaid(filters):
	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': filters.get("company"), 'status_payment': 'Unpaid'},
										fieldname=['name', 'party', 'paid_amount', 'posting_date',
												'due_date'], as_dict=1)

	return data_cash_flow


def get_reg_paid(filters):
	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': filters.get("company"), 'status_payment': 'Paid'},
										fieldname=['name', 'party', 'paid_amount', 'posting_date',
												'due_date'], as_dict=1)

	return data_cash_flow


def conversion_fechas(fecha, filters):
	if filters.range == 'Weekly':
		period = 'Week ' + str(fecha.isocalendar()[1]) + ' ' + str(fecha.year)
	elif filters.range == 'Monthly':
		period = fecha.strftime("%b %Y")
	elif filters.range == 'Quarterly':
		period = 'Quarter ' + str(((fecha.month - 1) //3) + 1) + ' ' + str(fecha.year)
	else:
		# period = str(fecha.year)
		year = get_fiscal_year(fecha, company=filters.company)
		period = str(year[2])

	return period


def add_total_row(out, filters, tipo=False):
	data = []

	if tipo:
		row_data = frappe._dict({
			"name": _("<b>Total Ingresos</b>")
		})

	else:
		row_data = frappe._dict({
			"name": _("<b>Total Egresos</b>")
		})

	ranges = get_period_date_ranges(filters)

	total = 0
	for row in out:
		for x in row:
			
			for dummy, end_date in ranges:
				period = get_period(end_date, filters)
				# frappe.msgprint(_(str(period.key)))
				if str(x.replace('_', ' ').capitalize()) == str(period):
					amount = (row[x])

					if str(x) != 'name':
						total += flt(amount)
						row_data.setdefault(scrub(period), 0.0)
						row_data[scrub((period))] += flt(amount)

				if filters.range == 'Yearly':
					if str(x) != 'name' and str(x) != 'indent' and str(x) != 'total':
						total += flt(row[scrub(period)])
						row_data.setdefault(scrub(period), 0.0)
						row_data[scrub((period))] += flt(row[scrub(period)])

	row_data["total"] = total
	data.append(row_data)
	data.append({})

	return data


def add_total_row_report(total_in, total_e, filters):
	data = []

	row_data = frappe._dict({
		"name": _("<b>Total Flujo de caja</b>")
	})

	for x in total_in:
		if x:
			total_ingresos = x
	
	for y in total_e:
		if y:
			total_egresos = y

	for item_ingreso in total_ingresos:
		for item_egreso in total_egresos:

			if item_egreso == item_ingreso:
				if item_egreso != 'name':
					row_data[str(item_egreso)] = float(total_ingresos[item_ingreso]
													 - total_egresos[item_egreso])

	data.append(row_data)
	data.append({})

	return data
