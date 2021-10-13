# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import calendar
import json
from datetime import date, datetime, time, timedelta

import frappe
from frappe import _, _dict, scrub

from revelare.revelare.report.sales_item_availability.sales_item_availability import get_data
from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import (find_conversion_factor,
                                                                                              total_sales_items)

from revelare.revelare.report.historical_weekly_item_amounts.utils
import get_range_of_date
import is_digit
import is_string
import list_of_ranges_date
import search_list_of_dict_k
import search_list_of_dict_v


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

def estimations_reports(flt, data_of_date):

    reports = []
    for year in data_of_date:
        # Por cada año
        for week in year:
            # Por cada semana modificamos el filtro generado artificialmente
            flt.from_date = week['from_date']
            flt.to_date = week['to_date']
            rep = prepair_data_of_report(flt)
            # Si hay data, entonce la agregamos la lista de diccionarios
            if rep != [{}]:
                reports.append(rep)
            else:
                sold(flt)
    return reports

def prepair_data_of_report(flt):
    # Llamamos la funcion get_data del reporte sales_item_availability
    rep = get_data(flt, False)
    if rep != [{}]:
        # TODO: Obtener el formato de semana para agregar lo a la lista de diccionarios
        # for row in rep:


    return [{}]

def sold(flt):

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
        for i_s in items_sales:
            index = search_list_of_dict_k(i_s['item_code_base'], dic_sold)
            if index != None:
                dic_sold[index][i_s['item_code_base']].append(i_s)
            else:
                dic_sold.append({i_s['item_code_base']:[i_s]})

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

        solds_totals = []
        for dic_s in dic_sold:
            item_code = list(dic_s.keys())[0]
            sum_items_sold = 0
            for item in list(dic_s.values()):

                for i in item:
                    if i.get('conversion_sold','') != '':
                        sum_items_sold += i['conversion_sold']
            if  sum_items_sold != 0:
                solds_totals.append({'item_code': item_code, 'sold':sum_items_sold})

    return solds_totals

def item_availability_estimate_attributes(flts):
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

    for si in sales_items:
        # Buscamos el facto de conversion, a la inversa que en el reporte Sales Item availability, desde el BOM ITEM para la estimacion
        si['conversion_factor'] = find_conversion_factor(si['bom_uom'], si['estimation_uom'])[0]['value']

    sales_items = sorted(sales_items, key = lambda i: i['item_code_base'],reverse=False)

    return sales_items

def get_sums_sales_items_qty(flt):
    sums_items_qty = []

    items_sales = item_availability_estimate_attributes(flt)
    sales_order = obtain_sales_orders_in_range(flt)
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

def obtain_sales_orders_in_range(flts):
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






def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'a') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
