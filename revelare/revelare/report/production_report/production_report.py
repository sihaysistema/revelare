# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
	columns = get_columns(filters)
	
	data = []

	chart = get_chart_data(columns)

	return columns, data, None, chart


def get_columns(filters):
	'''Genera las columnas necesarias para el reporte'''

	columns = [
		{
		"fieldname": "item_code",
		"label": _("Item Code"),
		"fieldtype": "Link",
		"options": "Item",
		"width": 200
		},
		{
		"fieldname": "item_name",
		"label": _("Item Name"),
		"fieldtype": "Data",
		"width": 200
		},
		{
		"fieldname": "qty",
		"label": _("Quantity"),
		"fieldtype": "Data",
		"width": 200
		},
		{
		"fieldname": "actual_qty",
		"label": _("Actual Quantity"),
		"fieldtype": "Data",
		"width": 200
		}
	]

	return columns


def get_chart_data(columns):
	'''retorna la data necesaria para mostrar las graficas en el reporte'''

	labels = [d.get("label") for d in columns]
	# labels = ["Item Code"]
	chart = {
		"data": {
			'labels': labels,
			'datasets':[]
		}
	}
	chart["type"] = "line"

	return chart


def obtener_items(filters):
	'''items
	'''

	items_data = frappe.db.get_values('Material Request Plan Item',
										filters={'company': filters.get("company"), 'status_payment': 'Paid'},
										fieldname=['name', 'party', 'paid_amount', 'posting_date',
												'due_date'], as_dict=1)

	return items_data