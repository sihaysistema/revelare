# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import calendar
import json
from datetime import date, datetime, time, timedelta

import frappe
from frappe import _, _dict, scrub
from revelare.revelare.report.sales_item_availability.sales_item_availability import get_data
from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import total_sales_items

# get_data(filters, is_report=False)
def execute(filters=None):
    columns, data = get_columns(filters), get_data_(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("Material"),
            "fieldname": "material",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("Quantity"),
            "fieldname": "quantity",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            "hidden": 1,
            "width": 90
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 320
        },
        {
            "label": _("Sales Item"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 120,
            "hidden": 1,
        },
        {
            "label": _("Possible Quantity"),
            "fieldname": "possible_quantity",
            "fieldtype": "Data",
            "width": 140
        }
    ]
    return columns

def get_data_(filters):
    """Genera JSON en la caperta /sites/ llamado data.json

    Args:
        filters ([type]): [description]

    Returns:
        [type]: [description]
    """
    """{
            "company": "Patito S.A.",
            "from_date": "2021-09-20",
            "to_date": "2021-09-26",
            "sales_from": "Sales Order"
            }
    """
    flt = frappe._dict({
            "from_date": "2021-09-20",
            "to_date": "2021-09-26",
            "sales_from": "Sales Order"
            })
    data_of_date = get_range_of_date(filters)
    estimations = estimations_reports(flt, data_of_date)
    return [{}]

def get_range_of_date(filters):
    current_year = datetime.today().year
    flt_year = int(filters.year)
    data = []
    while flt_year <= current_year:
        data.append(list_of_ranges_date(flt_year))
        flt_year += 1

    return data

def list_of_ranges_date(flt_year):
    year = flt_year
    first_week = date(year,1,1)
    while True:

        data_of_year = datetime.isocalendar(first_week)
        validate = f'{data_of_year[0]} week{data_of_year[1]}'
        if f'{year} week' in validate:
            break
        else:
            first_week =  first_week + timedelta(days=1)
    first_week
    from_date = first_week.strftime('%Y-%m-%d')

    year_ = year

    dic_date = []
    while year_ == year:
        to_date = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=6)
        to_date = to_date.strftime('%Y-%m-%d')

        wk = datetime.strptime(from_date, '%Y-%m-%d').strftime('%V')
        eval_date = datetime.strptime(from_date, '%Y-%m-%d')
        date_now = datetime.today()

        if eval_date < date_now:
            dic_date.append({'from_date':from_date, 'to_date':to_date, 'wk':wk, 'year':year, 'dic_name':f'{year} Week{wk}'})
        else:
            break

        from_date = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=7)

        year_ = from_date.year

        from_date = from_date.strftime('%Y-%m-%d')

    return dic_date

def estimations_reports(flt, data_of_date):

    reports = []
    for year in data_of_date:
        for week in year:
            flt.from_date = week['from_date']
            flt.to_date = week['to_date']
            rep = get_data(flt, False)
            if rep != [{}]:
                reports.append(rep)
            else:
                pass
                # reports.append(sold(flt))
    dicToJSON('reports',reports)
    return reports

def sold(flt):
    #TODO: Ver la manera de emular la función de la columna sold

    # ES: Este es un query de ordenes de venta donde retornamos todos los nombres de las ordenes de venta que cumplen con los filtros de las fechas en el reporte.
    #     Segun su FECHA DE ENTREGA!! no estamos usando la fecha de posteo.
    matching_sales_order_items = total_sales_items(flt)

    # Obtenemos las cantidades de los items en las ordenes de venta
    sales_item_codes = [item['item_code'] for item in matching_sales_order_items]

    return []
def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
