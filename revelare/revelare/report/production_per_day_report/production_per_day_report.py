# Copyright (c) 2019, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)

    data = obtener_items(filters)

    # chart = get_chart_data(columns)

    # return columns, data, None, chart
    return columns, data


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
            "fieldname": "stock_uom",
            "label": _("UOM"),
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
    '''Obtiene items de la base de datos en base a los filtros
    '''
    data = []

    # Obtiene la data necesaria
    master_items = []

    production_plans = frappe.db.get_values('Production Plan',
                                            filters={'company': filters.get("company"),
                                                    'posting_date': filters.get("from_date")},
                                            fieldname=['name'], as_dict=1)

    for item in production_plans:
        required_items = frappe.db.sql('''SELECT item_code, item_name, quantity, actual_qty
                                          FROM `tabMaterial Request Plan Item`
                                          WHERE parent=%(plan_name)s''', 
                                      {'plan_name': str(item.get('name'))}, as_dict=True)

        master_items.extend(required_items)

    # Prepara la data para ser mostrada correctamente en el informe
    for item_data in master_items:
        row = frappe._dict({
            "item_code": item_data.item_code,
            "item_name": item_data.item_name,
            "stock_uom": "Lbs",
            "qty": item_data.quantity,
            "actual_qty": item_data.actual_qty
            # "indent": flt(1)
        })

        data.append(row)

    return data
