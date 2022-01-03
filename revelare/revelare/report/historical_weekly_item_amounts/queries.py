# Copyright (c) 2020, Si Hay Sistema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
from datetime import datetime, timedelta

import frappe
import numpy as np
from frappe import _, _dict, scrub
from frappe.utils import cstr, flt, nowdate

@frappe.whitelist()
def get_configured_item(qty=4):
    qty = int(qty)
    flts = {'include_in_estimations':1,'is_sales_item':0}
    fldname = ['name','item_code','item_name']
    result = frappe.db.get_values('Item', filters=flts, fieldname=fldname,as_dict=True)
    if len(result) >= qty:
        result = result[:qty]

    return result

@frappe.whitelist()
def get_qty_element():
    flts = {'include_in_estimations':1,'is_sales_item':0}
    fldname = ['name','item_code','item_name']
    result = frappe.db.get_values('Item', filters=flts, fieldname=fldname,as_dict=True)

    return {'qty': len(result),'items':result}

def boms_item(filters):
    result = frappe.db.sql(f'''
    SELECT bi.item, bii.item_code
        FROM `tabBOM` AS bi
        INNER JOIN `tabBOM Item` AS bii
        ON bii.parent = bi.name
        WHERE bi.docstatus = 1 AND bi.is_default = 1
        AND bii.item_code = '{filters.item_selected}'
        GROUP BY bi.item;
    ''', as_dict=True)
    return result

def from_data(item_sales):
    result = frappe.db.sql(f'''
    SELECT soi.item_code,
    count(so.delivery_date) AS cantidad,
    YEAR(so.delivery_date) AS anio,
    MONTH(so.delivery_date) AS mes
    FROM `tabSales Order` AS so
    INNER JOIN `tabSales Order Item` AS soi
    ON soi.parent = so.name
    WHERE so.delivery_date IS NOT NULL
    AND so.docstatus = 1
    AND soi.item_code = '{item_sales}'
    GROUP BY YEAR(so.delivery_date), MONTH(so.delivery_date) ASC;
    ''', as_dict=True)
    return result

def get_sales_order_individual(item_code_sale):
    result = frappe.db.sql(f'''
    SELECT soi.item_code AS item, soi.item_name,  so.transaction_date AS fecha,
    SUM(soi.qty) AS `Cant SO`, boi.uom, boi.qty AS `Cant IB`, (SUM(soi.qty) * boi.qty) AS total
    FROM `tabSales Order` AS so
    INNER JOIN `tabSales Order Item` AS soi ON soi.parent = so.name
    INNER JOIN `tabItem` AS i ON soi.item_code = i.name
    INNER JOIN `tabBOM` AS bo ON soi.item_code = bo.item
    INNER JOIN `tabBOM Item` AS boi ON boi.parent = bo.name
    WHERE so.docstatus = 1 AND i.include_in_estimations = 1
    AND soi.item_code = '{item_code_sale}' AND soi.qty > 0
    GROUP BY so.transaction_date ASC
    ORDER BY so.transaction_date ASC;
    ''', as_dict=True)
    return result

def get_availability_estimates():
    result = frappe.db.sql(f'''
    SELECT iae.start_date, iae.end_date, ei.item_code, ei.item_name, ei.amount, ei.amount_uom
    FROM `tabItem Availability Estimate` AS iae
    INNER JOIN `tabEstimated Item` AS ei ON ei.parent = iae.name
    WHERE iae.docstatus = 1;
    ''', as_dict=True) or []
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

# Para debug
def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))

