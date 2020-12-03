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

from revelare.revelare.report.sales_item_availability.sales_item_availability_queries import (
    item_availability_estimates_range,
    periods_estimated_items,
    estimation_item_attributes,
    find_bom_items, find_boms,
    find_sales_items,
    find_conversion_factor,
    find_sales_orders,
    find_sales_order_items,
    total_item_availability_estimates,
    total_item_availability_estimate_attributes,
    total_sales_items
)

from revelare.revelare.report.sales_item_availability.sales_item_availability_utils import html_wrap


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
            "width": 110
        },
        {
            "label": _("D"),
            "fieldname": "D",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": _("E"),
            "fieldname": "E",
            "fieldtype": "Data",
            "width": 110
        },
        {
            "label": _("F"),
            "fieldname": "F",
            "fieldtype": "Data",
            "width": 130
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
    # Styles
    quantity_style_estimate_1 = """
      color: white;
      background-color: darkorange;
      display: block;
      text-align: center;
      vertical-align: middle;
      height: 100%;
      width: 100%;
    """

    quantity_style_plenty_1 = """
      color: black;
      background-color: orange;
      float: right;
      text-align: right;
      vertical-align: middle;
      height: 100%;
      width: 100%;
    """

    quantity_style_few_1 = """
      color: black;
      background-color: blue;
      float: right;
      text-align: right;
      vertical-align: text-top;
    """

    quantity_style_sold_1 = """
      color: black;
      background-color: #60A917;
      float: right;
      text-align: right;
      vertical-align: middle;
      height: 100%;
      width: 100%;
    """

    quantity_style_sold_dk_1 = """
      color: white;
      background-color: darkgreen;
      display: block;
      text-align: center;
      vertical-align: middle;
      height: 100%;
      width: 100%;
    """

    # Tag arrays
    strong = {"markup": "strong", "style": ""}
    strong_gray = {"markup": "strong", "style": "color: #686868"}

    qty_plenty1_strong = [
        {"markup": "span", "style": quantity_style_plenty_1}, strong]

    qty_estimate1_strong = [
        {"markup": "span", "style": quantity_style_estimate_1}, strong]

    qty_sold1_strong = [
        {"markup": "span", "style": quantity_style_sold_1}, strong]

    qty_sold1_dk_strong = [
        {"markup": "span", "style": quantity_style_sold_dk_1}, strong]

    item_link_open = "<a href='#Form/Item"
    item_link_style = "style='color: #1862AA;'"
    item_link_open_end = " target='_blank'>"
    item_link_close = "</a>"

    # ----- QUERY # 1 BEGIN -----
    # We now create a list of estimation item attributes
    # [{'name': 'CULTIVO-0069', 'estimation_name': 'Perejil', 'estimation_uom': 'Pound', 'stock_uom': 'Onza', 'amount':'15.0', 'amount_uom': 'Pound'}]
    # This list is already "filtered" and curated to include all the REQUESTED estimation item codes and attributes
    estimated_materials_with_attributes = total_item_availability_estimate_attributes(
        filters)

    # ----- QUERY # 2 BEGIN -----
    # Now we find the BOM names based on the names of material items in our item_attributes_list
    # [{'item_code': 'CULTIVO-0069', 'parent': 'BOM-7401168802186-001', 'stock_qty': 6.0, 'stock_uom': 'Onza'}]
    bom_items_list = []
    for material in estimated_materials_with_attributes:
        material_doctype_name = material['name']
        bom_items = find_bom_items(filters, material_doctype_name)
        bom_items_list.extend(bom_items)

    # ----- QUERY # 3 BEGIN -----
    # we get sales item code, quantity obtained, and uom obtained for each bom parent.
    material_and_sales_items = []
    included_items = set()
    for bom_item in bom_items_list:
        bom_name = bom_item['parent']
        boms = find_boms(filters, bom_name)

        # We rearrange the current dictionary, assigning values from returned keys in this list
        # to new keys in this object.
        if len(boms):
            bom_item['sales_item_code'] = boms[0]['item']
            bom_item['sales_item_qty'] = boms[0]['quantity']
            bom_item['sales_item_uom'] = boms[0]['uom']
            bom_item['sales_item_name'] = boms[0]['item_name']
            bom_item['conversion_factor'] = find_conversion_factor(
                estimated_materials_with_attributes[0]['amount_uom'], bom_item['stock_uom'])
            bom_item.pop("parent")

            # Append it to the list of sales items if not already included in the report
            if not boms[0]['item_name'] in included_items:
                included_items.add(boms[0]['item_name'])
                material_and_sales_items.append(bom_item)

    # ----- QUERY # 4 BEGIN -----
    # Sales Order query, return all sales order names that fit within
    # the dates in report filter
    matching_sales_order_items = total_sales_items(filters)

    # Sort material and sales items list by order of sales item code
    # Should print the code column in order like: -001, -002, -003, ...
    material_and_sales_items = sorted(
        material_and_sales_items, key=lambda x: x['sales_item_code'])

    # Get the sales order quantities for items
    sales_item_codes = [item['item_code']
                        for item in matching_sales_order_items]

    # ----- PROCESS DATA BEGIN -----
    # Iterate over the list of item estimates, including items from matching
    # sales orders and converting units to the target uom
    for available_material in estimated_materials_with_attributes:
        # en: We build and add the "grouping row"
        estimation_name = available_material['estimation_name']
        uom_name = available_material["amount_uom"]
        material_amount = available_material['amount']

        material_amount_html = html_wrap(
            str(material_amount), qty_plenty1_strong)
        row_header = {
            "A": estimation_name,
            "B": material_amount_html,
            "C": _(f"{uom_name}"),
            "D": _(f"Total {uom_name} Sold"),
            "E": "",
            "F": "",
            "G": ""
        }
        # We add bold style to the subtitles for the headers.
        col_a = html_wrap(_("Code"), [strong])
        col_b = html_wrap(_("Name"), [strong])
        col_c = html_wrap(_("Possible"), [strong])
        col_d = html_wrap(_("UOM"), [strong])
        col_e = html_wrap(_("Sold"), [strong])
        col_f = html_wrap(_("Available"), [strong])

        row_sub_header = {
            "A": col_a,
            "B": col_b,
            "C": col_c,
            "D": col_d,
            "E": col_e,
            "F": col_f,
            "G": ""
        }

        explanation_f = html_wrap(_("Possible - Total Sold"), [strong_gray])

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
        total_sold_column = "E"
        total_difference_column = "F"

        # Set the header and subheader values
        data.append(row_header)
        header_idx = len(data) - 1  # track the header index for updates later
        data.append(row_sub_header)
        data.append(row_explanation)

        # Initialize the total sold items in the target uom
        total_target_uom_sold = 0
        total_uom_sold = 0

        # Sum the sales order items and deduct from total available
        item_deductions = {}
        total_uom_sold = 0
        for ms_item in material_and_sales_items:
            if ms_item['item_code'] == available_material['name']:
                # Reset variables
                item_code = ""
                items_sold = 0
                target_uom_sold = 0

                # Total all units sold per sales item
                item_code = ms_item['sales_item_code']
                if item_code in sales_item_codes:
                    # sum the stock qty for all sales order items
                    order_qtys = [item['stock_qty'] for item in matching_sales_order_items
                                  if item['item_code'] == ms_item['sales_item_code']]
                    items_sold = math.floor(sum(order_qtys))
                else:
                    items_sold = 0

                # Convert the items sold an amt in the target UOM
                conversion = ms_item['conversion_factor'][0]['value']
                target_uom_sold = (
                    items_sold * ms_item['stock_qty']) / conversion

                # Add sold qty to item_deductions for later use
                total_uom_sold += target_uom_sold
                item_deductions[item_code] = target_uom_sold

        # We now cross-check, convert and structure our row output.
        for ms_item in material_and_sales_items:
            if ms_item['item_code'] == available_material['name']:
                if ms_item['stock_uom'] != available_material['amount_uom']:

                    # Reinitialize variables
                    item_code = ""

                    # find conversion factor , from unit is available material amount_uom - INSERT QUERY CALL HERE
                    conversion_factor = find_conversion_factor(
                        available_material['amount_uom'], ms_item['stock_uom'])
                    conversion_factor_reversed = find_conversion_factor(
                        ms_item['stock_uom'], available_material['amount_uom'])

                    # Warn the user if a conversion factor doesn't exist for
                    # the ms_item
                    if not conversion_factor:
                        frappe.msgprint("A UOM conversion factor is required to convert " + str(
                            available_material['amount_uom']) + " to " + str(ms_item['stock_uom']))
                    elif not conversion_factor_reversed:
                        frappe.msgprint("A UOM conversion factor is required to convert " + str(
                            ms_item['stock_uom']) + " to " + str(available_material['amount_uom']))
                    else:
                        # Convert available_material uom to ms_item uom, by multiplying available material amount by conversion factor found
                        av_mat_amt_converted = float(
                            available_material['amount']) * float(conversion_factor[0]['value'])

                        # Now, we divide the av_mat_amt_converted by the stock_qty to obtain possible quantity
                        # Adjusted quantity takes into account aldready sold uom counts
                        adjusted_amt = float(
                            available_material['amount']) - total_uom_sold
                        adjusted_quantity = math.floor((
                            adjusted_amt * float(conversion_factor[0]['value'])) / ms_item['stock_qty'])

                        # Possible quantity is the original converted material amount
                        # without deducting sales
                        possible_quantity = av_mat_amt_converted / \
                            ms_item['stock_qty']
                        possible_uom = _(ms_item['sales_item_uom'])

                        # Add HTML and CSS styles to certain fields
                        pos_qty = str(math.floor(possible_quantity))
                        quantity_sales_item_html = html_wrap(
                            pos_qty, qty_plenty1_strong)

                        # Build the item code url
                        item_code = ms_item['sales_item_code']
                        sales_item_route = f"{item_link_open}/{item_code}'" + \
                            item_link_style + item_link_open_end + \
                            str(ms_item['sales_item_code']
                                [-4:]) + item_link_close

                        # Calculate the amount sold
                        if ms_item['sales_item_code'] in sales_item_codes:
                            # sum the stock qty for all sales order items
                            order_qtys = [item['stock_qty'] for item in matching_sales_order_items
                                          if item['item_code'] == ms_item['sales_item_code']]
                            sold_quantity = math.floor(sum(order_qtys))
                        else:
                            sold_quantity = 0

                        # Add HTML to the sold quantity
                        quantity_sold_html = html_wrap(
                            str(sold_quantity), qty_sold1_strong)

                        # Calculate the difference of possible and sold items
                        available_quantity = int(
                            possible_quantity - sold_quantity)

                        available_quantity_html = html_wrap(
                            str(adjusted_quantity), qty_plenty1_strong)

                        # Populate the row
                        sales_item_row = {
                            "A": sales_item_route,
                            "B": str(ms_item['sales_item_name']),
                            "C": quantity_sales_item_html,
                            "D": _(possible_uom),
                            "E": quantity_sold_html,
                            "F": available_quantity_html,
                            "G": ""
                        }
                        data.append(sales_item_row)

                else:
                    print('Units are the same, no need for conversion.')
            else:
                pass

        # Add the target uom total to the header
        data[header_idx][total_sold_column] = html_wrap(
            str(total_uom_sold), qty_sold1_dk_strong)

        # Add the target uom total difference to the header
        total_uom_diff = str(material_amount - total_uom_sold)
        data[header_idx][total_difference_column] = html_wrap(
            total_uom_diff, qty_estimate1_strong)

        # We add an empty row after a set of products for easier reading.
        data.append(empty_row)

    # ----- PROCESS DATA END -----
    return data


def make_list_of_unique_codes(estimated_material_list):
    """Function that makes a list of unique item codes

    Args:
        estimated_material_list: It expects a list similar to this one:
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
    for available_material in estimated_material_list:
        only_codes_list.append(available_material['item_code'])

    unique_item_codes.extend(list(dict.fromkeys(only_codes_list)))

    return unique_item_codes


def sum_and_convert_estimated_material_list(estimated_material_list):
    """Function that finds all item_code values in an object list, and sums their amount value
    together, to return a list with only one unique object based on item code and the amounts of
    same item_code objects added to the unique one.

    Args:
        estimated_material_list: It expects a list similar to this one:
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
    for unique_item_code in make_list_of_unique_codes(estimated_material_list):
        temp_dict = {}
        # en: Subtotalizing variable where we will be adding each amount of each available material, after we convert to the first UOM found.
        # es-GT: Variable subtotalizadora en donde iremos sumando cada cantidad de cada material disponible posterior a una conversion a la primer UDM encontrada.
        same_material_amount_total = 0

        # en: Since we run the risk that similar available materials were added with different units of measure, we must select a UOM and then convert to it before adding amounts.
        # en: Each time a unique code is found, the variable will have a "not assigned" value, which will help determine whether to assign a variable for the first time.
        # es-GT: Como corremos el riesgo que materiales similares fueron agregados con diferentes unidades de medida, debemos seleccionar una UDM y luego convertir a esa antes de sumar cantidades.

        available_material_uom = "UOM for unique code not assigned yet"

        # Since we found a unique code, now we can search the estimated_material_list
        for available_material in estimated_material_list:
            if available_material["item_code"] == unique_item_code:
                # en: We get the current list index, because we want the entire value of that index!
                # es-GT: Obtenemos el indice actual de la lista, porque queremos obtener el valor completo de ese indice!
                index = estimated_material_list.index(available_material)

                # en: Since all the objects from estimated_material_list are the same, we obtain them each time and replace temp_dict
                # es-GT: Como todos los objetos del listado de materiales disponibles son lo mismo, los obtenemos cada vez y reemplazamos temp_dict
                temp_dict = estimated_material_list[index]

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
