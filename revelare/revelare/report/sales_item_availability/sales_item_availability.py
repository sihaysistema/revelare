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

from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import item_availability_estimates_range, periods_estimated_items, estimation_item_attributes, find_bom_items, find_boms, find_sales_items, find_conversion_factor, find_sales_orders, find_sales_order_items


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
            "width": 120
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
    # --------- STYLES DEIFNITIONS BEGIN ----------
    quantity_style_plenty_1 = "<span style='color: black; background-color: orange; float: right; text-align: right; vertical-align: middle; height: 100%; width: 100%;'><strong>"
    quantity_style_plenty_2 = "</strong></span>"
    quantity_style_few_1 = "<span style='color: black; background-color: blue; float: right; text-align: right; vertical-align: text-top;'><strong>"
    quantity_style_few_2 = "</strong></span>"
    quantity_style_sold_1 = "<span style='color: black; background-color: #60A917; float: right; text-align: right; vertical-align: middle; height: 100%; width: 100%;'><strong>"
    quantity_style_sold_2 = "</strong></span>"
    item_link_open = "<a href='#Form/Item/' style='color: #1862AA;'"
    item_link_open_end = " target='_blank'>"
    item_link_close = "</a>"

    # quantity_material = quantity_style_plenty_1 + \
    #     str(35) + quantity_style_plenty_2
    # quantity_sales_item = quantity_style_plenty_1 + \
    #     str(70) + quantity_style_plenty_2
    # row1 = {
    #     "A": "Albahaca",
    #     "B": quantity_material,
    #     "C": "Pound",
    #     "D": "7401168800724",
    #     "E": "Albahaca 8Oz",
    #     "F": quantity_sales_item
    # }

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
    # We are now ready to assemble a list of Material items, for those IAE names that fit date filters.
    # [{'item_code': 'CULTIVO-0069', 'amount':'15.0', 'amount_uom': 'Pound'}]
    # since we will do several rounds of list gathering, we need to extend the list, and if there are objects with same item code, we want only ONE object for each item_code, but with the total amount of Item Availability Estimates
    available_material_list_raw = []
    for x in iae_list:
        materials = periods_estimated_items(filters, x)
        available_material_list_raw.extend(materials)
    # ----- QUERY # 2 END -----

    # ----- UNIFY ITEM CODES AND ADD UP AMOUNTS BEGIN -----
    # We want unique item codes and amounts, such that each material item estimate is included only ONCE.
    available_material_list = sum_and_convert_available_material_list(
        available_material_list_raw)

    # Cleaning things up.
    available_material_list_raw.clear()
    # ----- UNIFY ITEM CODES AND ADD UP AMOUNTS END -----

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
        # x['sales_item_code'] = boms['item']
        # x['sales_item_qty'] = boms['quantity']
        # x['sales_item_uom'] = boms['uom']
        x['sales_item_code'] = boms[0]['item']
        x['sales_item_qty'] = boms[0]['quantity']
        x['sales_item_uom'] = boms[0]['uom']
        x['sales_item_name'] = boms[0]['item_name']
        x['conversion_factor'] = find_conversion_factor(
            available_material_list[0]['amount_uom'], x['stock_uom'])
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

    # ----- QUERY # 6 BEGIN -----
    # Sales Order query, return all sales order names that fit within the dates in report filter.
    sales_orders = find_sales_orders(filters)

    # en: We create an empty list where we will add Item Availability Estimate doctype names
    # es-GT: Creamos una lista vacia para luego agregar los nombres de los doctypes de Estimados de Disponibilidad
    sales_order_list = []
    # we now add them
    for sales_order in sales_orders:
        sales_order_list.append(sales_order['name'])
    # ----- QUERY # 6 BEGIN -----

    # ----- QUERY # 7 BEGIN -----
    matching_sales_order_items = []
    for sales_order in sales_order_list:
        matching_sales_order_items.extend(
            find_sales_order_items(filters, sales_order))
    # ----- QUERY # 7 BEGIN -----

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
                break
            else:
                x = None

        material_amount_html = quantity_style_plenty_1 + \
            str(available_material['amount']) + quantity_style_plenty_2
        row_header = {
            "A": estimation_name,
            "B": material_amount_html,
            "C": _(available_material['amount_uom']),
            "D": "",
            "E": "",
            "F": "",
            "G": ""
        }
        # We add bold style to the subtitles for the headers.
        bld_start = "<strong>"
        bld_end = "</strong>"
        col_a = bld_start + _("Code") + bld_end
        col_b = bld_start + _("Name") + bld_end
        col_c = bld_start + _("Possible") + bld_end
        col_d = bld_start + _("UOM") + bld_end
        col_e = bld_start + _("Sold") + bld_end
        col_f = bld_start + _("Available") + bld_end

        row_sub_header = {
            "A": col_a,
            "B": col_b,
            "C": col_c,
            "D": col_d,
            "E": col_e,
            "F": col_f,
            "G": ""
        }
        data.append(row_header)
        data.append(row_sub_header)

        # Get the sales order quantities for items
        sales_item_codes = [item['item_code']
                            for item in matching_sales_order_items]

        # Sort material and sales items list by order of sales item code
        # Should print the code column in order like: -001, -002, -003, ...
        material_and_sales_items = sorted(
            material_and_sales_items, key=lambda x: x['sales_item_code'])

        # We now cross-check, convert and structure our row output.
        for pair in material_and_sales_items:
            if pair['item_code'] == available_material['item_code']:
                # code exists, do this
                # print("item code code exists")
                # amount_uom is in A
                # Item stock uom is in B
                if pair['stock_uom'] != available_material['amount_uom']:
                    # print('Must convert units!')
                    # find conversion factor , from unit is available material amount_uom - INSERT QUERY CALL HERE
                    conversion_factor = find_conversion_factor(
                        available_material['amount_uom'], pair['stock_uom'])

                    # Warn the user if a conversion factor doesn't exist for
                    # the pair
                    if not conversion_factor:
                        frappe.msgprint("A UOM conversion factor is required to convert " + str(
                            available_material['amount_uom']) + " to " + str(pair['stock_uom']))
                    else:
                        # Convert available_material uom to pair uom, by multiplying available material amount by conversion factor found
                        av_mat_amt_converted = float(
                            available_material['amount']) * float(conversion_factor[0]['value'])
                        # print('Available material amount has been converted to stock units in BOM for sales item')

                        # print('Possible amount')
                        # Now, we divide the av_mat_amt_converted by the stock_qty to obtain possible quantity
                        possible_quantity = av_mat_amt_converted / \
                            pair['stock_qty']

                        if math.floor(possible_quantity) > 1:
                            possible_uom = _(pair['sales_item_uom'] + 's')
                        else:
                            possible_uom = _(pair['sales_item_uom'])
                        # print(pair['sales_item_code'][-4:] + ' ' + pair['sales_item_name'] + ' ' + str(math.floor(possible_quantity)) + ' ' + possible_uom)

                        # Add HTML and CSS styles to certain fields
                        quantity_sales_item_html = quantity_style_plenty_1 + \
                            str(math.floor(possible_quantity)) + \
                            quantity_style_plenty_2
                        sales_item_route = item_link_open + \
                            str(pair['sales_item_code']) + item_link_open_end + \
                            str(pair['sales_item_code'][-4:]) + item_link_close

                        if pair['sales_item_code'] in sales_item_codes:
                            idx = sales_item_codes.index(
                                pair['sales_item_code'])
                            item_sold = matching_sales_order_items[idx]
                            sold_quantity = math.floor(item_sold['stock_qty'])
                        else:
                            sold_quantity = 0
                        quantity_sold_html = quantity_style_sold_1 + \
                            str(sold_quantity) + quantity_style_sold_2

                        # Calculate the difference of possible and sold items
                        available_quantity = int(
                            possible_quantity - sold_quantity)
                        available_quantity_html = quantity_style_plenty_1 + \
                            str(available_quantity) + quantity_style_plenty_2

                        # Populate the row
                        sales_item_row = {
                            "A": sales_item_route,
                            "B": str(pair['sales_item_name']),
                            "C": quantity_sales_item_html,
                            "D": possible_uom,
                            "E": quantity_sold_html,
                            "F": available_quantity_html,
                            "G": ""
                        }
                        data.append(sales_item_row)
                else:
                    print('Units are the same, no need for conversion.')
            else:
                pass

        # We add an empty row after a set of products for easier reading.
        data.append(empty_row)
    # ----- PROCESS DATA END -----
    return data
    # return test_data1


def make_list_of_unique_codes(available_material_list):
    """Function that makes a list of unique item codes

    Args:
        available_material_list: It expects a list similar to this one:
        [
            {'item_code': 'CULTIVO-0069', 'amount':'15.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0069', 'amount':'4.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0024', 'amount':'8.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0023', 'amount':'21.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0024', 'amount':'14.0', 'amount_uom': 'Pound'},
        ]

    Returns:
        unique item_code list: It returns a list of unique item codes, like the one below:
        ['CULTIVO-0069', 'CULTIVO-0024', 'CULTIVO-0023']

    Reference: https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order
    """
    unique_item_codes = []
    only_codes_list = []
    for available_material in available_material_list:
        only_codes_list.append(available_material['item_code'])

    unique_item_codes.extend(list(dict.fromkeys(only_codes_list)))

    return unique_item_codes


def sum_and_convert_available_material_list(available_material_list):
    """Function that finds all item_code values in an object list, and sums their amount value
    together, to return a list with only one unique object based on item code and the amounts of
    same item_code objects added to the unique one.

    Args:
        available_material_list: It expects a list similar to this one:
        [
            {'item_code': 'CULTIVO-0069', 'amount':'15.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0069', 'amount':'4.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0024', 'amount':'8.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0023', 'amount':'21.0', 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0024', 'amount':'14.0', 'amount_uom': 'Pound'},
        ]

    Returns:
        unique item code objects, amounts summed in a list, like this one:
        [
            {'item_code': 'CULTIVO-0069', 'amount': 19.0, 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0024', 'amount': 22.0, 'amount_uom': 'Pound'},
            {'item_code': 'CULTIVO-0023', 'amount': 21.0, 'amount_uom': 'Pound'}
        ]
    """
    new_list = []
    temp_list = []
    new_list.clear()
    for unique_item_code in make_list_of_unique_codes(available_material_list):
        temp_dict = {}
        # en: Subtotalizing variable where we will be adding each amount of each available material, after we convert to the first UOM found.
        # es-GT: Variable subtotalizadora en donde iremos sumando cada cantidad de cada material disponible posterior a una conversion a la primer UDM encontrada.
        same_material_amount_total = 0

        # en: Since we run the risk that similar available materials were added with different units of measure, we must select a UOM and then convert to it before adding amounts.
        # en: Each time a unique code is found, the variable will have a "not assigned" value, which will help determine whether to assign a variable for the first time.
        # es-GT: Como corremos el riesgo que materiales similares fueron agregados con diferentes unidades de medida, debemos seleccionar una UDM y luego convertir a esa antes de sumar cantidades.

        available_material_uom = "UOM for unique code not assigned yet"

        # Since we found a unique code, now we can search the available_material_list
        for available_material in available_material_list:
            if available_material["item_code"] == unique_item_code:
                # en: We get the current list index, because we want the entire value of that index!
                # es-GT: Obtenemos el indice actual de la lista, porque queremos obtener el valor completo de ese indice!
                index = available_material_list.index(available_material)

                # en: Since all the objects from available_material_list are the same, we obtain them each time and replace temp_dict
                # es-GT: Como todos los objetos del listado de materiales disponibles son lo mismo, los obtenemos cada vez y reemplazamos temp_dict
                temp_dict = available_material_list[index]

                # en: A problem arises: We might not have the same units. Therefore we will
                # es-GT: Como todos los objetos del listado de materiales disponibles son lo mismo, los obtenemos cada vez y reemplazamos temp_dict

                # First we decide to assign the value of the amount_uom
                if available_material_uom == "UOM for unique code not assigned yet":
                    # First time, we need to assign the amount_uom of this list item.
                    available_material_uom = available_material["amount_uom"]

                    # We also assign the value of the first time.
                    same_material_amount_total += float(
                        available_material["amount"])

                else:
                    # Value has probably been assigned on first found item, so we need to check if assigned unit matches this unit
                    if available_material_uom != available_material["amount_uom"]:
                        # CONVERSION NEEDED!
                        # we need to convert from: available_material["amount_uom"]  to  available_material_uom
                        # Ounce to Pound
                        # 32 ounces = 2 pounds

                        av_mat_amt_converted = float(
                            available_material['amount']) * float(conversion_factor[0]['value'])
                        # print('Available material amount has been converted to stock units in BOM for sales item')
                        # convert
                        # add
                        same_material_amount_total += float(
                            available_material["amount"])
                    elif available_material_uom == available_material["amount_uom"]:
                        # No conversion needed, just add the amount
                        # en: We add the available material object amount to our subtotaler variable, for later assignment to temp_dict.
                        # es-GT: Sumamos el monto del objeto de este material disponible a nuestra variable subtotalizadora, para posterior asignacion al diccionario temporal.
                        same_material_amount_total += float(
                            available_material["amount"])
                    else:
                        pass
            else:
                pass
        # Now that we have summed all of the same unique code, we can change the objects amount value
        temp_dict["amount"] = same_material_amount_total
        new_list.append(temp_dict)
    # Our list is now ready to use, with like item amounts added.
    return new_list
