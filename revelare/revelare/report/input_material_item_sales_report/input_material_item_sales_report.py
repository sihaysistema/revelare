# Copyright (c) 2021, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from datetime import datetime
from erpnext.accounts.report.utils import convert  # value, from_, to, date
import json
from frappe.utils import nowdate, cstr, flt

import pandas as pd
import numpy as np
import math

from revelare.revelare.report.input_material_item_sales_report.input_material_item_sales_queries import (
    total_item_availability_estimate_attributes,
    item_availability_estimate_attributes,
    total_item_bom_sales,
    find_boms_and_conversions,
    find_conversion_factor,
    find_bom_items,
    find_boms,
    item_bom_sales
)

from revelare.revelare.report.input_material_item_sales_report.input_material_item_sales_utils import (
    html_wrap,
    weeks_in_year,
    weeks_between,
    quarter_dates,
    get_periods,
    get_date_ranges,
    get_next_day,
    get_prior_day,
    get_week_number,
    get_quarter_number,
    get_month_number,
    get_year_number,
    group_data,
    convert_uom,
    filter_dictionaries
)

from revelare.revelare.report.input_material_item_sales_report.report_markup_styles import (
    quantity_style_estimate_1,
    quantity_style_plenty_1,
    quantity_style_few_1,
    quantity_style_sold_1,
    quantity_style_sold_dk_1,
    strong,
    strong_gray,
    qty_plenty1_strong,
    qty_estimate1_strong,
    qty_sold1_strong,
    qty_sold1_dk_strong,
    item_link_open,
    item_link_style,
    item_link_open_end,
    item_link_close,
    label_style_item_gray1
)


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    '''
    Defines the report column structure
    '''
    # Weekly, Monthly, Quarterly, Yearly'
    no_data = [{}]

    # Frequency mapping user filter selection to pandas.date_range freq values
    pandas_freq = {
        'Weekly': 'W',
        'Monthly': 'M',
        'Quarterly': 'Q',
        'Yearly': 'Y'
    }

    # We also build a column header mapping based on the periodicity filter
    period_header = {
        'Weekly': 'Week',
        'Monthly': 'Month',
        'Quarterly': 'Quarter',
        'Yearly': 'Year'
    }

    period_format = {
        'Weekly': '%V',
        'Monthly': '%m',
        'Quarterly': '%m',
        'Yearly': '%Y'
    }

    period_fn = {
        'Weekly': get_week_number,
        'Monthly': get_month_number,
        'Quarterly': get_quarter_number,
        'Yearly': get_year_number
    }

    # Using the user's filters, we create an array of dates to build the
    # headers with
    period = filters.get('period')
    start_date = filters.get('from_date')
    end_date = filters.get('to_date')
    if not period or not start_date or not end_date:
        return no_data

    date_ranges = get_date_ranges(start_date, end_date, pandas_freq[period])
    if not date_ranges:
        return no_data

    label = period_header[period]
    period_num_fn = period_fn[period]
    period_num = period_num_fn(start_date)

    first_column = [
        {
            'label': 'Type',
            'fieldname': '0',
            'fieldtype': 'Data',
            'height': 100,
            'width': 200
        }
    ]

    report_columns = [
        {
            'label': f'{label} {period_num + idx}',
            'fieldname': str(idx + 1),
            'fieldtype': 'Data',
            'height': 100,
            'width': 200
        } for idx, date in enumerate(date_ranges)
    ]

    return first_column + report_columns


def get_data(filters):
    '''
    Accesses and processes the data for the report
    '''
    # Empty Row
    empty_row = {}
    data = []

    # Using the user's filters, we create an array of dates to build the
    # headers with
    pandas_freq = {
        'Weekly': 'W',
        'Monthly': 'M',
        'Quarterly': 'Q',
        'Yearly': 'Y'
    }

    # We also build a column header mapping based on the periodicity filter
    period_header = {
        'Weekly': 'Week',
        'Monthly': 'Month',
        'Quarterly': 'Quarter',
        'Yearly': 'Year'
    }

    period_format = {
        'Weekly': '%V',
        'Monthly': '%m',
        'Quarterly': '%m',
        'Yearly': '%Y'
    }

    period_fn = {
        'Weekly': get_week_number,
        'Monthly': get_month_number,
        'Quarterly': get_quarter_number,
        'Yearly': get_year_number
    }

    period = filters.get('period')
    start_date = filters.get('from_date')
    end_date = filters.get('to_date')
    if not period or not start_date or not end_date:
        return data

    formatted_dates = get_date_ranges(
        start_date, end_date, pandas_freq[period])

    if not formatted_dates:
        return data

    header_subtitle_row = {'0': 'Date Range'}
    header_subtitle_data = {idx + 1: f'{formatted_dates[idx][0]} - {formatted_dates[idx][1]}'
                            for idx, date in enumerate(formatted_dates)}
    header_subtitle_row.update(header_subtitle_data)
    data.append(header_subtitle_row)

    # Get the estimated amount for all items in the date range
    estimated_materials = item_availability_estimate_attributes(filters)
    frappe.msgprint(str(estimated_materials))

    # Get the sales data for the range, individually listed by date
    sales_items = get_sales_data(filters)
    frappe.msgprint(str(sales_items))

    # Get sales unit conversion data
    bom_data = get_bom_data(filters, estimated_materials)
    conversions = {item['sales_item_code']: item for item in bom_data}
    frappe.msgprint(str(conversions))

    # Divide the data into date range buckets
    estimated_date_props = ('start_date', 'end_date')
    estimated_ranges = group_data(dates=formatted_dates,
                                  data=estimated_materials,
                                  date_props=estimated_date_props)
    # frappe.msgprint(str(estimated_ranges))

    sold_date_props = ('delivery_date', 'delivery_date')
    sold_ranges = group_data(dates=formatted_dates,
                             data=sales_items,
                             date_props=sold_date_props)

    # Empty Row
    empty_row = {}
    data.append([empty_row])

    # Get the item name list
    # Ensure it is unique by using sets
    # This is used to display the estimation items on the far left column
    item_names = set()
    for date_range, estimate_array in estimated_ranges.items():
        if estimate_array:
            for estimate in estimate_array:
                item_name = estimate.get('estimation_name', '')
                if len(item_name):
                    item_names.add(item_name)
    return data


def get_report_data(filters, material_items):
   # A dictionary that contain an item name, html content, a column number
    data = []

    # Track sales items that may not have a corresponding estimate
    estimated_sales_items = set()

    # Get the estimated amount for all items in the date range
    estimated_materials = total_item_availability_estimate_attributes(filters)

    # Get sales unit conversion data
    material_and_sales_items = get_bom_data(filters, estimated_materials)

    # Get the sales items in the date range
    sales_item_totals = total_item_bom_sales(filters)

    # List the codes for sales order summation later
    sales_item_codes = [item['item_code'] for item in sales_item_totals]

    for available_material in estimated_materials:
        material_data = {
            'item_name': '',
            'content': {
                'estimated': 0,
                'sold': 0,
                'difference': 0
            },
            'column': filters['column']
        }

        estimation_name = available_material['estimation_name']
        uom_name = available_material['amount_uom']
        material_amount = available_material['amount']

        # Calculate the total items sales in this period
        total_uom_sold = sum_sales_data(
            material_and_sales_items, available_material, sales_item_codes)

        item_name = available_material['item_name']

        # Convert amounts to styled HTML
        material_amount_html = html_wrap(
            str(material_amount), qty_plenty1_strong)

        total_uom_sold_html = html_wrap(
            str(total_uom_sold), qty_sold1_strong)

        difference_html = html_wrap(
            str(material_amount - total_uom_sold), qty_estimate1_strong)

        # Display the data on the report
        material_data['item_name'] = item_name

        estimated_row = {
            'label': html_wrap(f'{item_name} Estimated', label_style_item_gray1),
            'amount': material_amount,
            'type': 'estimated'
        }
        # material_data['content']['estimated'] = estimated_row
        material_data['content']['estimated'] = material_amount

        sold_row = {
            'label': html_wrap(f'{item_name} Sold', label_style_item_gray1),
            'amount': total_uom_sold,
            'type': 'sold'
        }
        # material_data['content']['sold'] = sold_row
        material_data['content']['sold'] = total_uom_sold

        difference_row = {
            'label': html_wrap(f'{item_name} Available', label_style_item_gray1),
            'amount': material_amount - total_uom_sold,
            'type': 'difference'
        }
        # material_data['content']['difference'] = difference_row
        material_data['content']['difference'] = material_amount - \
            total_uom_sold

        data.append(material_data)

    return data


def get_sales_data(filters):
    """Returns the sale data for the range in filters"""
    sales_data = item_bom_sales(filters)
    return sales_data


def get_bom_data(filters, estimated_materials):
    """Get the bom information that is necessary to convert sales item uoms"""

    # Obtain conversion units for sales items from BOM items
    # bom_items contains the stock_uom, which is the number of units of
    # the parent item, for instance, 12oz or 5lbs
    bom_items_list = []
    for material in estimated_materials:
        material_doctype_name = material['name']
        bom_items = find_bom_items(filters, material_doctype_name)
        bom_items_list.extend(bom_items)

    # Get the sales order item names and conversion factors from the BOMs
    # We use this later to total the sales in the target uom
    material_and_sales_items = []
    included_items = set()
    for bom_item in bom_items_list:
        bom_name = bom_item['parent']
        boms = find_boms(filters, bom_name)

        if len(boms):
            bom_item['sales_item_code'] = boms[0]['item']
            bom_item['conversion_factor'] = find_conversion_factor(
                estimated_materials[0]['amount_uom'], bom_item['stock_uom'])
            bom_item.pop('parent')

            # Append it to the list of sales items if not already included in the report
            if not boms[0]['item_name'] in included_items:
                included_items.add(boms[0]['item_name'])
                material_and_sales_items.append(bom_item)

    return material_and_sales_items


def sum_sales_data(sales_data, material_data, sales_item_codes):
    """Sum the totals for sales items in the range"""
    # Initialize the total sold items in the target uom
    total_target_uom_sold = 0
    total_uom_sold = 0

    # Sum the sales order items and deduct from total available
    for ms_item in sales_data:
        if ms_item['item_code'] == material_data['name']:
            frappe.msgprint(str(ms_item))
            # Reset variables
            item_code = ''
            items_sold = 0
            target_uom_sold = 0

            # Total all units sold per sales item
            item_code = ms_item['sales_item_code']
            if item_code in sales_item_codes:
                # sum the stock qty for all sales order items
                order_qtys = [item['stock_qty'] for item in sl
                              if item['item_code'] == ms_item['sales_item_code']]
                frappe.msgprint(str(order_qtys))
                items_sold = math.floor(sum(order_qtys))
            else:
                items_sold = 0

            # Convert the items sold an amt in the target UOM
            conversion = ms_item['conversion_factor'][0]['value']
            target_uom_sold = (
                items_sold * ms_item['stock_qty']) / conversion

            # Add sold qty to item_deductions for later use
            total_uom_sold += target_uom_sold
    frappe.msgprint(str(total_uom_sold))
    return total_uom_sold
