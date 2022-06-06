# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
import statistics as stdic
from datetime import datetime

import frappe
import pandas as pd
from frappe import _

from revelare.revelare.report.historical_weekly_item_amounts.queries import (boms_item, find_conversion_factor, from_data,
                                                                             get_availability_estimates,
                                                                             get_sales_order_individual)
from revelare.revelare.report.historical_weekly_item_amounts.utils import (get_range_of_date, search_list_of_dict_k)


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    """
    Assigns the properties for each column to be displayed in the report
    Args:
        filters (dict): Front end filters
    Returns:
        list: List of dictionaries
    """

    columns = [
        {
            "label": _("A"),
            "fieldname": "A",
            "fieldtype": "Data",
            "width": 145
        },
        {
            "label": _("B"),
            "fieldname": "B",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": _("C"),
            "fieldname": "C",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("D"),
            "fieldname": "D",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": _("Repeat"),
            "fieldname": "repeat",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": _("E"),
            "fieldname": "E",
            "fieldtype": "Data",
            "width": 80
        },
        {
            "label": _("F"),
            "fieldname": "F",
            "fieldtype": "Data",
            "width": 150
        },
    ]

    return columns


@frappe.whitelist()
def get_data(filters):

    try:
        filters = frappe._dict(json.loads(filters))
    except Exception:
        filters = filters

    data = []
    if filters.item_selected is not None:

        result = boms_item(filters)
        if result != []:

            d = []
            for r in result:
                dat_from = from_data(r['item'])

                if dat_from != []:
                    d.append(dat_from)
            men_year = 9999999
            index = 0
            for sales_order_ in d:
                anio = [int(e['anio']) for e in sales_order_]
                if men_year > min(anio):
                    men_year = min(anio)

            data_for_item_sales = []
            for item in result:
                sales_individuals = get_sales_order_individual(item['item'])
                if sales_individuals != []:
                    data_for_item_sales += sales_individuals

            if data_for_item_sales == []:
                data = [{
                    "item_code": filters.item_selected,
                    "item_name": filters.item_selected,
                    "UOM": "Pound",
                    "labels": ["No existen ventas para ese item base"],
                    "values": ["No existen ventas para ese item base"],
                    "values1": ["No existen ventas para ese item base"],
                    "values2": ["No existen ventas para ese item base"],
                    "values3": ["No existen ventas para ese item base"]
                }]
                return data

            # pasamos a Data Frame para prepar los datos a unir
            data_for_item_sales = sorted(data_for_item_sales, key=lambda i: i['fecha'], reverse=False)
            availability_estimate = get_availability_estimates()

            if availability_estimate != []:
                # with open("log.txt",'a',encoding = 'utf-8') as f:
                #     f.write(f"item:{filters.item_selected} -\n\tavailability_estimate:{availability_estimate} \n-> result:{result}\n\n")
                #     f.close()
                # Seeccionamos los datos del item seleccionado
                df_availability_estimate = pd.DataFrame(json.loads(json.dumps(availability_estimate, indent=4, sort_keys=True, default=str)))
                df_availability_estimate = df_availability_estimate.fillna('')
                df_availability = df_availability_estimate.query(str(f'item_code == "{filters.item_selected}"'))

                if df_availability.shape[0] == 0:
                    data = [{
                        "item_code": filters.item_selected,
                        "item_name": filters.item_selected,
                        "UOM": "Pound",
                        "labels": ["No existen estimaciones para este item"],
                        "values": ["No existen estimaciones para este item"],
                        "values1": ["No existen estimaciones para este item"],
                        "values2": ["No existen estimaciones para este item"],
                        "values3": ["No existen estimaciones para este item"]
                    }]
                    return data

                df_result = pd.DataFrame(json.loads(json.dumps(result))).fillna('')

                df_union = pd.merge(df_availability, df_result, left_on='item_code', right_on='item_code')
                union = df_union.to_dict(orient='records')
            else:
                data = [{
                    "item_code": filters.item_selected,
                    "item_name": filters.item_selected,
                    "UOM": "Pound",
                    "labels": ["No existen estimaciones para este item"],
                    "values": ["No existen estimaciones para este item"],
                    "values1": ["No existen estimaciones para este item"],
                    "values2": ["No existen estimaciones para este item"],
                    "values3": ["No existen estimaciones para este item"]
                }]
                return data

            for row in data_for_item_sales:
                # row['type_date'] = datetime.strptime(row['fecha'], '%Y-%m-%d')
                row['type_date'] = row['fecha']

            for row in union:
                # row['type_date_start'] = row['start_date']
                # row['type_date_end'] = row['end_date']
                row['type_date_start'] = datetime.strptime(row['start_date'], '%Y-%m-%d').date()
                row['type_date_end'] = datetime.strptime(row['end_date'], '%Y-%m-%d').date()

            new_data = []
            for row in union:
                for item in data_for_item_sales:
                    if row["item"] == item["item"]:
                        if item['type_date'] >= row['type_date_start'] and item['type_date'] <= row['type_date_end']:
                            new_data.append({
                                    'item': row['item'],
                                    'start_date': row['start_date'],
                                    'end_date': row['end_date'],
                                    'fecha': item['fecha'],
                                    'item_code_base': row['item_code'],
                                    'item_name_base': row['item_name'],
                                    'item_sale_code': item['item'],
                                    'item_sale_name': item['item_name'],
                                    'amount_estiamted': row['amount'],
                                    'uom_estimated': row['amount_uom'],
                                    'total_qty_sales_order': item['Cant SO'],
                                    'total_sales_order': item['total'],
                                    'uom_sales': item['uom']
                            })
                            data_for_item_sales.pop(data_for_item_sales.index(item))
                        else:
                            item['item'] = row['item']
                            item['item_code_base'] = row['item_code']
                            item['item_name_base'] = row['item_name']
                            item['uom_estimated'] = row['amount_uom']

            for row in new_data:
                row['factor_conversion'] = find_conversion_factor(row['uom_sales'], row['uom_estimated'])[0]
                row['sold'] = row['factor_conversion']['value'] * row['total_sales_order']

            for row in data_for_item_sales:
                row['factor_conversion'] = find_conversion_factor(row['uom'], row['uom_estimated'])[0]
                row['sold'] = row['factor_conversion']['value'] * row['total']

            range_of_date = get_range_of_date(frappe._dict({'year': men_year}))
            other_data = []
            while len(data_for_item_sales) > 0:

                for year in range_of_date:
                    for week in year:
                        if data_for_item_sales == []:
                            break
                        row = data_for_item_sales[0]
                        if row['fecha'] <= datetime.strptime(week['to_date'], '%Y-%m-%d').date() and row['fecha'] >= datetime.strptime(
                                week['from_date'], '%Y-%m-%d').date():

                            index = search_list_of_dict_k(f'{week["year"]} Week{week["wk"]}', other_data)
                            element = dict(row, **week)

                            if index is not None:
                                other_data[index][f'{week["year"]} Week{week["wk"]}'].append(element)
                            else:
                                other_data.append({f'{week["year"]} Week{week["wk"]}': [element]})

                            data_for_item_sales.pop(data_for_item_sales.index(row))

            while len(new_data) > 0:
                for year in range_of_date:
                    for week in year:
                        if new_data == []:
                            break
                        row = new_data[0]
                        if row['fecha'] <= datetime.strptime(week['to_date'], '%Y-%m-%d').date() and row['fecha'] >= datetime.strptime(
                                week['from_date'], '%Y-%m-%d').date():

                            index = search_list_of_dict_k(f'{week["year"]} Week{week["wk"]}', other_data)
                            element = dict(row, **week)

                            if index is not None:
                                other_data[index][f'{week["year"]} Week{week["wk"]}'].append(element)
                            else:
                                other_data.append({f'{week["year"]} Week{week["wk"]}': [element]})

                            new_data.pop(new_data.index(row))

            mdata = list(other_data[0].values())[0][0]
            data.append({
                'item_code': mdata['item_code_base'],
                'item_name': mdata['item_name_base'],
                'UOM': mdata['uom_estimated'],
                'time_series_data': []
            })

            for element in other_data:
                rdata = list(element.values())[0][0]
                data[0]['time_series_data'].append({rdata['dic_name']: {
                    'estimated': rdata.get('estiamted', 0),
                    'reserved': rdata.get('reserved', 0),
                    'sold': rdata.get('sold', 0),
                    'available': rdata.get('available', 0)
                    }
                })

            week_list = []
            for row in data[0]['time_series_data']:
                week_ = list(row.keys())[0]
                week_list.append(week_)

            for year in range_of_date:
                for week in year:
                    if not week['dic_name'] in week_list:
                        data[0]['time_series_data'].append({week['dic_name']: {'estimated': 0, 'reserved': 0, 'sold': 0, 'available': 0}})

            data = add_stadistics(data, filters)
            data = add_values_of_char(data, filters)

        else:
            # item_link_open = "<a href='/app/item/"
            # item_link_open_end = "' target='_blank'>"
            # item_link_close = "</a>"
            data = [{
                "item_code": filters.item_selected,
                "item_name": filters.item_selected,
                "UOM": "Pound",
                "labels": ["No existe BOM configurado"],
                "values": ["No existe BOM configurado"],
                "values1": ["No existe BOM configurado"],
                "values2": ["No existe BOM configurado"],
                "values3": ["No existe BOM configurado"]
            }]
            return data
    return data


def add_stadistics(data, filters):
    """Agregamos las estadisticas por semana por cada item base

    Args:
        data ([type]): [description]

    Returns:
        [type]: [description]
    """
    fiscal_year = frappe.utils.nowdate()[:4]

    # Por cada item en la data
    for dat in data:
        # Creamos la lista de registros por semana
        records_of_weeks = []
        order_of_week = []
        # Por cada semana en el rango
        for week_ in range(1, 54):
            # Obtenemos el numero de semana a dos digitos
            no_week = str(week_).zfill(2)

            # Por cada semana en la serie de datos
            for d in dat['time_series_data']:
                wsearch = f'Week{no_week}'

                if fiscal_year in list(d.keys())[0]:
                    # Si la semana a buscar por cada año esta en la llave "2018 Week01", "2019 Week01", "2020 Week01"
                    if wsearch in list(d.keys())[0]:
                        index_1 = search_list_of_dict_k(wsearch, order_of_week)

                        if index_1 is not None:
                            # Solo le agregamos los valores de esa semana, del año seleccionado
                            order_of_week[index_1][wsearch].append(list(d.values())[0])
                        else:

                            order_of_week.append({wsearch: [list(d.values())[0]]})

                elif fiscal_year not in list(d.keys())[0]:
                    if wsearch in list(d.keys())[0]:

                        # Buscamos el indice de la semana en la lista de registros
                        index_2 = search_list_of_dict_k(wsearch, records_of_weeks)
                        # Si ya esta la semana en los registros
                        if index_2 is not None:
                            # Solo le agregamos los valores de esa semana, sin importar el año
                            records_of_weeks[index_2][wsearch].append(list(d.values())[0])
                        else:
                            # Sino agregamos un diccionario con el nombre de la semana sin el año
                            # Y agregamos los valores de esa semana, sin importar el año
                            records_of_weeks.append({wsearch: [list(d.values())[0]]})

        dat['year_curren'] = order_of_week

        # Creamos la llave estadistica para agregale los valores estadisticos
        dat['statistics'] = []

        # Por cada registro en la lista de registros de semanas
        for rec_wek in records_of_weeks:
            # Obtenemos el nombre de la lista y los valores de la lista, que estan dentro del diccionario
            list_name = list(rec_wek.keys())[0]
            list_values = list(rec_wek.values())[0]

            # Preparamos la variables sobre los cuales obtendremos los calculos
            estimated_values = []
            reserved_values = []
            available_values = []
            sold_values = []

            # Por cada año en las lista de valores
            for item in list_values:
                # Agregamos dicho valor en formato float a cada lista respectivamente
                estimated_values.append(float(item['estimated']))
                reserved_values.append(float(item['reserved']))
                available_values.append(float(item['available']))
                sold_values.append(float(item['sold']))

            # Agregamos el nombre de la lista en el apartado de estadisticas
            dat['statistics'].append({
                # Le damos el nombre de la semana "Week01"
                list_name: {
                    # Agregamos cada columna de estimacioens
                    # Obtenemos por medio de la funcion max() el valor maximo en la lista
                    # Obtenemos por medio de la funcion min() el valor minimo en la lista
                    # Obtenemos el promedio por medio de la funcion stadistics.mean()
                    #   que obtiene la media aritmetica de la libreria estadisticas
                    'estimated': {
                        'max': max(estimated_values),
                        'avg': stdic.mean(estimated_values),
                        'min': min(estimated_values)
                    },
                    'reserved': {
                        'max': max(reserved_values),
                        'avg': stdic.mean(reserved_values),
                        'min': min(reserved_values)
                    },
                    'available': {
                        'max': max(available_values),
                        'avg': stdic.mean(available_values),
                        'min': min(available_values)
                    },
                    'sold': {
                        'max': max(sold_values),
                        'avg': stdic.mean(sold_values),
                        'min': min(sold_values)
                    },
                }
            })

    return data


def add_values_of_char(data, filters):
    # year = '2021'
    # type_of_char = 'estimated'
    type_of_char = 'sold'

    for dat in data:
        dat['labels'] = []
        dat['values'] = []

        dat['value1'] = []
        dat['value2'] = []
        dat['value3'] = []

        for item in dat['year_curren']:

            dat['labels'].append(list(item.keys())[0])
            # dat['values'].append(list(item.values())[0][type_of_char])
            sum_curren = 0
            for val in list(item.values())[0]:
                sum_curren += float(val[type_of_char])

            dat['values'].append(sum_curren)

        dat['labels'].sort()

        for item in dat['statistics']:
            stadistic = list(item.values())[0]
            data_selec = stadistic[type_of_char]

            if dat['statistics'].index(item)+1 < len(dat['year_curren']):
                dat['value1'].append(data_selec['max'])
                dat['value2'].append(data_selec['avg'])
                dat['value3'].append(data_selec['min'])

    return data

def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=4, default=str))
