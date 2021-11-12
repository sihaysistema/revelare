# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import calendar
import json
import statistics as stdic
from datetime import date, datetime, time, timedelta

import frappe
from frappe import _, _dict, scrub

from revelare.revelare.report.historical_weekly_item_amounts.utils import (get_range_of_date, is_digit, is_string,
                                                                           list_of_ranges_date, search_list_of_dict_k,
                                                                           search_list_of_dict_v, search_week_in_range)
from revelare.revelare.report.sales_item_availability.sales_item_availability import get_data
from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import (find_conversion_factor,
                                                                                              total_sales_items)


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

    flt = frappe._dict({
            "from_date": "",
            "to_date": "",
            "sales_from": "Sales Order"
            })
    # Obtener fechas y rango por numero de semana
    data_of_date = get_range_of_date(filters)
    # Obtenemos las estimaciones en reporte y las ordenes de venta
    estimations = estimations_reports(flt, data_of_date, filters)

    # Formatemos los obtenidos
    list_of_items = formating_data(estimations, data_of_date)

    #Agregando estadisticas
    list_of_items = add_stadistics(list_of_items)
    list_of_items = add_values_of_char(list_of_items, flt)
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
    rep = get_data(flt, False)
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
                        with open("log.txt",'a',encoding = 'utf-8') as f:
                            f.write(f"{dic_s}\n")
                            f.close()
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
    flts_ = [['docstatus','=',1],[date_doc,'>=',flts.from_date],[date_doc,'<=',flts.to_date]]
    fieldname = ['name',date_doc]
    sales_orders = frappe.db.get_list(f"{doctype}", filters=flts_, fields =fieldname) or []

    # Obtenemos los items de cada orden de venta
    so_items = []
    for so in sales_orders:
        flts1 = [['parent','=',so['name']]]
        fieldname1 = ['item_code','item_name','qty','amount','stock_uom']
        sales_orders_items = frappe.db.get_list(f"{doctype} Item", filters=flts1, fields =fieldname1) or []
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

def add_stadistics(data):
    """Agregamos las estadisticas por semana por cada item base

    Args:
        data ([type]): [description]

    Returns:
        [type]: [description]
    """
    # fiscal_years = frappe.db.get_list('Fiscal Year', pluck='name')[0]

    fiscal_years = '2021'

    # Por cada item en la data
    for dat in data:
        # Creamos la lista de registros por semana
        records_of_weeks = []
        # Por cada semana en el rango
        for week_ in range(1, 54):
            # Obtenemos el numero de semana a dos digitos
            no_week = str(week_).zfill(2)

            # Por cada semana en la serie de datos
            for d in dat['time_series_data']:
                # Buscamos el numero de semana en la lista de datos "Week01"
                wsearch = f'Week{no_week}'
                # Si la semana a buscar por cada año esta en la llave "2018 Week01", "2019 Week01", "2020 Week01"
                if wsearch in list(d.keys())[0]:

                    # fiscal_years not in list(d.keys())[0]
                    if fiscal_years not in list(d.keys())[0]:
                        # Buscamos el indice de la semana en la lista de registros
                        index = search_list_of_dict_k(wsearch,records_of_weeks)
                        # Si ya esta la semana en los registros
                        if index != None:
                            # Solo le agregamos los valores de esa semana, sin importar el año
                            records_of_weeks[index][wsearch].append(list(d.values())[0])
                        else:
                            # Sino agregamos un diccionario con el nombre de la semana sin el año
                            # Y agregamos los valores de esa semana, sin importar el año
                            records_of_weeks.append({wsearch:[list(d.values())[0]]})

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

def add_values_of_char(data, flt):
    dicToJSON('data_', data)
    year = '2021'

    for dat in data:
        year_select = []
        for item in dat['time_series_data']:
            name = list(item.keys())[0]
            if year in name:
                year_select.append(item)
        dat['year_select'] = year_select

    for dat in data:
        dat['labels'] = []
        dat['values'] = []
        for item in dat['year_select']:
            dat['labels'].append(list(item.keys())[0])
            dat['values'].append(list(item.values())[0]['estimated'])

    type_of_char = 'estimated'
    for dat in data:
        dat['value1'] = []
        dat['value2'] = []
        dat['value3'] = []

        for item in dat['statistics']:
            stadistic = list(item.values())[0]
            data_selec = stadistic[type_of_char]
            dat['value1'].append(data_selec['max'])
            dat['value2'].append(data_selec['avg'])
            dat['value3'].append(data_selec['min'])

    return data


def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=4, default=str))
