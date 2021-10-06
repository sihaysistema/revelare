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

    flt = frappe._dict({
            "from_date": "2021-09-20",
            "to_date": "2021-09-26",
            "sales_from": "Sales Order"
            })
    # Obtener fechas y rango por numero de semana
    data_of_date = get_range_of_date(filters)
    estimations = estimations_reports(flt, data_of_date)
    return [{}]

def get_range_of_date(filters):
    # Año actual
    current_year = datetime.today().year
    # Año desde el que se va a calcular
    flt_year = int(filters.year)

    data = []
    # Mientras el año del filtro sea menor obtenemos el listado de fechas
    while flt_year <= current_year:
        data.append(list_of_ranges_date(flt_year))
        # le sumamos un año al año desde el que se calculara
        flt_year += 1

    return data

def list_of_ranges_date(flt_year):
    # año sobre el cual se calcularan las fechas
    year = flt_year
    # Buscamos primer semana del año respecto al ISO-8601
    # Nota: El ISO-8601 es un forma que toma en cuenta el primer lunes de cada año, como primer día de la semana en cada año.
    # en el caso del año 2021 el lunes 04 de enero, es el primer día de la semana 1. el dia 03-01-2021, aun es semana 52 del año 2020
    first_week = date(year,1,1)

    while True:
        # Obtenemos una tupla
        # retorna tupla('año','#semana','#dia')
        data_of_year = datetime.isocalendar(first_week)
        # Ej: Validate = '2021 week2'
        validate = f'{data_of_year[0]} week{data_of_year[1]}'
        # si el año a validar esta en el string de validacion
        # '2020 week' in '2021 week2'
        if f'{year} week' in validate:
            # Si ya es el mismo año, rompemos el ciclo
            break
        else:
            # De lo contrario le sumamos un día a la fecha de la primer semana
            first_week = first_week + timedelta(days=1)

    # Fecha de inicio, es el primer día de la primer semana de cada año
    from_date = first_week.strftime('%Y-%m-%d')

    # Año a comparar
    year_ = year

    # Diccionario a retornar
    dic_date = []
    # Mientras year_ sea igual que year
    while year_ == year:
        # La fecha fin, sera el primer día (from_date) + 6 días
        to_date = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=6)
        # De tipo Date la pasamos a tipo String
        to_date = to_date.strftime('%Y-%m-%d')

        # Obtenemos el numero de semana de la fecha de inicio bajo el ISO-8601
        wk = datetime.strptime(from_date, '%Y-%m-%d').strftime('%V')
        # Fecha a evualar sera la fecha de inicio para que no se pase de la fecha actual
        eval_date = datetime.strptime(from_date, '%Y-%m-%d')
        # Fecha actual.
        date_now = datetime.today()

        if eval_date < date_now:
            # Si la fecha a evaluar es menor, generamos el diccionario con el rango de fechs y el nombre del diccionario por # de semana
            dic_date.append({'from_date':from_date, 'to_date':to_date, 'wk':wk, 'year':year, 'dic_name':f'{year} Week{wk}'})
        else:
            # De lo contrario nos salimos del ciclo
            break

        # Agregamos 7 dias a la fecha de inicio
        from_date = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=7)

        # Revisamos si la fecha de la fecha de inicio aun esta en el año a obtener el rango de fechas
        year_ = from_date.year

        # Convetirmos la fecha de tipo Date a String
        from_date = from_date.strftime('%Y-%m-%d')

    # Retornamos el rango de fechas
    return dic_date

def estimations_reports(flt, data_of_date):

    reports = []
    for year in data_of_date:
        # Por cada año
        for week in year:
            # Por cada semana modificamos el filtro generado artificialmente
            flt.from_date = week['from_date']
            flt.to_date = week['to_date']
            # Llamamos la funcion get_data del reporte sales_item_availability
            rep = get_data(flt, False)
            # Si hay data, entonce la agregamos la lista de diccionarios
            if rep != [{}]:
                reports.append(rep)
            else:
                pass
                # reports.append(sold(flt))
    sold(flt)
    # dicToJSON('reports',reports)
    return reports

def sold(flt):
    #TODO: Ver la manera de emular la función de la columna sold

    # ES: Este es un query de ordenes de venta donde retornamos todos los nombres de las ordenes de venta que cumplen con los filtros de las fechas en el reporte.
    #     Segun su FECHA DE ENTREGA!! no estamos usando la fecha de posteo.
    matching_sales_order_items = total_sales_items(flt)

    # Obtenemos las cantidades de los items en las ordenes de venta
    sales_item_codes = [item['item_code'] for item in matching_sales_order_items]

    data = item_availability_estimate_attributes(flt)
    dicToJSON('data_',data)
    return []

def item_availability_estimate_attributes(filters):
    # -----Buscamos todos los items que tengan BOM y sean de venta
    filt = [['default_bom','!=',''],['is_sales_item','=','1'] ]
    fieldnames = ['name', 'stock_uom', 'default_bom']
    item_estimate = frappe.db.get_list('Item', filters=filt, fields=fieldnames) or []

    items_estimate = []
    for item in item_estimate:
        # -----Obtenemos el Bom de cada item con Bom
        filt1 = [['parent','=',item['default_bom']]]
        fieldnames1 = ['name']
        item_ = frappe.db.get_list('BOM Item', filters=filt1, fields=fieldnames1) or []

        for i in item_:
            filt2 = [['name','=',i['name']],['include_in_estimations','=','1']]
            fieldnames2 = ['name','include_in_estimations']
            estimate = frappe.db.get_list('Item', filters=filt2, fields=fieldnames2) or []
            if estimate != []:
                items_estimate.append(estimate)

    return items_estimate

def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
