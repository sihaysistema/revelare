# Copyright (c) 2021, Si Hay Sistema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict, scrub


def total_item_availability_estimate_attributes(filters):
    """
    Returns a list of dictionaries that contain the item availability estimate
    name, estimation name, estimation uom, stock uom, total amount, amount uom
    """
    result = frappe.db.sql(
        f"""
        SELECT name, estimation_name, estimation_uom, stock_uom,
                    estimate.item_name, estimate.amount, estimate.amount_uom
        FROM `tabItem`
        INNER JOIN
          (SELECT ei.item_code, ei.item_name, SUM(ei.amount) as amount, ei.amount_uom
          FROM `tabItem Availability Estimate` as iae
          INNER JOIN `tabEstimated Item` as ei
          ON iae.name = ei.parent
          WHERE iae.docstatus = 1
          AND ei.docstatus = 1
          AND (iae.start_date AND iae.end_date
                BETWEEN '{filters.from_date}' AND '{filters.to_date}')
          GROUP BY ei.item_code) as estimate
        WHERE name=estimate.item_code;
        """, as_dict=True
    )
    return result


def total_sales_items(filters):
    """
    Returns the sales item totals for each sales item code
    """
    result = frappe.db.sql(
        f"""
        SELECT soi.item_name, soi.item_code, soi.delivery_date,
          SUM(soi.stock_qty) as total_stock_qty, COUNT(soi.item_code) total_orders, soi.stock_uom
        FROM `tabSales Order Item` as soi
        WHERE soi.parent IN
          (SELECT so.name FROM `tabSales Order` AS so
          WHERE docstatus=1
          AND delivery_date BETWEEN '{filters.from_date}' AND '{filters.to_date}')
        GROUP BY soi.item_code;
        """, as_dict=True
    )
    return result


def total_item_bom_sales(filters):
    """
    Returns the sales item totals for sales items with a bom docstatus of 1
    """
    result = frappe.db.sql(
        f"""
        SELECT soi.item_code, soi.item_name, soi.parent,  
          SUM(soi.stock_qty) as stock_qty, soi.stock_uom 
        FROM `tabSales Order Item` as soi
        INNER JOIN
          (SELECT so.name FROM `tabSales Order` AS so 
          WHERE so.docstatus=1 
          AND (delivery_date BETWEEN '{filters.from_date}' AND '{filters.to_date}')) AS soitems
        ON soitems.name=soi.parent
        INNER JOIN
          (SELECT DISTINCT item 
          FROM `tabBOM`
          WHERE docstatus=1) AS tb
        ON soi.item_code=tb.item
        GROUP BY tb.item;
        """, as_dict=True
    )
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
    result = frappe.db.sql(
        f"""
        SELECT from_uom, to_uom, value FROM `tabUOM Conversion Factor` 
        WHERE from_uom='{from_uom}' AND to_uom='{to_uom}';
        """, as_dict=True
    )
    # Change the return to this variable to provide only the value of the conversion.
    return result


def find_bom_items(filters, estimation_item_code):
    """Function that returns the item_code, parent, stock_qty, stock_uom used in BOM Item, to prepare conversion for use 
    in the calculations, and to find BOM names that will help find Sales Items.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        estimation_item_code:  The estimation item name, to find the BOM Items where it is listed, so that we may find the BOMs being used.
    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, parent, stock_qty, stock_uom 
        FROM `tabBOM Item` 
        WHERE item_code='{estimation_item_code}'
        AND docstatus=1;
        """, as_dict=True
    )
    return result


def find_boms(filters, bom):
    """Function that returns the item, quantity and uom to obtain from this bom, such that we may go find Sales Items.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        bom:  The bom name or ID
    """
    result = frappe.db.sql(
        f"""
        SELECT item, quantity, uom, item_name 
        FROM `tabBOM` 
        WHERE name='{bom}'
        AND docstatus=1;
        """, as_dict=True
    )
    return result


def find_boms_and_items(item_code, filters):
    result = frappe.db.sql(
        f"""
        SELECT tbi.item_code, tbi.parent, tbi.stock_qty, tbi.stock_uom,
          tb.item, tb.quantity, tb.uom, tb.item_name  
        FROM `tabBOM Item` as tbi
        INNER JOIN `tabBOM` as tb 
        ON tbi.parent = tb.name
        WHERE item_code={item_code}
        AND tbi.docstatus=1 and tb.docstatus=1;
        """, as_dict=True
    )
    return result


def find_boms_and_conversions(from_uom, filters):
    """
    Find the boms and the converstion factor from from_uom to the stock_uom
    """
    result = frappe.db.sql(
        f"""
        SELECT tbi.item_code, tbi.parent, tbi.stock_qty, tbi.stock_uom,
          tb.item as sales_item_code, tb.quantity as sales_item_qty, 
          tb.uom as sales_item_uom, tb.item_name as sales_item_name,
          cf.from_uom, cf.to_uom, cf.value as conversion_factor
        FROM `tabBOM Item` AS tbi
        INNER JOIN `tabBOM` AS tb 
        ON tbi.parent = tb.name
        INNER JOIN `tabUOM Conversion Factor` AS cf
        ON cf.from_uom='Pound'
        WHERE cf.to_uom=tbi.stock_uom
        AND tbi.docstatus=1 and tb.docstatus=1;
        """, as_dict=True
    )
    return result
