# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt


# import frappe
from frappe import _
from revelare.revelare.report.repack_report.utils import list_of_ranges_date, list_of_ranges_month, get_isoYear_start_and_endDate
from revelare.revelare.report.repack_report.queries import get_stock_value_data
from datetime import datetime as dt


def execute(filters=None):
    columns, data = get_columns(filters), get_data(filters)
    return columns, data


def get_columns(filters):
    columns = [
        {
            "fieldname": "item_code",
            "label": _("Item Code"),
            "fieldtype": "Link",
            "options": "Item",
            "width": 150
        },
        {
            "fieldname": "item_name",
            "label": _("Item Name"),
            "fieldtype": "Data",
            "width": 180
        },
        {
            "fieldname": "uom",
            "label": _("UOM"),
            "fieldtype": "Data",
            "width": 100
        },
        # {
        #     "fieldname": "qty",
        #     "label": _("Quantity"),
        #     "fieldtype": "Data",
        #     "width": 200
        # }
    ]

    if filters.period == 'Weekly':
        ranges = list_of_ranges_date(int(filters.fiscal_year))
        for week in ranges:
            columns.append({
                "fieldname": f"{week['dic_name']}",
                "label": f"{week['dic_name']} [{week['from_date'].replace('-','/')[5:]} - {week['to_date'].replace('-','/')[5:]}]",
                "fieldtype": "Data",
                "width": 180
            })
    elif filters.period == 'Monthly':
        ranges = list_of_ranges_month(int(filters.fiscal_year))
        for month in ranges:
            columns.append({
                "fieldname": f"{month['dic_name']}",
                "label": f"{month['month']}",
                "fieldtype": "Data",
                "width": 90
            })

    columns.append({
            "fieldname": f"total",
            "label": f"Total",
            "fieldtype": "Data",
            "width": 80
            })
    return columns


def get_data(filters):
    data = []
    if filters.period == 'Weekly':
        # Obtenemos la estructura de rangos de fecha por semanas
        ranges = list_of_ranges_date(int(filters.fiscal_year))

    elif filters.period == 'Monthly':
        # Obtenemos la estructura de rangos de fecha por mes
        ranges = list_of_ranges_month(int(filters.fiscal_year))

    # Obtenemos primer y ultimo día del año ISO-8601
    from_date, to_date = get_isoYear_start_and_endDate(filters.fiscal_year)
    # Obtenemos Stock Entrys de tipo Repack, con las fechas anteriormente obtenidas.
    raw_data = get_stock_value_data(from_date, to_date, filters.item_code, filters.period)

    if raw_data == []:
        return [{}]

    list_of_items = {}
    # Dividimos la data por item code, en una lista de diccinarios con una lista
    # [{'item_code':[{'item_code':'01-Aderezo', 'item_name':'Aderezo', 'week1':0, ...}]}]
    for row in raw_data:
        list_of_items.setdefault(row.get('item_code', ''), []).append(row)

    list_of_items = [{k: v} for k, v in list_of_items.items()]

    # Convetirmos la fecha de string a tipo Date
    for week in ranges:
        week['from_date'] = dt.strptime(week['from_date'], '%Y-%m-%d')
        week['to_date'] = dt.strptime(week['to_date'], '%Y-%m-%d')

    clean_data = []
    for row in list_of_items:
        # Diccionario a agregar a la data
        dic_to_append = {}
        for r in list(row.values())[0]:
            # Verificamos si existe en cada posición del rango ya sea semana o mes
            for week in ranges:
                # Veficamos si el stock entry esta entre las fechas del rango
                if week['from_date'].date() <= r['posting_date'] <= week['to_date'].date():
                    # Si esta, agregamos la cantidad a esa llave, la cantidad
                    dic_to_append[week['dic_name']] = r['qty']
                else:
                    # Si esa posicion en el diccionario no est ocupado, agregamos un 0
                    if dic_to_append.get(week['dic_name']) is None:
                        dic_to_append[week['dic_name']] = 0

            # En la ultima posicion, de la lista de items, agregamos las llaves de la primer columna
            if list(row.values())[0].index(r) == len(list(row.values())[0])-1:
                # Agregamos el codigo de item al diccionario
                [dic_to_append['item_code']] = row.keys()
                dic_to_append['uom'] = r['uom']
                dic_to_append['item_name'] = r['item_name']

        clean_data.append(dic_to_append)

    # Sumamos los valores para agregar la ultima columna
    for row in clean_data:
        sum_of_item = 0
        for column in list(row.keys()):
            if column not in ['uom', 'item_code', 'item_name']:
                sum_of_item += float(row[column])

        row['total'] = sum_of_item
    data = clean_data

    return data
