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
	data = get_data(filters)
	# data = [{}]
	# frappe.msgprint(_((filters.from_date)))
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

def get_data(filters):
	formato_fecha = "%Y-%m-%d"
	data = []
	# items = get_items(filters)
	# sle = get_stock_ledger_entries(filters, items)
	# item_details = get_item_details(items, sle, filters)
	item_details = get_items(filters)
	# periodic_data = get_periodic_data(sle, filters)
	ranges = get_period_date_ranges(filters)

	for item_data in item_details:
		# row = {
		# 	"party_cash_flow": _(item_data.party),
		# 	# "indent": flt(1),
		# 	# # "year_start_date": year_start_date,
		# 	# # "year_end_date": year_end_date,
		# 	# "currency": 'GTQ',
		# 	# "is_group": 0,
		# 	# "opening_balance": d.get("opening_balance", 0.0) * (1 if balance_must_be=="Debit" else -1),
		# 	"total": item_data.paid_amount,
		# }

		row = frappe._dict({
			"name": _(item_data.party)
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

		# for dummy, end_date in ranges:
		# 	period = get_period(end_date, filters)
		# 	amount = flt(periodic_data.get(item_data.name, {}).get(period))
		# 	row[scrub(period)] = amount
		# 	total += amount
		# row["total"] = total
		# data.append(row)

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


def get_items(filters):
	data_cash_flow = frappe.db.get_values('Budgeted Cash Flow',
										filters={'company': filters.get("company"), 'status_payment': 'Unpaid'},
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
		period = str(fecha.year)

	return period