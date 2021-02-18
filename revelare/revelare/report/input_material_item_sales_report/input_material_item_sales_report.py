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
    total_item_bom_sales,
    find_boms_and_conversions,
    find_conversion_factor,
    find_bom_items,
    find_boms
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
    get_year_number
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

    dates = get_periods(start_date, end_date, pandas_freq[period])
    if not dates:
        return data

    formatted_dates = get_date_ranges(
        start_date, end_date, pandas_freq[period])

    header_subtitle_row = {'0': 'Date Range'}
    header_subtitle_data = {idx + 1: f'{formatted_dates[idx][0]} - {formatted_dates[idx][1]}'
                            for idx, date in enumerate(formatted_dates)}
    header_subtitle_row.update(header_subtitle_data)
    data.append(header_subtitle_row)

    # Get the report data for each date range
    product_sum_columns = []
    for idx, (from_date, to_date) in enumerate(formatted_dates):
        date_filters = filters.copy()
        date_filters['from_date'] = from_date
        date_filters['to_date'] = to_date
        date_filters['column'] = idx

        new_data = get_report_data(date_filters)
        product_sum_columns += new_data

    # Empty Row
    empty_row = {}
    data.append([empty_row])

    # Get the item name list
    item_names = set()
    for column in product_sum_columns:
        if column:
            item_name = column.get('item_name', '')
            if len(item_name):
                item_names.add(item_name)

    # Arrange the item names and totals in html on the grid
    item_totals = {
        item_name: {
            'estimated': {
                idx + 1: 0 for idx in range(len(formatted_dates))
            },
            'sold': {
                idx + 1: 0 for idx in range(len(formatted_dates))
            },
            'difference': {
                idx + 1: 0 for idx in range(len(formatted_dates))
            }
        }
        for item_name in item_names
    }

    # Calculate the item sums per period
    for column in product_sum_columns:
        '''
        Items have a shape as shown below:
        item = {
             'item_name': 'Butter lettuce',
             'content': {
                 'estimated': 5,
                 'sold': 3,
                 'difference': 2
             },
             'column': 3
         }
       '''
        if column:
            name = column.get('item_name', '')
            content = column.get('content', {})
            column = int(column.get('column', 0))
            if content:
                estimated = content.get('estimated', 0)
                sold = content.get('sold', 0)
                difference = content.get('difference', 0)
                if column > 0:
                    item = item_totals[name]
                    item["estimated"][column] += estimated
                    item["sold"][column] += sold
                    item["difference"][column] += difference

    # Combine the data into rows
    for item_name in item_names:
        # Get the items
        item_data = item_totals[item_name]

        # Get the item totals
        estimated = item_data["estimated"]
        sold = item_data["sold"]
        difference = item_data["difference"]

        # Build the row dictionary

        # Estimated
        new_row = {'0': f'{item_name} Estimated'}
        new_row.update(estimated)
        data.append(new_row)

        # Sold
        new_row = {'0': f'{item_name} Sold'}
        new_row.update(sold)
        data.append(new_row)

        # Difference
        new_row = {'0': f'{item_name} Remaining'}
        new_row.update(difference)
        data.append(new_row)

        # Add an empty row between items
        data.append(empty_row)
    return data


def get_report_data(filters):
   # A dictionary that contain an item name, html content, a column number
    data = []

    # Get the estimated amount for all items in the date range
    estimated_materials_with_attributes = total_item_availability_estimate_attributes(
        filters)
    # frappe.msgprint(str(estimated_materials_with_attributes))
    # if estimated_materials_with_attributes:
    # Get the conversion factors for the bom items
    # from_uom = estimated_materials_with_attributes[0]['amount_uom']

    # Total the sales for all sales items
    # material_and_sales_items = find_boms_and_conversions(from_uom, filters)

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
            bom_item.pop('parent')

            # Append it to the list of sales items if not already included in the report
            if not boms[0]['item_name'] in included_items:
                included_items.add(boms[0]['item_name'])
                material_and_sales_items.append(bom_item)

    # Get the sales items abd codes in the date range
    sales_item_totals = total_item_bom_sales(filters)

    # Get the sales order quantities for items
    sales_item_codes = [item['item_code'] for item in sales_item_totals]

    for available_material in estimated_materials_with_attributes:
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

        # Initialize the total sold items in the target uom
        total_target_uom_sold = 0
        total_uom_sold = 0

        # Sum the sales order items and deduct from total available
        for ms_item in material_and_sales_items:
            if ms_item['item_code'] == available_material['name']:
                # Reset variables
                item_code = ''
                items_sold = 0
                target_uom_sold = 0

                # Total all units sold per sales item
                item_code = ms_item['sales_item_code']
                if item_code in sales_item_codes:
                    # sum the stock qty for all sales order items
                    order_qtys = [item['stock_qty'] for item in sales_item_totals
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

        item_name = available_material['item_name']

        # Convert amounts to styled HTML
        material_amount_html = html_wrap(
            str(material_amount), qty_plenty1_strong)

        total_uom_sold_html = html_wrap(
            str(total_uom_sold), qty_sold1_strong)

        # Compute the difference
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
