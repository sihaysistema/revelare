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
import math

from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import item_availability_estimates_range, periods_estimated_items, estimation_item_attributes, find_bom_items, find_boms, find_sales_items, find_conversion_factor

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

    old_columns = [
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

    columns = [
        {
            "label": _("A"),
            "fieldname": "A",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("B"),
            "fieldname": "B",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("C"),
            "fieldname": "C",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("D"),
            "fieldname": "D",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("E"),
            "fieldname": "E",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("F"),
            "fieldname": "F",
            "fieldtype": "Data",
            "width": 90
        },
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
        "A": "Albahaca",
        "B": quantity_material,
        "C": "Pound",
        "D": "7401168800724",
        "E": "Albahaca 8Oz",
        "F": quantity_sales_item
    }

    # for x in range(4):
    #    data.append(row1)
    # --------- Testing styles for report ENDS ----------

    # ----- QUERY # 1 BEGIN -----
    # Obtain Valid Item Availability Estimates for dates from our query functions.
    estimates = item_availability_estimates_range(filters)
    # Just the name
    # estimate_data = estimates[0]['name']
    
    # en: We create an empty list where we will add Item Availability Estimate doctype names 
    # es-GT: Creamos una lista vacia para luego agregar los nombres de los doctypes de Estimados de Disponibilidad
    iae_list = []
    # we now add them
    for x in estimates:
        iae_list.append(x['name'])
    # ----- QUERY # 1 END -----

    # ----- QUERY # 2 BEGIN -----
    # We are now ready to assemble a list of Material items, for those estimate titles that fit
    # [{'item_code': 'CULTIVO-0069', 'amount':'15.0', 'amount_uom': 'Pound'}]
    # since we will do several rounds of list gathering, we will extend a single list of objects.
    available_material_list = []
    for x in iae_list:
        materials = periods_estimated_items(filters, x)
        available_material_list.extend(materials)
    # ----- QUERY # 2 END -----

    # ----- QUERY # 3 BEGIN -----
    # estimation item attributes
    # We now create a list of estimation item attributes
    # [{'name': 'CULTIVO-0069', 'estimation_name': 'Perejil', 'estimation_uom': 'Pound', 'stock_uom': 'Onza'}]
    # This list is already "filtered" and curated to include all the REQUESTED estimation item codes and attributes
    available_materials_with_attributes = []
    for x in available_material_list:
        item_attributes = estimation_item_attributes(filters, x['item_code'])
        # we extend the list along with the item attributes, so it is only one list, for each item in the material list.
        available_materials_with_attributes.extend(item_attributes)
    # ----- QUERY # 3 END -----

    # ----- QUERY # 4 BEGIN -----
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
    # ----- QUERY # 4 END -----

    # ----- QUERY # 5 BEGIN -----
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
        x['sales_item_name'] = boms[0]['item_name']
        x['conversion_factor'] = find_conversion_factor(available_material_list[0]['amount_uom'], x['stock_uom'])
        x.pop("parent")
        material_and_sales_items.append(x)
    '''
    row = {
            "A": "Albahaca",
            "B": quantity_material,
            "C": "PRUEBA",
            "D": str(material_and_sales_items),
            "E": "",
            "F": quantity_sales_item
        }
    '''
    # ----- QUERY # 5 END -----

    # data.append(row)
    test_data1 = [{'A': 'Perejil', 'B': '4.0', 'C': 'Pound', 'D': '', 'E': '', 'F': '', 'G': ''}, {'A': '', 'B': '', 'C': '', 'D': '2186', 'E': 'Perejil 6Oz', 'F': '10', 'G': 'Unidades'}, {'A': '', 'B': '', 'C': '', 'D': '2193', 'E': 'Perejil 8Oz', 'F': '8', 'G': 'Unidades'}, {'A': '', 'B': '', 'C': '', 'D': '2209', 'E': 'Perejil 1Lb', 'F': '4', 'G': 'Unidades'}, {'A': '', 'B': '', 'C': '', 'D': '2179', 'E': 'Perejil 5Oz', 'F': '12', 'G': 'Unidades'}, {'A': '', 'B': '', 'C': '', 'D': '2278', 'E': 'Perejil .5Oz', 'F': '128', 'G': 'Unidades'}, {'A': '', 'B': '', 'C': '', 'D': '2674', 'E': 'Perejil 1Oz', 'F': '64', 'G': 'Unidades'}, {}]

    # We go through each item in the available_material_list.
    
    # ----- DEBUGGING BEGIN -----
    frappe.msgprint(iae_list)
    # ----- DEBUGGING ENDS -----


    # ----- PROCESS DATA BEGIN -----
    # en: We begin by 
    # es-GT:
    for available_material in available_material_list:
        # en: We add the "grouping row"
        # we need to find the estimation name
        estimation_name = ""
        for x in available_materials_with_attributes:
            if x['name'] == available_material['item_code']:
                estimation_name = x['estimation_name']
                # print(estimation_name)
                break
            else:
                x = None
        
        row_header = {
                        "A": estimation_name,
                        "B": available_material['amount'],
                        "C": _(available_material['amount_uom']),
                        "D": "",
                        "E": "",
                        "F": "",
                        "G": ""
                    }
        data.append(row_header)

        # We now cross-check, convert and structure our row output.
        for pair in material_and_sales_items:
            if pair['item_code'] == available_material['item_code']:
                #code exists, do this
                # print("item code code exists")
                # amount_uom is in A
                # Item stock uom is in B
                if pair['stock_uom'] != available_material['amount_uom']:
                    # print('Must convert units!')
                    # find conversion factor , from unit is available material amount_uom - INSERT QUERY CALL HERE
                    conversion_factor = find_conversion_factor(available_material['amount_uom'], pair['stock_uom'])
                    # Convert available_material uom to pair uom, by multiplying available material amount by conversion factor found
                    conversion_factor1 = [{'from_uom': 'Pound', 'to_uom': 'Onza', 'value': 16.0}]
                    
                    av_mat_amt_converted = float(available_material['amount']) * float(conversion_factor[0]['value'])
                    # print('Available material amount has been converted to stock units in BOM for sales item')
                    
                    # print('Possible amount')
                    # Now, we divide the av_mat_amt_converted by the stock_qty to obtain possible quantity
                    possible_quantity = av_mat_amt_converted / pair['stock_qty']
                    
                    if math.floor(possible_quantity) > 1:
                        possible_uom = "Unidades"
                    else:
                        possible_uom = "Unidad"
                    # print(pair['sales_item_code'][-4:] + ' ' + pair['sales_item_name'] + ' ' + str(math.floor(possible_quantity)) + ' ' + possible_uom)
                    
                    
                    sales_item_row = {
                        "A": "",
                        "B": "",
                        "C": "",
                        "D": str(pair['sales_item_code'][-4:]),
                        "E": str(pair['sales_item_name']),
                        "F": str(math.floor(possible_quantity)),
                        "G": possible_uom
                    }
                    data.append(sales_item_row)
                else:
                    print('Units are the same, no need for conversion.')
            else:
                pass
        
        # We add an empty row after a set of products for easier reading
        data.append(empty_row)
    # ----- PROCESS DATA END -----
    return data
    #return test_data1