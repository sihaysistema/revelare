# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import calendar
import json
import math
import statistics as stdic
from datetime import date, datetime, time, timedelta

import frappe
from frappe import _, _dict, scrub

from revelare.revelare.report.historical_weekly_item_amounts.utils import (get_range_of_date, is_digit, is_string,
                                                                           list_of_ranges_date, search_list_of_dict_k,
                                                                           search_list_of_dict_v, search_week_in_range)
from revelare.revelare.report.sales_item_availability.sales_item_availability import get_data
from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import (estimation_item_attributes,
                                                                                              find_bom_items, find_boms,
                                                                                              find_conversion_factor,
                                                                                              find_sales_items,
                                                                                              find_sales_order_items,
                                                                                              find_sales_orders,
                                                                                              item_availability_estimates_range,
                                                                                              periods_estimated_items,
                                                                                              total_item_availability_estimates,
                                                                                              total_sales_items,
                                                                                              total_sales_items_draft)


def execute(filters=None):
    columns, data = get_columns(filters), get_data_(filters)
    return columns, data

def get_columns(filters):
    columns = [
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            # "hidden": 0,
            "width": 90
        },
        {
            "label": _("Name Estimate"),
            "fieldname": "item_name_estimate",
            "fieldtype": "Data",
            #"options": "Item",
            "width": 320
        },
        {
            "label": _("Serie De Datos"),
            "fieldname": "time_series_data",
            "fieldtype": "Data",
            "width": 1200,
            #"hidden": 0,
        }
    ]
    return columns


@frappe.whitelist()
def get_data_(filters):
    """Genera JSON en la caperta /sites/ llamado data.json

    Args:
        filters ([type]): [description]

    Returns:
        [type]: [description]
    """
    try:
        filters = frappe._dict(json.loads(filters))
    except:
        filters = filters
    dicToJSON('filters',filters)

    flt = frappe._dict({
            "from_date": "",
            "to_date": "",
            "sales_from": "Sales Order",
            "item_selected": filters.item_selected
            })
    # Obtener fechas y rango por numero de semana
    data_of_date = get_range_of_date(filters)
    # Obtenemos las estimaciones en reporte y las ordenes de venta
    estimations = estimations_reports(flt, data_of_date, filters)
    # Formatemos los obtenidos
    list_of_items = formating_data(estimations, data_of_date)

    #Agregando estadisticas
    list_of_items = add_stadistics(list_of_items, filters)
    list_of_items = add_values_of_char(list_of_items, filters)
    dicToJSON('data',list_of_items)
    return list_of_items

def estimations_reports(flt, data_of_date, filters):
    """Funcion que obtiene los estimado desde el reporte de "Sales Item Availability

    Args:
        flt (frapp._dict): filtros por medio del cual se llamara al reporte
        data_of_date (list): rango de fechas por el cual se llamara

    Returns:
        list: Lista de diccionarios con los datos necesarios para su analisis
        Ej: [{'item_code_base':lechuga-01, 'estimated':250, 'reserved':50, 'availability':200, 'item_name_base':'lechuga lista para consechar', ...}]
    """
    # Creamos lista a devolver con los reportes y las ventas
    reports = []
    # Por cada año en el rango de fechas seleccionado
    for year in data_of_date:
        # Por cada año
        for week in year:
            # Por cada semana modificamos el filtro generado artificialmente
            flt.from_date = week['from_date']
            flt.to_date = week['to_date']
            flt.year = week['year']

            # Obtenemos la data del reporte en el rango de fechas
            rep = prepair_data_of_report(flt, filters)
            # Obtenemo las ventas en el rango de fechas
            sold_ = sold(flt, filters)
            # Si hay data, entonce la agregamos la lista de diccionarios
            if rep != []:
                reports.append(rep)
            elif sold_ != []:
                reports.append(sold_)

    return reports

def prepair_data_of_report(flt, filters):
    """Funcion que prepara la data del reporte

    Args:
        flt ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Llamamos la funcion get_data del reporte sales_item_availability
    # rep = get_data(flt, False)
    rep = get_data_for_item(flt) or [{}]


    # Creamos la lista de los items base del reporte
    items_in_report = []
    # Si hay data el reporte
    if rep != [{}]:

        # Si no esta marcado el cheque de item de venta
        if filters.is_sales_item == 0 or filters.is_sales_item == None:
            # Por cada fila del reporte
            for row in rep:

                # Buscamos si la columna B es digito, dicho digito obtiene el total de estimaciónes para el item base
                # Con el valor verdadero de la setencia, sabemos que esa es una columna con item base de estimación
                if is_digit(row.get('B','')):
                    # Si es digito, obtenemos las demas columnas de esa fila y la agregamos a los items del reporte
                    items_in_report.append(
                        {
                            'item_name_estimate':row['A'],
                            'estimated':row['B'],
                            'uom':row['C'],
                            'reserved':row['repeat'],
                            'sold':row['E'],
                            'available':row['F'],
                            'item_name_base':row['J'],
                            'item_code_base':row['H'],
                            'year':flt.year,
                            'from_date':flt.from_date
                        })

        # Si esta marcado el cheque de item de venta
        elif filters.is_sales_item == 1:

            # Por cada fila del reporte
            for row in rep:

                # Buscamos si la columna C es digito, dicho digito tiene el total posible para vender con los items base postulados
                # Buscamos si la columna "Repeat" es digito, dicho digito tiene el valor de los autorepetidos.
                # Con los dos valores positivos sabemos que esa es una columna de un item de venta
                if is_digit(row.get('C','')) and is_digit(row.get('repeat', '')):
                    # Si es digito, obtenemos las demas columnas de esa fila y la agregamos a los items del reporte

                    if filters.item_selected != None:
                    # Si seleccionamos un item de venta
                        if row['A'] == filters.item_selected:
                        # Al recorrer el reporte buscamos el item de venta para agregar lo al reporte
                            items_in_report.append(
                                {
                                    'item_name_estimate':row['A'],
                                    'estimated':row['C'],
                                    'uom':row['D'],
                                    'reserved':row['repeat'],
                                    'sold':row['E'],
                                    'available':row['F'],
                                    'item_name_base':row['B'],
                                    'item_code_base':row['A'],
                                    'year':flt.year,
                                    'from_date':flt.from_date
                                })
                    else:
                            items_in_report.append(
                                {
                                    'item_name_estimate':row['A'],
                                    'estimated':row['C'],
                                    'uom':row['D'],
                                    'reserved':row['repeat'],
                                    'sold':row['E'],
                                    'available':row['F'],
                                    'item_name_base':row['B'],
                                    'item_code_base':row['A'],
                                    'year':flt.year,
                                    'from_date':flt.from_date
                                })

    return items_in_report

def sold(flt, filters):
    """ Funcion que obtiene las ordenes de venta, formateadas para ser agregadas a la lista de items

    Args:
        flt ([type]): [description]

    Returns:
        [type]: [description]
    """

    # 1) Obtenemos los items venditos
    # 2) La lista de los items base con el nombre de los items de venta a utilizar
    sums_items_sales, items_sales = get_sums_sales_items_qty(flt)
    solds_totals = []
    # Si hubieron ventas esa semana ejecutamos lo siguiten
    if sums_items_sales != []:

        # Reorganizamos una lista de diccionario de items vendidos de la forma:
        """
        [{
            item : [ lista_items, ...]
        },
        {
            item : [ lista_items, ...]
        }]
        """
        dic_sold = []
        if filters.is_sales_item == None:
            for i_s in items_sales:
                index = search_list_of_dict_k(i_s['estimation_name'], dic_sold)
                if index != None:
                    dic_sold[index][i_s['estimation_name']].append(i_s)
                else:
                    dic_sold.append({i_s['estimation_name']:[i_s]})

            #---Realizaremos la conversion
            for dic_s in dic_sold:
                for item in list(dic_s.values()):
                    # accedemos hasta los items de venta que tienen el mismo item base en comun
                    for i in item:

                        # Revisamos si uno de los items de venta esta entre los items vendidos esa semana
                        index = search_list_of_dict_v(i['item'],'item_code',sums_items_sales)

                        # Si esta entonces le generamos la conversión
                        if index != None:
                            # Formula para obtener la conversion: ((cantidad consumida por unidad a crear) * (factor de conversion) * (cantidad vendida en esa semana))
                            # Ej:
                            # Item base: Lechuga lista para consechar en libras
                            # Item de venta: Lechuga en bolsa de 8OZ
                            # Cantidad vendida: 15 unidades
                            # Factor de conversion de onzas a libras es 0.0625
                            # venta convertida = (8 *0.0625 * 15) = 7.5
                            sum_item = sums_items_sales[index]['sum_item']
                            i['conversion_sold'] = (i['qty_consumed_per_units'] * i['conversion_factor'] * sum_item)

            # Total de ventas  por item base
            solds_totals = []
            # Por cada item base se genera un nuevo diccionario
            for dic_s in dic_sold:

                # Obtenemos los campos que necesitaremos agregar a cada suma
                item_name_estimate = list(dic_s.keys())[0]
                item_code_base = dic_s[item_name_estimate][0]['item_code_base']
                item_name_base = dic_s[item_name_estimate][0]['item_name_base']
                uom = dic_s[item_name_estimate][0]['uom']


                # Suma que generaremos para cada item
                sum_items_sold = 0
                # Por cada item base se obtienen los items de venta de dicho item base
                for item in dic_s[item_name_estimate]:
                    # Si existe venta convertida la sumamos
                    if item.get('conversion_sold','') != '':
                        sum_items_sold += item['conversion_sold']

                # Si la suma es mayor que 0 generamos el nuevo diccionario
                if  sum_items_sold > 0:
                    solds_totals.append({
                        'item_name_estimate': item_name_estimate,
                        'sold':sum_items_sold,
                        'item_code_base':item_code_base,
                        'item_name_base':item_name_base,
                        'year':flt.year, 'from_date':flt.from_date,
                        'uom':uom})

        elif filters.is_sales_item == 1:

                for i_s in items_sales:
                    index = search_list_of_dict_k(i_s['item'], dic_sold)
                    if index != None:
                        dic_sold[index][i_s['item']].append(i_s)
                    else:
                        dic_sold.append({i_s['item']:[i_s]})

                #---Realizaremos la conversion
                for dic_s in dic_sold:
                    for item in list(dic_s.values()):
                        # accedemos hasta los items de venta que tienen el mismo item base en comun
                        for i in item:

                            # Revisamos si uno de los items de venta esta entre los items vendidos esa semana
                            index = search_list_of_dict_v(i['item'],'item_code',sums_items_sales)

                            # Si esta entonces le generamos la conversión
                            if index != None:
                                # Formula para obtener la conversion: ((cantidad consumida por unidad a crear) * (factor de conversion) * (cantidad vendida en esa semana))
                                # Ej:
                                # Item base: Lechuga lista para consechar en libras
                                # Item de venta: Lechuga en bolsa de 8OZ
                                # Cantidad vendida: 15 unidades
                                # Factor de conversion de onzas a libras es 0.0625
                                # venta convertida = (8 *0.0625 * 15) = 7.5
                                sum_item = sums_items_sales[index]['sum_item']
                                i['conversion_sold'] = (i['qty_consumed_per_units'] * i['conversion_factor'] * sum_item)

                # Total de ventas  por item base
                solds_totals = []
                if filters.item_selected == None:
                    # Por cada item base se genera un nuevo diccionario
                    for dic_s in dic_sold:
                        # Obtenemos los campos que necesitaremos agregar a cada suma
                        item_name_estimate = list(dic_s.keys())[0]
                        item_code_base = dic_s[item_name_estimate][0]['item_code_base']
                        item_name_base = dic_s[item_name_estimate][0]['item_name_base']
                        uom = dic_s[item_name_estimate][0]['uom']


                        # Suma que generaremos para cada item
                        sum_items_sold = 0
                        # Por cada item base se obtienen los items de venta de dicho item base
                        for item in dic_s[item_name_estimate]:
                            # Si existe venta convertida la sumamos
                            if item.get('conversion_sold','') != '':
                                sum_items_sold += item['conversion_sold']

                        # Si la suma es mayor que 0 generamos el nuevo diccionario
                        if  sum_items_sold > 0:
                            solds_totals.append({
                                'item_name_estimate': item_name_estimate,
                                'sold':sum_items_sold,
                                'item_code_base':item_code_base,
                                'item_name_base':item_name_base,
                                'year':flt.year, 'from_date':flt.from_date,
                                'uom':uom})

                elif filters.item_selected != None:
                    # Por cada item base se genera un nuevo diccionario
                    for dic_s in dic_sold:
                        # Obtenemos los campos que necesitaremos agregar a cada suma
                        item_name_estimate = list(dic_s.keys())[0]
                        item_code_base = dic_s[item_name_estimate][0]['item']
                        item_name_base = dic_s[item_name_estimate][0]['item_name']
                        uom = dic_s[item_name_estimate][0]['uom']


                        # Suma que generaremos para cada item
                        sum_items_sold = 0
                        # Por cada item base se obtienen los items de venta de dicho item base
                        for item in dic_s[item_name_estimate]:
                            # Si existe venta convertida la sumamos
                            if item.get('conversion_sold','') != '':
                                sum_items_sold += item['conversion_sold']

                        # Si la suma es mayor que 0 generamos el nuevo diccionario
                        if  sum_items_sold > 0:
                            if filters.item_selected == item_name_estimate:

                                solds_totals.append({
                                    'item_name_estimate': item_name_estimate,
                                    'sold':sum_items_sold,
                                    'item_code_base':item_code_base,
                                    'item_name_base':item_name_base,
                                    'year':flt.year, 'from_date':flt.from_date,
                                    'uom':uom})

    return solds_totals

def get_sums_sales_items_qty(flt):
    """Funcion que obtiene la suma de cada item de venta, del campo cantidad

    Args:
        flt ([type]): [description]

    Returns:
        [type]: [description]
    """
    sums_items_qty = []

    # Obtenemos los items de compra que tengan marcado el campo de estimacion y de manufactura
    items_sales = get_items_sales(flt)
    # Obtenemos todas las ventas durante el periodo de tiempo en el rango
    sales_order = obtain_sales_orders_in_range(flt)

    # Si hay ventas de ese item
    if sales_order != []:

        # Obtenemos la lista solo con los nombre de los items de venta a sumar
        list_items = [i['item'] for i in items_sales]

        # Reordenamos los items de las ordenes de venta
        sales_order = sorted(sales_order, key = lambda i: i['item_code'],reverse=False)

        # Reorganizamos una lista de diccionario de la forma:
        """
        [{
            item : [ lista_items, ...]
        },
        {
            item : [ lista_items, ...]
        }]
        """
        dic_sales_order = []
        for s in sales_order:
            index = search_list_of_dict_k(s['item_code'], dic_sales_order)
            if index != None:
                dic_sales_order[index][s['item_code']].append(s)
            else:
                dic_sales_order.append({s['item_code']:[s]})

        # lista de diccionarios con la suma de cada item vendido en el rango de tiempo
        sums_items_qty = []
        # Por cada item de la lista de dicciciones de ordenes de venta
        for dic in dic_sales_order:
            # Obtenemos el item que validaremos
            key = list(dic.keys())[0]
            # Si esta en la lista de items a estimar
            if key in list_items:
                # Recorremos la lista que viene dentro, sumando el campo qty
                for item in list(dic.values()):
                    sum_of_item = 0
                    for i in item:
                        sum_of_item += i['qty']
                    # Agregamos a sumas de los items, el dicciciario con el nombre del item y la suma
                    sums_items_qty.append({'item_code':key,'sum_item':sum_of_item})

    return sums_items_qty,items_sales

def get_items_sales(flts):
    """Funcion que obtiene las ordenes de venta que estan en el rango de fechas seleccionado

    Args:
        flts ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Dependiendo de doctype se obtiene el campo de fecha
    date_doc = ''
    if flts.sales_from == 'Sales Order':
        date_doc = 'delivery_date'
    elif flts.sales_from == 'Delivery Note':
        date_doc = 'posting_date'
    elif flts.sales_from == 'Sales Invoice':
        date_doc = 'due_date'
    doctype = flts.sales_from

    # ----Query 1
    # Vamos a buscar todos los items que tengan marcado el campo de incluir en estimacion
    fieldnames = ['name','estimation_name','estimation_uom']
    conditions = [['include_item_in_manufacturing','=',1],['include_in_estimations','=',1]]
    purchase_items = frappe.db.get_list('Item', filters=conditions, fields =fieldnames)

    list_of_boms = []

    # Buscamos los BOMs que tengan estos items en su lista de requerimientos
    for pur_it in purchase_items:
        name = pur_it['name']
        # ----Query 2
        parents_boms = frappe.db.get_list('BOM Item', filters=[['item_code','=',name]], fields =['parent','item_code','item_name','qty','stock_uom']) or []
        if parents_boms != []:
            for p in parents_boms:
                p['estimation_name'] = pur_it['estimation_name']
                p['estimation_uom'] = pur_it['estimation_uom']


            list_of_boms.extend(parents_boms)

    # Buscamos los items de venta que generan esos boms
    sales_items = []
    for boms in list_of_boms:
        name = boms['parent']
        # ----Query 3
        boms_item = frappe.db.get_list('BOM', filters=[['name','=',name],['is_active','=',1]], fields =['item','item_name']) or []
        if boms_item != []:
            for b in boms_item:
                b['estimation_name'] = boms['estimation_name']
                b['estimation_uom'] = boms['estimation_uom']
                b['item_code_base'] = boms['item_code']
                b['item_name_base'] = boms['item_name']
                b['bom_uom'] = boms['stock_uom']
                b['qty_consumed_per_units'] = boms['qty']
            sales_items.extend(boms_item)

    # Por cada item de venta buscamos su factor de conversión
    for si in sales_items:
        # Buscamos el facto de conversion, a la inversa que en el reporte Sales Item availability, desde el BOM ITEM para la estimacion
        si['conversion_factor'] = find_conversion_factor(si['bom_uom'], si['estimation_uom'])[0]['value']
        si['uom'] = si['estimation_uom']

    # Reordenamos por el codigo de item base
    sales_items = sorted(sales_items, key = lambda i: i['item_code_base'],reverse=False)

    return sales_items

def obtain_sales_orders_in_range(flts):
    """Obtenemos las ordenes de venta que estan en el rango de fechas seleccionados

    Args:
        flts ([type]): [description]

    Returns:
        [type]: [description]
    """
    date_doc = ''
    if flts.sales_from == 'Sales Order':
        date_doc = 'delivery_date'
    elif flts.sales_from == 'Delivery Note':
        date_doc = 'posting_date'
    elif flts.sales_from == 'Sales Invoice':
        date_doc = 'due_date'
    doctype = flts.sales_from

    # Obtenemos las ordenes de venta entre el rango de fechas.
    # flts_ = [['docstatus','=',1],[date_doc,'>=',flts.from_date],[date_doc,'<=',flts.to_date]]
    # fieldname = ['name',date_doc]
    # sales_orders = frappe.db.get_list(f"{doctype}", filters=flts_, fields =fieldname) or []

    filt = {'docstatus' : 1, date_doc : ['>=',flts.from_date], date_doc : ['<=',flts.to_date]}
    fieldnames = ['name',date_doc]
    sales_orders = frappe.db.get_values(f"{doctype}", filters=filt, fieldname=fieldnames, as_dict=1) or []

    # Obtenemos los items de cada orden de venta
    so_items = []
    for so in sales_orders:
        # flts1 = [['parent','=',so['name']]]
        # fieldname1 = ['item_code','item_name','qty','amount','stock_uom']
        # sales_orders_items = frappe.db.get_list(f"{doctype} Item", filters=flts1, fields =fieldname1) or []
        flts1 = {'parent' : so['name']}
        fieldname1 = ['item_code','item_name','qty','amount','stock_uom']
        sales_orders_items = frappe.db.get_values(f"{doctype} Item", filters=flts1, fieldname=fieldname1, as_dict=1) or []
        if sales_orders_items != []:
            for s in sales_orders_items:
                s[date_doc] = so[date_doc]
            so_items.extend(sales_orders_items)

    return so_items

def formating_data(estimations, data_of_date):
    """Generamos la estructura de datos con las estimaciones obteniedas

    Args:
        estimations ([type]): [description]
        data_of_date ([type]): [description]

    Returns:
        [type]: [description]
    """
    # Lista de items
    list_of_items = []
    # Por cada fila de estimacion
    for row in estimations:
        # Por cada elemento o item, de la estimaciónes
        for item in row:
            # Buscamos el item_base en la lista de diccicionarios de la lista de los items
            index_ = search_list_of_dict_v(item['item_code_base'], 'item_code',list_of_items)
            # Buscamos la fecha en el rango de fechas para ir a obtener el nombre de la semana y el año
            index_1, index_2 = search_week_in_range(item['year'],item['from_date'],data_of_date)
            # Obtenemos el nombre de la semana y el año "2021 Week01"
            d_date = data_of_date[index_1][index_2]

            # Si encuentra el valor en la lista de items
            if index_ != None:
                # Solo agregamos la fecha con las columnas de estimación en ese lugar
                list_of_items[index_]['time_series_data'].append({
                    d_date['dic_name'] :
                    {
                        'estimated':item.get('estimated', 0),
                        'reserved':item.get('reserved', 0),
                        'sold':item.get('sold', 0),
                        'available':item.get('available', 0)
                    }
                })
            else:
                # Si no esta la fecha, creamos un diccionario con una lista en la llave "time_series_data"
                # De la forma
                """
                    {
                        "item_code": "CULTIVO-0001",
                        "item_name": "Lechuga Butter Lista para Cosechar",
                        "UOM": "Libra",
                        "time_series_data": {
                            "2016W01": {
                                "estimated": null,
                                "reserved": null,
                                "sold": "10.0",
                                "available": null
                            },
                            "..."
                            "2021W01": {
                                "estimated": "500",
                                "reserved": "12.5",
                                "sold": "8.5",
                                "available": "479.0"
                            }
                        }
                    }
                """
                list_of_items.append({
                    'item_code':item['item_code_base'],
                    'item_name':item['item_name_base'],
                    'item_name_estimate':item['item_name_estimate'],
                    'uom':item['uom'],
                    'time_series_data':[
                        {
                            d_date['dic_name']:
                            {
                                'estimated':item.get('estimated', 0),
                                'reserved':item.get('reserved', 0),
                                'sold':item.get('sold', 0),
                                'available':item.get('available', 0)
                            }
                        }
                    ]
                })

    # Agregmos las semanas en donde no tengamos ventas ni estimaciones en el reporte,
    # dependiendo del rango de fechas que hayamos seleccionado
    for row in list_of_items:
        week_list = []
        for i in row['time_series_data']:
            week = list(i.keys())[0]
            week_list.append(week)

        for year in data_of_date:
            for week in year:
                if not week['dic_name'] in week_list:
                    row['time_series_data'].append({
                        week['dic_name']:
                            {
                                'estimated':0, 'reserved':0,
                                'sold':0, 'available':0
                            }
                        })
    return list_of_items

def add_stadistics(data, filters):
    """Agregamos las estadisticas por semana por cada item base

    Args:
        data ([type]): [description]

    Returns:
        [type]: [description]
    """
    # fiscal_years = frappe.db.get_list('Fiscal Year', pluck='name')[0]

    fiscal_year = filters.year_selected

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
                        index_1 = search_list_of_dict_k(wsearch,order_of_week)

                        if index_1 != None:
                            # Solo le agregamos los valores de esa semana, del año seleccionado
                            order_of_week[index_1][wsearch].append(list(d.values())[0])
                        else:

                            order_of_week.append({wsearch:[list(d.values())[0]]})

                elif fiscal_year not in list(d.keys())[0]:
                    if wsearch in list(d.keys())[0]:

                        # Buscamos el indice de la semana en la lista de registros
                        index_2 = search_list_of_dict_k(wsearch,records_of_weeks)
                        # Si ya esta la semana en los registros
                        if index_2 != None:
                            # Solo le agregamos los valores de esa semana, sin importar el año
                            records_of_weeks[index_2][wsearch].append(list(d.values())[0])
                        else:
                            # Sino agregamos un diccionario con el nombre de la semana sin el año
                            # Y agregamos los valores de esa semana, sin importar el año
                            records_of_weeks.append({wsearch:[list(d.values())[0]]})

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

def add_values_of_char(data,filters):
    year = '2021'
    # type_of_char = 'estimated'
    type_of_char = 'available'

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

## --------Reporte por Item
def get_data_for_item(filters):
    if filters.is_sales_item != None:
        if filters.item_selected != None:
            is_item_sales_total_avaiability(filters, filters.item_selected)
        else:
            list_of_item = list_of_item_sales(filters)
            # with open("log.txt",'a',encoding = 'utf-8') as f:
            #     f.write(f"{list_of_item}\n")
            #     f.close()
            for item in list_of_item:

                name_item = item['item_code']
                is_item_sales_total_avaiability(filters, name_item)
            # with open("log.txt",'a',encoding = 'utf-8') as f:
            #     f.write(f"{list_of_item}\n")
            #     f.close()

    elif filters.is_sales_item == None:
        estimated_materials_with_attributes = total_item_availability_estimate_attributes(filters)

        bom_items_list = []
        for material in estimated_materials_with_attributes:
            material_doctype_name = material['name']
            bom_items = find_bom_items(filters, material_doctype_name)
            bom_items_list.extend(bom_items)

        material_and_sales_items = []
        included_items = set()
        for bom_item in bom_items_list:
            bom_name = bom_item['parent']
            boms = find_boms(filters, bom_name)

            if len(boms):
                bom_item['sales_item_code'] = boms[0]['item']
                bom_item['sales_item_qty'] = boms[0]['quantity']
                bom_item['sales_item_uom'] = boms[0]['uom']
                bom_item['sales_item_name'] = boms[0]['item_name']
                bom_item['conversion_factor'] = find_conversion_factor(estimated_materials_with_attributes[0]['amount_uom'], bom_item['stock_uom'])
                bom_item.pop("parent")

                if not boms[0]['item_name'] in included_items:
                    included_items.add(boms[0]['item_name'])
                    material_and_sales_items.append(bom_item)

        matching_sales_order_items = total_sales_items(filters)

        matching_SO_items_draft = total_sales_items_draft(filters)

        material_and_sales_items = sorted(material_and_sales_items, key=lambda x: x['sales_item_code'])

        sales_item_codes = [item['item_code'] for item in matching_sales_order_items]

        items_SO_draft = [item['item_code'] for item in matching_SO_items_draft]

        # with open("log.txt",'a',encoding = 'utf-8') as f:
        #     f.write(f"estimated_materials_with_attributes:{estimated_materials_with_attributes}\nmatching_sales_order_items:{matching_sales_order_items}\nmatching_SO_items_draft:{matching_SO_items_draft}\nmaterial_and_sales_items:{material_and_sales_items}\nsales_item_codes:{sales_item_codes}\nitems_SO_draft:{items_SO_draft}\n\n")
        #     f.close()

        data = process_data(estimated_materials_with_attributes, material_and_sales_items,
                        sales_item_codes, matching_sales_order_items, items_SO_draft, matching_SO_items_draft)
        with open("log.txt",'a',encoding = 'utf-8') as f:
            f.write(f"data{data}\n\n")
            f.close()
    return data

## -------Queries
def total_item_availability_estimate_attributes(filters):
    """
    Returns a list of dictionaries that contain the item availability estimate
    name, estimation name, estimation uom, stock uom, total amount, amount uom
    """
    result = frappe.db.sql(f"""
    SELECT name, estimation_name, estimation_uom, stock_uom,
                 estimate.item_name, estimate.amount, estimate.amount_uom
    FROM `tabItem`
    INNER JOIN
      (SELECT ei.item_code, ei.item_name, SUM(ei.amount) as amount, ei.amount_uom
       FROM `tabItem Availability Estimate` as iae
       INNER JOIN `tabEstimated Item` as ei
       ON iae.name = ei.parent
       WHERE iae.docstatus = 1
       AND ei.docstatus = 1
       AND ei.item_code = '{filters.item_selected}'
       AND (iae.start_date AND iae.end_date BETWEEN '{filters.from_date}' AND '{filters.to_date}')
       GROUP BY ei.item_code) as estimate
       WHERE name=estimate.item_code;
    """, as_dict=True)
    return result

def is_item_sales_total_avaiability(filters, name_item=''):
    #boms_in_items = frappe.db.get_value('BOM', filters={'item':filters.item}, filname=[], as_dict=True)
    #'start_date': ['>=',filters.from_date], 'start_date': ['<=',filters.to_date]

    if name_item != '':
        base_item = []

        boms_of_sales_item = frappe.db.get_value('BOM', filters={'item':name_item}, fieldname=['name'], as_dict=True)

        if boms_of_sales_item != None:
            item_of_bom = frappe.db.get_values('BOM Item', filters={'parent':boms_of_sales_item['name']}, fieldname=['item_code', 'item_name'], as_dict=True)

            if item_of_bom:
                item_ok = {}

                with open("log.txt",'a',encoding = 'utf-8') as f:
                    for item in item_of_bom:
                        item_configure = frappe.db.get_value('Item', filters={'name':item['item_code'], 'include_in_estimations':1, 'is_sales_item':0}, fieldname=['name', 'include_in_estimations','is_sales_item', 'is_purchase_item'], as_dict=True)
                        if item_configure:
                            flt_estimated = {'item_code':item_configure['name']}
                            fnm_estimated = ['item_code', 'item_name', 'amount', 'amount_uom', 'parent']
                            item_availability_estimate_i = frappe.db.get_values('Estimated Item', filters=flt_estimated, fieldname=fnm_estimated, as_dict=True)
                            # f.write(f"item_availability_estimate_i: {item_availability_estimate_i}\n")

                            for item in item_availability_estimate_i:
                                flt_i_estimated = {'name':item['parent'], 'start_date':['>=',filters.from_date], 'end_date':['<=', filters.to_date], 'docstatus':1}
                                fnm_i_estimated = ['name']

                                doct_in_range = frappe.db.get_values('Item Availability Estimate', filters=flt_i_estimated, fieldname=fnm_i_estimated, as_dict=True) or []
                                if doct_in_range != []:
                                    """
                                    if len(doct_in_range) > 0:
                                        msg_validate = f'There are more than one validated doctype, please check the following documents: '
                                        for doc in doct_in_range:
                                            one_string = '<a target="_blank" href="/app/item-availability-estimate/'
                                            two_string = '">'
                                            three_string = '</a>'
                                            msg_validate += f"{one_string}{doc['name']}{two_string}{doc['name']}{three_string} \n"
                                        frappe.msgprint(_(msg_validate))
                                    """
                                    base_item.append(item)
                    # f.write(f"base_item: {base_item[0]}\n")
                    # base_item ya tenemos el monto
                    sale_item = frappe.db.get_value('Item', filters={'name':filters.item_selected}, fieldname=['item_code' , 'stock_uom'], as_dict=True)
                    # f.write(f"sale_item: {sale_item}\n")
                    item_ok['conversion_factor'] = find_conversion_factor(base_item[0]['amount_uom'], sale_item['stock_uom'])
                    # bom_item['conversion_factor'] = find_conversion_factor(estimated_materials_with_attributes[0]['amount_uom'], bom_item['stock_uom'])
                    # f.write(f"item_ok: {item_ok}\n")
                    # f.write(f"-------\n")
                    f.close()

        # item_of_bom = frappe.db.get_values('BOM Item', filters={'parent':})
    else:
        boms_of_sales_item = frappe.db.get_value('BOM', filters={'item':name_item}, fieldname=['name'], as_dict=True)

        if boms_of_sales_item != None:

            item_of_bom = frappe.db.get_values('BOM Item', filters={'parent':boms_of_sales_item['name']}, fieldname=['item_code', 'item_name'], as_dict=True)

            if item_of_bom:

                with open("log.txt",'a',encoding = 'utf-8') as f:
                    for item in item_of_bom:

                        item_configure = frappe.db.get_values('Item', filters={'name':item['item_code'], 'include_in_estimations':1, 'is_sales_item':0}, fieldname=['name', 'include_in_estimations','is_sales_item', 'is_purchase_item'], as_dict=True)

                        if item_configure:
                            f.write(f"item_of_bom: {item_configure}\n")
                    f.write(f"-------\n")
                    f.close()

    """
    with open("log.txt",'a',encoding = 'utf-8') as f:
        f.write(f"{}\n")
        f.close()
    """
    result = []
    return result

def find_conversion_factor(from_uom, to_uom):
    """Function that returns the item code and item name for sales items only.

    Args:
        from_uom: Unit that user wishes to convert from, i.e. Kilogram
        to_uom: Unit that the user wishes to convert to, i.e. Gram
    Returns: A list containing the following object:
        {
            name: the individual ID name for the conversion factor
            from_uom: the name of the origin UOM
            to_uom: the name of the target UOM
            value: the amount by which origin amount must be multiplied to obtain target amount.
        }
        Updated: returns the value of the 'value' key only.
    """

    ## Validar si la dos UOM son iguales, no se hace conversion y se retorna 1,
    #  Si no se encuentra la conversion se muestra un mensaje que diga,
    # "Unit conversion factor for {from_uom} uom to {to_uom} uom not found, creating a new one, please make sure to specify the correct conversion factor."
    # Agregar un link, que cree un nuevo doctype de conversion, ya con los datos cargados que faltan.

    if from_uom == to_uom:
        return [{
            'from_uom':from_uom,
            'to_uom': to_uom,
            'value': 1
        }]
    else:
        result = frappe.db.sql(
            f"""
            SELECT from_uom, to_uom, value FROM `tabUOM Conversion Factor` WHERE from_uom='{from_uom}' AND to_uom='{to_uom}';
            """, as_dict=True
        )

        if result:
            return result
        else:
            frappe.msgprint(f'Unit conversion factor for {from_uom} uom to {to_uom} uom not found, creating a new one, please make sure to specify the correct conversion factor.')

            return [{
            'from_uom':from_uom,
            'to_uom': to_uom,
            'value': 0
            }]

def list_of_item_sales(filters):
    list_of_items = frappe.db.get_values('Item', filters={'is_sales_item':1 ,'include_in_estimations':1}, fieldname=['item_name', 'item_code'], as_dict=True)
    return list_of_items

def total_sales_items(filters):

    doctype = filters.sales_from
    type_of_report = filters.sales_from

    date_doc = ''
    if filters.sales_from == 'Sales Order':
        date_doc = 'transaction_date'
    elif filters.sales_from == 'Delivery Note':
        date_doc = 'posting_date'
    elif filters.sales_from == 'Sales Invoice':
        date_doc = 'posting_date'
    """
    filt = [['docstatus','=',1],[date_doc,'>=',filters.from_date],[date_doc,'<=',filters.to_date]]
    fieldnames = ['name']
    get_list_doctypes = frappe.db.get_list(doctype, filters=filt, fields=fieldnames) or []

    data = []
    for doc in get_list_doctypes:
        doctype = f'{type_of_report} Item'
        filt = [['parent','=',doc['name']]]
        fieldnames = ['parent','item_code', 'delivery_date', 'SUM(stock_qty) AS stock_qty','stock_uom']
        items = frappe.db.get_list(doctype, filters=filt, fields=fieldnames, group_by='item_code')
        data = data + items
    """

    # Hemos dejado de utilizar este query y lo omologamos al codigo anterior
    result = frappe.db.sql(
        f"""
        SELECT soi.item_code, so.{date_doc},
                SUM(soi.stock_qty) as stock_qty, soi.stock_uom
        FROM `tab{doctype} Item` as soi, `tab{doctype}` as so
        WHERE so.docstatus=1 AND so.name = soi.parent AND (so.{date_doc}
        BETWEEN '{filters.from_date}' AND '{filters.to_date}')
        GROUP BY soi.item_code;
        """, as_dict=True)

    # Como estaba
    """
    SELECT soi.item_code, soi.delivery_date,
         SUM(soi.stock_qty) as stock_qty, soi.stock_uom
    FROM `tabSales Order Item` as soi
    WHERE soi.parent IN
      (SELECT so.name FROM `tabSales Order` AS so
        WHERE so.docstatus=1
        AND (delivery_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'))
    GROUP BY soi.item_code;
    """

    return result

def process_data(estimated_materials_with_attributes, material_and_sales_items, sales_item_codes, matching_sales_order_items, items_SO_draft, matching_SO_items_draft):
    """Función para limiar la data del html"""

    empty_row = {}
    data = [empty_row]
    for available_material in estimated_materials_with_attributes:
        # en: We build and add the "grouping row"
        # ES: Construimos y agregamos la fila de agrupamiento
        estimation_name = available_material['estimation_name']
        uom_name = available_material["amount_uom"]
        material_amount = available_material['amount']
        item_code = available_material['name']
        item_name = available_material['item_name']

        #material_amount_html = html_wrap(
        #    str(material_amount), qty_plenty1_strong)
        row_header = {
            "A": estimation_name,
            "B": material_amount,
            "C": _(f"{uom_name}"),
            "D": _(f"Total {uom_name} Sold"),
            "E": "",
            "F": "",
            "G": "",
            "H": item_code,
            "J":item_name
        }

        # We add bold style to the subtitles for the headers.
        # Agregamos negrita a los encabezados
        col_a = _("Code")
        col_b = _("Name")
        col_c = _("Possible")
        col_d = _("UOM")
        col_e = _("Sold")
        col_f = _("Available")
        reserved = _("Reserved")

        row_sub_header = {
            "A": col_a,
            "B": col_b,
            "C": col_c,
            "D": col_d,
            "repeat":reserved,
            "E": col_e,
            "F": col_f,
            "G": ""
        }

        explanation_f = _("Possible - Total Sold")


        row_explanation = {
            "A": "",
            "B": "",
            "C": "",
            "D": "",
            "E": "",
            "F": explanation_f,
            "G": ""
        }

        # Declare the columns where we will place the total sold data
        # Declaremos los columnas en donde vamos a colocar la data del total vendido
        total_sold_column = "E"
        total_difference_column = "F"

        # Set the header and subheader values
        # Indicar el valor del encabezado y los hijos
        data.append(row_header)
        header_idx = len(data) - 1  # track the header index for updates later;
                                    # ES: Rastrear el indice del Header para ser actualizado despues
        data.append(row_sub_header)
        data.append(row_explanation)

        # Initialize the total sold items in the target uom
        # Inicializar los items de venta totales en la unidad de medida objetivo

        # total_target_uom_sold = 0

        # Sum the sales order items and deduct from total available
        # Sumamos los items de la orden de venta (notas de entrega o facturas de venta) y los deducimos del total disponible
        item_deductions = {}
        total_uom_sold = 0
        total_uom_sold_draft = 0

        # with open("log.txt",'a',encoding = 'utf-8') as f:
        #     f.write(f"available_material: {available_material}")
        #     f.close()

        for ms_item in material_and_sales_items:
            if ms_item['item_code'] == available_material['name']:
                # Reset variables
                # Reiniciamos variables
                item_code = ""
                items_sold = 0
                items_sold_draft = 0
                target_uom_sold = 0

                # Total all units sold per sales item
                # Totalizamos todas las unidades vendidas por cada item de venta
                item_code = ms_item['sales_item_code']
                if item_code in sales_item_codes:
                    # sum the stock qty for all sales order items
                    # Sumamos la cantidad de stock para todos los items de las ordenes de venta
                    order_qtys = [item['stock_qty'] for item in matching_sales_order_items if item['item_code'] == ms_item['sales_item_code']]
                    items_sold = math.floor(sum(order_qtys))

                else:
                    items_sold = 0

                # Totalizamos todas las unidades reservadad en el auto repeat por cada item de venta
                if item_code in items_SO_draft:
                    # Sumamos la cantidad de stock para todos los items de las ordenes de venta en borrador
                    order_qtys_draft = [item['stock_qty'] for item in matching_SO_items_draft if item['item_code'] == ms_item['sales_item_code']]
                    items_sold_draft = math.floor(sum(order_qtys_draft))
                else:
                    items_sold_draft = 0

                # with open("log.txt",'a',encoding = 'utf-8') as f:
                #     f.write(f"items_sold_draft: {items_sold_draft} -> items_sold:{items_sold}\n\n")
                #     f.close()
                # Convert the items sold an amt in the target UOM
                # Convertimos los items vendidos a su cantidad en la unidad de medida objetivo
                conversion = ms_item['conversion_factor'][0]['value']

                target_uom_sold = (items_sold * ms_item['stock_qty']) / conversion

                # Agregamos la parte apartada a los totales
                target_uom_sold_draft = (items_sold_draft * ms_item['stock_qty']) / conversion

                # Add sold qty to item_deductions for later use
                # Agregamos la cantidad vendida a las deducciones de los items para posterior uso
                total_uom_sold += target_uom_sold

                total_uom_sold_draft += target_uom_sold_draft

                # item_deductions[item_code] = target_uom_sold
        # We now cross-check, convert and structure our row output.
        # Ahora hacemos un chequeo cruzado, convertimos y estructuramos nuestras filas.
        for ms_item in material_and_sales_items:
            if ms_item['item_code'] == available_material['name']:
                if ms_item['stock_uom'] != available_material['amount_uom']:

                    # Reinitialize variables
                    # Reiniciamos las variables
                    item_code = ""

                    # find conversion factor , from unit is available material amount_uom - INSERT QUERY CALL HERE
                    # Encontramos el factor de conversion, la unidad "from" es igual a la unidad de medida de material disponible - Insertar llamada al query desde aquí
                    conversion_factor = find_conversion_factor(available_material['amount_uom'], ms_item['stock_uom'])
                    conversion_factor_reversed = find_conversion_factor(ms_item['stock_uom'], available_material['amount_uom'])

                    # Warn the user if a conversion factor doesn't exist for
                    # the ms_item

                    # Alertamos al usuario si el factor de conversion no existe para el ms_item
                    if not conversion_factor:
                        frappe.msgprint("A UOM conversion factor is required to convert " + str(available_material['amount_uom']) + " to " + str(ms_item['stock_uom'])+ "; Item:"+str(ms_item['item_code']))

                    elif not conversion_factor_reversed:
                        frappe.msgprint("A UOM conversion factor is required to convert " + str(ms_item['stock_uom']) + " to " + str(available_material['amount_uom']))

                    else:
                        # Convert available_material uom to ms_item uom, by multiplying available material amount by conversion factor found
                        # Convertimos la unidad de medida available_material a la unidad de medida ms_item al multiplicar la cantidad de material disponible por el factor de conversión encontrado.
                        av_mat_amt_converted = float(available_material['amount']) * float(conversion_factor[0]['value'])
                        # Now, we divide the av_mat_amt_converted by the stock_qty to obtain possible quantity
                        # Ahora, dividimos la cantidad de material disponible "av_mat_amt_converted", convertido por la vantidad stock para obtener la cantidad posible

                        # Adjusted quantity takes into account aldready sold uom counts
                        # La cantidad ajustada toma en cuenta la contabilización de las unidades de medida que ya se vendieron
                        adjusted_amt = float(available_material['amount']) - total_uom_sold - total_uom_sold_draft
                        # adjusted_amt = float(available_material['amount'])

                        adjusted_quantity = math.floor((adjusted_amt * float(conversion_factor[0]['value'])) / ms_item['stock_qty'])

                        # Possible quantity is the original converted material amount
                        # without deducting sales
                        # La cantidad posible es la cantidad de material originalmente convertida sin deducir las ventas
                        possible_quantity = av_mat_amt_converted / ms_item['stock_qty']
                        possible_uom = _(ms_item['sales_item_uom'])

                        # Add HTML and CSS styles to certain fields
                        # Agregamo html y css algunos campos
                        pos_qty = str(math.floor(possible_quantity))
                        # quantity_sales_item_html = html_wrap(pos_qty, qty_plenty1_strong)

                        # Build the item code url
                        # Construimos la url del codigo de item
                        item_code = ms_item['sales_item_code']
                        # sales_item_route = f"{item_link_open}/{item_code}'" + item_link_style + item_link_open_end + str(ms_item['sales_item_code']) + item_link_close
                        sales_item_route = str(ms_item['sales_item_code'])

                        # Calculate the amount sold
                        # Calculamos la cantidad vendida
                        if ms_item['sales_item_code'] in sales_item_codes:
                            # sum the stock qty for all sales order items
                            # Sumamos la cantidad stock para todos los items de las ordenes de venta
                            order_qtys = [item['stock_qty'] for item in matching_sales_order_items if item['item_code'] == ms_item['sales_item_code']]
                            sold_quantity = math.floor(sum(order_qtys))
                        else:
                            sold_quantity = 0

                        if ms_item['sales_item_code'] in items_SO_draft:
                            # Sumamos la cantidad stock para todos los items de las ordenes de venta en borrador
                            order_qtys_draft = [item['stock_qty'] for item in matching_SO_items_draft if item['item_code'] == ms_item['sales_item_code']]
                            items_sold_draft = math.floor(sum(order_qtys_draft))
                        else:
                            items_sold_draft = 0

                        # Add HTML to the sold quantity
                        # Agregamos html a la cantidad vendida
                        # quantity_sold_html = html_wrap(str(sold_quantity), qty_sold1_strong)

                        # Calculate the difference of possible and sold items
                        # Calculamos la diferencia de items posibles menos vendidos
                        # TODO: agregar la reserva
                        available_quantity = int(possible_quantity - sold_quantity - items_sold_draft)

                        # available_quantity_html = html_wrap(str(adjusted_quantity), qty_plenty1_strong)

                        # Populate the row
                        # Llenamos la fila con los resultados anteriores
                        sales_item_row = {
                            "A" : sales_item_route,
                            "B" : str(ms_item['sales_item_name']),
                            "C" : pos_qty,
                            "D" : _(possible_uom),
                            "repeat" : items_sold_draft,
                            "E" : sold_quantity,
                            "F" : str(adjusted_quantity),
                            "G" : "",
                            "H" : str(ms_item['sales_item_code']),
                            "J" : str(ms_item['sales_item_name'])
                        }
                        data.append(sales_item_row)

                else:
                    print('Units are the same, no need for conversion.')
            else:
                pass

        # Add the target uom total to the header
        # Agregamos el total de la unidad de medida objetivo al encabezado
        data[header_idx][total_sold_column] = str(total_uom_sold)
        data[header_idx]['repeat'] = str(total_uom_sold_draft)

        # Add the target uom total difference to the header
        # Agregamos la diferencia total de la unidad de medida objetivo al encabezado
        total_uom_diff = str(material_amount - total_uom_sold - total_uom_sold_draft)
        data[header_idx][total_difference_column] = total_uom_diff

        # We add an empty row after a set of products for easier reading.
        # Agregamos una fila vacía luego de un set de productos para facilitar la lectura
        data.append(empty_row)

        if len(data) > 1:
            val_a = _("Report generated at")
            val_b = _(f'{datetime.now().strftime("%H:%M:%S")}')
            val_c = _(f'{datetime.now().strftime("%d/%m/%Y")}')

            data[0] = {'A' :val_a, 'B' :val_b, 'C' :val_c}

    return data

def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=4, default=str))
