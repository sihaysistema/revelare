# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
# import frappe

import frappe
from frappe import _
from datetime import datetime
from erpnext.accounts.report.utils import convert  # value, from_, to, date
import json
from frappe.utils import nowdate, cstr, flt

import pandas as pd
import numpy as np

from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import item_availability_estimates_range, periods_estimated_items, estimation_item_attributes, find_bom_items, find_boms, find_sales_items

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
            "width": 180
        }
    ]

    return columns

def get_data(filters):
    """Function to obtain and process the data.

    Args:
        filters ([type]): [description]

    Returns:
        dicitonary list: A list of dictionaries, in ascending order, each key corresponds to a 
        column name as declared in the function above, and the value is what will be shown.

    """
    # --------- EMPTY ROW ----------
    empty_row = {}
    data = [empty_row]
    # --------- Testing styles for report START ----------
    quantity_style_1 = "<span style='color: green; float: right; text-align: right; vertical-align: text-top;'><strong>"
    quantity_style_2 = "</strong></span>"
    quantity_material = quantity_style_1 + str(35) + quantity_style_2
    quantity_sales_item = quantity_style_1 + str(70) + quantity_style_2
    row1 = {
        "material": "Albahaca",
        "quantity": quantity_material,
        "uom": "Pound",
        "item_code": "7401168800724",
        "item_name": "Albahaca 8Oz",
        "possible_quantity": quantity_sales_item
    }

    for x in range(4):
        data.append(row1)
    # --------- Testing styles for report ENDS ----------

    # Obtain Valid Item Availability Estimates for dates from our query functions.
    estimates = item_availability_estimates_range(filters)
    # Just the name
    # estimate_data = estimates[0]['name']

    # We create an empty list where we will add Item Availability Estimate doctype names 
    iae_list = []
    # we now add them
    for x in estimates:
        iae_list.append(x['name'])

    # We are now ready to assemble a list of Material items, for those estimate titles that fit
    # [{'item_code': 'MATITEMCODE-001', 'amount':'15.0', 'amount_uom': 'Pound'}]
    # since we will do several rounds of list gathering, we will extend a single list of objects.
    available_material_list = []
    for x in iae_list:
        materials = periods_estimated_items(filters, x)
        available_material_list.extend(materials)

    # estimation item attributes
    # We now create a list of estimation item attributes
    # [{'name': 'CULTIVO-0069', 'estimation_name': 'Perejil', 'estimation_uom': 'Pound', 'stock_uom': 'Onza'}]
    # This list is already "filtered" and curated to include all the REQUESTED estimation item codes and attributes
    available_materials_with_attributes = []
    for x in available_material_list:
        item_attributes = estimation_item_attributes(filters, x['item_code'])
        # we extend the list along with the item attributes, so it is only one list, for each item in the material list.
        available_materials_with_attributes.extend(item_attributes)

    # Now we find the BOM names based on the names of material items in our item_attributes_list
    # [{'item_code': 'CULTIVO-0069', 'parent': 'BOM-7401168802186-001', 'stock_qty': 6.0, 'stock_uom': 'Onza'}]
    # The assembled object contains  
    bom_names_list = []
    for x in available_materials_with_attributes:
        bom_items = find_bom_items(filters, x['name'])
        bom_names_list.extend(bom_items)
        '''
        row = {
            "material": "Albahaca",
            "quantity": quantity_material,
            "uom": "PRUEBA",
            "item_code": str(bom_names_list),
            "item_name": "",
            "possible_quantity": quantity_sales_item
        }
        data.append(row)
        '''
    
    # we get sales item code, quantity obtained, and uom obtained for each bom parent.
    material_and_sales_items = []
    for x in bom_names_list:
        boms = find_boms(filters, x['parent'])
        # We rearrange the current dictionary, assigning values from returned keys in this list
        # to new keys in this object.
        # We also drop the parent key in the existing
        #x['sales_item_code'] = boms['item']
        #x['sales_item_qty'] = boms['quantity']
        #x['sales_item_uom'] = boms['uom']
        x['sales_item_code'] = boms[0]['item']
        x['sales_item_qty'] = boms[0]['quantity']
        x['sales_item_uom'] = boms[0]['uom']
        x.pop("parent")
        material_and_sales_items.append(x)


    row = {
            "material": "Albahaca",
            "quantity": quantity_material,
            "uom": "PRUEBA",
            "item_code": str(material_and_sales_items),
            "item_name": "",
            "possible_quantity": quantity_sales_item
        }

    data.append(row)

    return data
'''
initial_vat_payable = {
 "doc_type": "",
 "doc_id": "<strong>Saldo Inicial IVA por pagar</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "300.00",
 "trans_total": "",
 "currency": "GTQ"
 }





    return data



def get_data(filters):
 empty_row = {}
 data = [empty_row]
 initial_vat_payable = {
 "doc_type": "",
 "doc_id": "<strong>Saldo Inicial IVA por pagar</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "300.00",
 "trans_total": "",
 "currency": "GTQ"
 }
 por_pagar_header = {
 "doc_type": "",
 "doc_id": "<strong>IVA POR PAGAR</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "",
 "trans_total": "",
 "currency": "GTQ"
 }
 por_pagar_footer = {
 "doc_type": "",
 "doc_id": "<strong>SUBTOTAL IVA POR PAGAR</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "672.00",
 "trans_total": "",
 "currency": "GTQ"
 }
 por_cobrar_header = {
 "doc_type": "",
 "doc_id": "<strong>IVA POR COBRAR</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "",
 "trans_total": "",
 "currency": "GTQ"
 }
 por_cobrar_footer = {
 "doc_type": "",
 "doc_id": "<strong>SUBTOTAL IVA POR COBRAR</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "36.00",
 "trans_total": "",
 "currency": "GTQ"
 }
 payable_vat_this_month = {
 "doc_type": "",
 "doc_id": "<strong>IVA a liquidar este mes</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "636.00",
 "trans_total": "",
 "currency": "GTQ"
 }
 total_vat_payable_now = {
 "doc_type": "",
 "doc_id": "<strong>Monto a Liquidar Incluyendo Saldos pendientes</strong>",
 "trans_date": "",
 "vat_debit": "",
 "vat_credit": "936.00",
 "trans_total": "",
 "currency": "GTQ"
 }
 data.append(initial_vat_payable)
 data.append(por_pagar_header)

 # en_US: Getting the transactions for vat payable accounts to insert the rows, for this month.
 # es: Obtenemos las transacciones de IVA por pagar de este mes para insertar las filas.

 payable_data = get_vat_payable_data(filters)
 if len(payable_data) > 0:
 por_pagar = apply_on_site_links(payable_data)
 data.extend(por_pagar)

 data.append(por_pagar_footer)
 data.append(empty_row)
 data.append(empty_row)
 data.append(por_cobrar_header)

 # en_US: Getting the transactions for vat receivable accounts to insert the rows, for this month.
 # es: Obtenemos las transacciones de IVA por cobrar de este mes para insertar las filas.
 receivable_data = get_vat_receivable_data(filters)
 if len(receivable_data) > 0:
 por_cobrar = apply_on_site_links(receivable_data)
 data.extend(por_cobrar)

 data.append(por_cobrar_footer)
 data.append(empty_row)
 data.append(empty_row)
 data.append(payable_vat_this_month)
 data.append(empty_row)
 data.append(total_vat_payable_now)

 return data
'''