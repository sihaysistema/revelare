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
    item_bom_sales,
    find_boms_by_item_code,
    find_bom_items_by_item_code
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
    filter_dictionaries_first,
    filter_dictionaries,
    shorten_column,
    reverse_dictionary
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

# Constants
MAX_CHART_NAME_LEN = 16


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    chart = get_chart(data, columns[1:], filters)
    return columns, data, None, chart


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

    # Get the period numbers for each date range
    period_num = period_num_fn(start_date)
    multi_year_range = False
    yearly_period_fn = period_fn["Yearly"]

    first_year = yearly_period_fn(date_ranges[0][0])
    last_year = yearly_period_fn(date_ranges[-1][0])
    if first_year != last_year:
        multi_year_range = True

    # Create a dictionary of header labels based on periodicty
    period_headers = {}
    header_text = ''
    header_column = 1  # The first column is unique and is not populated iteratively
    separator_char = '/'
    final_weeks = [52, 53]
    for start, end in date_ranges:
        period_name = period_header[period]
        period_number = period_fn[period](end)

        # Handle the multi-year Yearly periodicity differently
        # to avoid duplicating 'Year' in the label content
        if multi_year_range and period != 'Yearly':
            # Determine if there are 2+ years in this date range tuple
            # If it has 2+ years then we'll separate them with a char
            start_year = yearly_period_fn(start)
            end_year = yearly_period_fn(end)
            if start_year != end_year and period_number not in final_weeks:
                # Two or more years in this range slice
                # e.g., 2020/2021
                year = f'{start_year}{separator_char}{end_year}'
            else:
                # Only one year in the range
                year = start_year
            header_text = f'Year {year}, {period_name} {period_number}'
        else:
            header_text = f'{period_name} {period_number}'

        # Assign the period header text to the appropriate header slot
        # Increment by columns in the header
        period_headers[header_column] = header_text
        header_column += 1

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
            'label': period_headers[idx + 1],
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

    # Get the sales data for the range, individually listed by date
    sales_items = get_sales_data(filters)

    # Handle item selection in filters
    selected_item = filters.get('item', '')
    if selected_item:
        # Create dictionaries mapping sales items to estimated names
        # and vice versa
        sales_to_estimated_map = get_bom_items_by_code(filters, sales_items)
        estimated_to_sales_map = reverse_dictionary(sales_to_estimated_map)

        # Identify if the item code is a sales item or an estimated item
        item_is_sales = selected_item in sales_to_estimated_map
        item_is_estimated = selected_item in estimated_to_sales_map

        # If a sales item is selected, the sales items are filtered by
        # the item code, but no estimation items are filtered.
        if item_is_sales:
            estimated_item = sales_to_estimated_map.get(selected_item, '')
            sales_item = selected_item
            sales_items = filter_dictionaries(
                sales_items, {'item_code': sales_item})
            estimated_materials = filter_dictionaries(
                estimated_materials, {'name': estimated_item})

        # If an estimation item is selected, then the estimation data is
        # filtered and all sales items linked to that item in BOms are included
        elif item_is_estimated:
            estimated_item = selected_item
            estimated_materials = filter_dictionaries(
                estimated_materials, {'name': estimated_item})

            # Add the filtered items by sales item codes mapped from estimated_item
            sales_item_list = estimated_to_sales_map.get(selected_item, '')
            sales_items_updated = []
            for item in sales_item_list:
                items = filter_dictionaries(sales_items, {'item_code': item})
                sales_items_updated += items
            sales_items = sales_items_updated

        else:
            sales_items = []
            estimated_materials = []

    # Get sales unit conversion data
    bom_data = {}
    if sales_items:
        bom_data_array = get_bom_item_data(filters, sales_items)
    elif estimated_materials:
        bom_data_array = get_bom_data(filters, estimated_materials)
    else:
        bom_data_array = []

    conversions = {item['sales_item_code']: item for item in bom_data_array}

    # Divide the data into date range buckets
    estimated_date_props = ('start_date', 'end_date')
    estimated_ranges = group_data(dates=formatted_dates,
                                  data=estimated_materials,
                                  date_props=estimated_date_props)

    sold_date_props = ('delivery_date', 'delivery_date')
    sold_ranges = group_data(dates=formatted_dates,
                             data=sales_items,
                             date_props=sold_date_props)

    # Get the item name list
    # Ensure it is unique by using sets
    # This is used to display the estimation items on the far left column
    # We go to lengths to make this available even when there are only sales
    item_names = set()
    item_codes = set()
    item_pairs = set()
    if sold_ranges:
        # If sold_ranges exists and estimated_ranges doesn't
        for bom_item in bom_data_array:
            item_name = bom_item.get('item_name', '')
            item_code = bom_item.get('item_code', '')
            if len(item_name):
                item_names.add(item_name)
            if len(item_code):
                item_codes.add(item_code)
            item_pairs.add((item_name, item_code))
    elif estimated_ranges:
        # if estimated_ranges exists
        for date_range, estimate_array in estimated_ranges.items():
            if estimate_array:
                for estimate in estimate_array:
                    item_name = estimate.get('estimation_name', '')
                    item_code = estimate.get('name', '')
                    if len(item_name):
                        item_names.add(item_name)
                    if len(item_code):
                        item_codes.add(item_code)
                    item_pairs.add((item_name, item_code))

    # Arrange the item names and totals to later iteratively add them
    # To their respective rows for each items
    item_totals = {
        item_code: {
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
        for item_code in item_codes
    }

    # Sum the sales data
    # convert_uom
    column = 1
    for date_range in estimated_ranges.keys():
        # Estimation items
        estimated_items = estimated_ranges.get(date_range, [])
        if estimated_items:
            for item in estimated_items:
                # Get the estimated quantity
                quantity = item.get('amount', 0)

                # Add it to the totals for that item in item_totals
                #item_name = item.get('item_name', '')
                item_name = item.get('name', '')
                if len(item_name):
                    estimated_total = item_totals[item_name]['estimated']
                    new_qty = estimated_total[column] + float(quantity)
                    estimated_total[column] = round(new_qty, 2)

        # Sales items
        sold_items = sold_ranges.get(date_range, [])

        if sold_items:
            for item in sold_items:
                # Get the sold quantity
                quantity = item.get('stock_qty', 0)
                # Get the sales item code for association with boms_data
                # to perform the conversion to the target uom
                item_code = item.get('item_code', '')
                conversion_item = conversions.get(item_code, {})
                conversion_data = conversion_item.get(
                    'conversion_factor', [])

                if conversion_data:
                    conversion_factor_data = conversion_data[0]
                    conversion_factor = int(
                        conversion_factor_data.get('divide_by', 1))
                    conversion_stock_qty = conversion_item.get('stock_qty', 0)
                    converted_qty = convert_uom(total_sold=quantity,
                                                stock_qty=conversion_stock_qty,
                                                conversion_factor=conversion_factor)

                    # Add it to the totals for that item in item_totals,
                    # not the sales item code
                    bom_data = filter_dictionaries_first(
                        bom_data_array, {'sales_item_code': item_code})
                    if bom_data:
                        parent_item_code = bom_data.get('item_code', '')
                        if len(parent_item_code):
                            sold_total = item_totals[parent_item_code]['sold']
                            new_qty = sold_total[column] + float(converted_qty)
                            sold_total[column] = round(new_qty, 2)

        # Continue to the next column of data
        column += 1

    # Calculate the remaining quantity
    for item_code, item_data in item_totals.items():
        estimated = item_data.get('estimated', [])
        sold = item_data.get('sold', [])
        difference = item_data.get('difference', [])

        # Update the difference in each column
        for idx in range(1, len(difference.keys()) + 1):
            difference[idx] = round(estimated[idx] - sold[idx], 2)

    # Construct rows for each item with item totals across the columns
    # Start with an empty Row
    empty_row = {}
    data.append(empty_row)
    # Build the remainder of the row data using the item totals
    for item_name, item_code in item_pairs:  # Get the items
        item_data = item_totals.get(item_code, {})
        item_uom = ''
        if estimated_materials:
            item_metadata = filter_dictionaries_first(
                estimated_materials, {'name': item_code})
            item_uom = item_metadata.get('estimation_uom', '')
        elif sales_items:
            item_metadata = filter_dictionaries_first(
                bom_data_array, {'item_code': item_code})
            item_uom = item_metadata.get('amount_uom', '')

        # Get the item totals
        estimated = item_data.get('estimated', {})
        sold = item_data.get('sold', {})
        difference = item_data.get('difference', {})

        # Build the row dictionary

        # Estimated
        new_row = {'0': f'{item_name} Estimated ({item_uom})'}
        new_row.update(estimated)
        data.append(new_row)

        # Sold
        new_row = {'0': f'{item_name} Sold ({item_uom})'}
        new_row.update(sold)
        data.append(new_row)

        # Difference
        new_row = {'0': f'{item_name} Remaining ({item_uom})'}
        new_row.update(difference)
        data.append(new_row)

        # Add an empty row between items
        data.append(empty_row)

    return data


def get_chart(data, columns, filters):
    labels = [column["label"] for column in columns]
    chart_data = [item for item in data[1:] if len(item) > 0]

    # Determine the chart data by sales category
    sales_category = filters.get('sales_category', '')

    # Filter the data if the user selects Actual or Estimated data filters
    if sales_category == 'Actual':
        # Show only sales data
        filtered_data = []
        for item in chart_data:
            label = item['0']
            if label.find('Sold') != -1:
                filtered_data.append(item)
        chart_data = filtered_data
    elif sales_category == 'Estimated':
        # Show only item estimate data
        filtered_data = []
        for item in chart_data:
            label = item['0']
            if label.find('Estimated') != -1:
                filtered_data.append(item)
        chart_data = filtered_data
    elif sales_category == 'Remaining':
        # Show only item estimate data
        filtered_data = []
        for item in chart_data:
            label = item['0']
            if label.find('Remaining') != -1:
                filtered_data.append(item)
        chart_data = filtered_data

    # Build the data sets
    datasets = [
        {
            'name': shorten_column(item['0'], " (Pound)", MAX_CHART_NAME_LEN),
            'values': [float(val) for key, val in item.items() if int(key) > 0]
        } for item in chart_data
    ]

    chart = {
        'data': {
            'labels': labels,
            'datasets': datasets
        },
        'isNavigable': 1,
        'type': 'line'
    }

    return chart


def get_sales_data(filters):
    '''Returns the sale data for the range in filters'''
    sales_data = item_bom_sales(filters)
    return sales_data


def get_bom_items_list(filters, sales_items):
    """Generate a list of sales items with bom data, including conversions"""
    # Obtain the boms for the sales items
    boms_list = []
    for sales_item in sales_items:
        sales_item_code = sales_item['item_code']
        boms = find_boms_by_item_code(filters, sales_item_code)
        if boms:  # boms are an array
            boms_list += boms

    # Get the estimation BOM name for the sales items by linking through
    # to them using the name property on the bom, which should match the
    # parent column on the `tabBom Item` table
    bom_items_list = []
    for bom in boms_list:
        bom_name = bom['name']
        bom_items = find_bom_items_by_item_code(filters, bom_name)
        if bom_items:  # bom_items is an array
            bom_items_list += bom_items
        else:
            # Warn the user if an item availability estimate doesn't exist
            # for this item
            item_name = bom.get('item')
            frappe.msgprint(
                f'Unable to include sales data for {item_name}.' +
                f' Please add at least one item availability estimate for' +
                f' {item_name} in order for it to be included in this report')

    return boms_list, bom_items_list


def get_bom_item_data(filters, sales_items):
    """Get all bom information, necessary to convert sales item uoms, but
    starting from the sales items rather than from the estimation items. This
    is necessary to prevent situations where there are no estimation items
    for a range or none selected in the filters"""
    material_and_sales_items = []
    boms_list, bom_items_list = get_bom_items_list(filters, sales_items)

    # Add columns from the bom table to the bom items data
    # Append the bom conversion data to the existing bom data
    included_items = set()
    for bom_item in bom_items_list:
        parent = bom_item.get('parent', '')
        matching_bom = filter_dictionaries_first(
            boms_list, {'name': parent})
        sales_item_code = matching_bom.get('item', '')
        bom_item['sales_item_code'] = sales_item_code
        if sales_item_code and not sales_item_code in included_items:
            included_items.add(sales_item_code)
            bom_item['conversion_factor'] = find_conversion_factor(
                bom_item['amount_uom'], bom_item['stock_uom'])
            material_and_sales_items.append(bom_item)
  
    return material_and_sales_items


def get_unique_bom_item_data(filters, sales_items):
    """Gets the bom information, necessary to convert sales item uoms, but
    starting from the sales items rather than from the estimation items. This
    is necessary to prevent situations where there are no estimation items
    for a range or none selected in the filters"""
    material_and_sales_items = []
    boms_list, bom_items_list = get_bom_items_list(filters, sales_items)

    # Add columns from the bom table to the bom items data
    included_items = set()
    for bom_item in bom_items_list:
        # Append it to the list of sales items if not already
        # included in the report
        if not bom_item['item_name'] in included_items:
            included_items.add(bom_item['item_name'])

            parent = bom_item.get('parent', '')
            matching_bom = filter_dictionaries_first(
                boms_list, {'name': parent})
            bom_item['sales_item_code'] = matching_bom['item']
            bom_item['conversion_factor'] = find_conversion_factor(
                bom_item['amount_uom'], bom_item['stock_uom'])

            material_and_sales_items.append(bom_item)

    return material_and_sales_items


def get_bom_items_by_code(filters, sales_items):
    """Returns a dictionary with the estimated item for each sales item"""
    bom_map = {}
    boms_list, bom_items_list = get_bom_items_list(filters, sales_items)

    # Add columns from the bom table to the bom items data
    for bom_item in bom_items_list:
        # Append it to the list of sales items if not already
        # included in the report
        parent = bom_item.get('parent', '')
        matching_bom = filter_dictionaries_first(
            boms_list, {'name': parent})
        bom_item['sales_item_code'] = matching_bom['item']
        bom_map[bom_item['sales_item_code']] = bom_item['item_code']

    return bom_map


def get_bom_data(filters, estimated_materials):
    '''Get the bom information that is necessary to convert sales item uoms'''

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
            bom_item['conversion_backwards'] = find_conversion_factor(
                bom_item['stock_uom'], estimated_materials[0]['amount_uom'])
            bom_item.pop('parent')

            # Append it to the list of sales items if not already included in the report
            if not boms[0]['item_name'] in included_items:
                included_items.add(boms[0]['item_name'])
                material_and_sales_items.append(bom_item)

    return material_and_sales_items
