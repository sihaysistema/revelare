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
    get_next_day,
    get_prior_day,
    get_week_number
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
    """
    Defines the report column structure
    """
    # Weekly, Monthly, Quarterly, Yearly"

    # Frequency mapping user filter selection to pandas.date_range freq values
    freq = {
        "Weekly": "W",
        "Monthly": "M",
        "Quarterly": "Q",
        "Yearly": "Y"
    }

    # We also build a column header mapping based on the periodicity filter
    period_header = {
        "Weekly": "Week",
        "Monthly": "Month",
        "Quarterly": "Quarter",
        "Yearly": "Year"
    }

    # Using the user's filters, we create an array of dates to build the
    # headers with
    period = filters["period"]
    start_date = filters["from_date"]
    end_date = filters["to_date"]
    label = period_header[period]

    dates = get_periods(start_date, end_date, freq[period])
    if not dates:
        return [{}]

    # Iterate through the dates and compile the column headers
    formatted_dates = [(start_date, dates[0])]
    next_start = get_next_day(dates[0])
    for date in dates[1:]:
        formatted_dates.append((next_start, date))
        next_start = get_next_day(date)
    frappe.msgprint(str(formatted_dates))

    report_columns = [
        {
            "label": f"{label} {idx + 1}",
            "fieldname": str(idx),
            "fieldtype": "Data",
            "width": 140
        } for idx, date in enumerate(dates))
    ]
    frappe.msgprint(str(report_columns))

    # The whole year
    yearly_columns = [
        {
            "label": _("A"),
            "fieldname": "A",
            "fieldtype": "Data",
            "width": 140
        },
        {
            "label": _("B"),
            "fieldname": "B",
            "fieldtype": "Data",
            "width": 140
        }
    ]

    # All 52-53 weeks in the year
    weekly_columns = [
        {}
    ]

    # All 4 quarters in the year
    quarterly_columns = [
        {}
    ]

    # All 12 months in the year
    monthly_columns = [
        {}
    ]

    return yearly_columns


def get_data(filters):
    """
    Accesses and processes the data for the report
    """
    # Empty Row
    empty_row = {}
    data = [empty_row]

    # Periodicity header
    period_header = {
        "A": "",
        "B": "Year 1",
    }
    data.append(period_header)

    # Get the estimated amount for all items in the date range
    estimated_materials_with_attributes = total_item_availability_estimate_attributes(
        filters)

    # if estimated_materials_with_attributes:
    # Get the conversion factors for the bom items
    # from_uom = estimated_materials_with_attributes[0]['amount_uom']

    # Total the sales for all sales items
    # material_and_sales_items = find_boms_and_conversions(from_uom, filters)

    bom_items_list=[]
    for material in estimated_materials_with_attributes:
        material_doctype_name=material['name']
        bom_items=find_bom_items(filters, material_doctype_name)
        bom_items_list.extend(bom_items)

    # ----- QUERY # 3 BEGIN -----
    # we get sales item code, quantity obtained, and uom obtained for each bom parent.
    material_and_sales_items=[]
    included_items=set()
    for bom_item in bom_items_list:
        bom_name=bom_item['parent']
        boms=find_boms(filters, bom_name)

        # We rearrange the current dictionary, assigning values from returned keys in this list
        # to new keys in this object.
        if len(boms):
            bom_item['sales_item_code']=boms[0]['item']
            bom_item['sales_item_qty']=boms[0]['quantity']
            bom_item['sales_item_uom']=boms[0]['uom']
            bom_item['sales_item_name']=boms[0]['item_name']
            bom_item['conversion_factor']=find_conversion_factor(
                estimated_materials_with_attributes[0]['amount_uom'], bom_item['stock_uom'])
            bom_item.pop("parent")

            # Append it to the list of sales items if not already included in the report
            if not boms[0]['item_name'] in included_items:
                included_items.add(boms[0]['item_name'])
                material_and_sales_items.append(bom_item)

    # Get the sales items abd codes in the date range
    sales_item_totals=total_item_bom_sales(filters)

    # Get the sales order quantities for items
    sales_item_codes=[item['item_code'] for item in sales_item_totals]

    for available_material in estimated_materials_with_attributes:
        estimation_name=available_material['estimation_name']
        uom_name=available_material["amount_uom"]
        material_amount=available_material['amount']

        material_amount_html=html_wrap(
            str(material_amount), qty_plenty1_strong)

        # Initialize the total sold items in the target uom
        total_target_uom_sold = 0
        total_uom_sold = 0

        # Sum the sales order items and deduct from total available
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

        total_uom_sold_html = html_wrap(
            str(total_uom_sold), qty_sold1_strong)

        # Compute the difference
        difference_html = html_wrap(
            str(material_amount - total_uom_sold), qty_estimate1_strong)

        # Display the data on the report
        estimated_row = {
            "A": html_wrap(f'{item_name} Estimated', label_style_item_gray1),
            "B": material_amount_html
        }
        data.append(estimated_row)

        sold_row = {
            "A": html_wrap(f'{item_name} Sold', label_style_item_gray1),
            "B": total_uom_sold_html,
        }
        data.append(sold_row)

        difference_row = {
            "A": html_wrap(f'{item_name} Available', label_style_item_gray1),
            "B": difference_html
        }
        data.append(difference_row)

        # Empty Row
        empty_row = {}
        data.append([empty_row])

    return data
