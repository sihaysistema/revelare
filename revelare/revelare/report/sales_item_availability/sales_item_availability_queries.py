# Copyright (c) 2020, Si Hay Sistema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, _dict, scrub

def total_item_availability_estimates(filters):
  """
  Returns a list of dictionaries that contain the sum of item availability
  estimate name, amounts and uom that fall within a date range
  """
  result = frappe.db.sql(
      f"""
      SELECT ei.item_code, SUM(ei.amount) as amount, ei.amount_uom
      FROM `tabItem Availability Estimate` as iae
      INNER JOIN `tabEstimated Item` as ei 
      ON iae.name = ei.parent
      WHERE iae.docstatus = 1 
      AND ei.docstatus = 1
      AND (iae.start_date AND iae.end_date 
           BETWEEN '{filters.from_date}' AND '{filters.to_date}')
      GROUP BY ei.item_code;
      """, as_dict=True
  )
  return result

def item_availability_estimates_range(filters):
    """Function that returns the name of the submitted Item Availability Estimates
    that fall between the dates selected in the filter.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
    """
    result = frappe.db.sql(
        f"""
        SELECT name FROM `tabItem Availability Estimate` 
        WHERE docstatus=1 AND start_date AND end_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'
        """, as_dict=True
    )
    return result


def periods_estimated_items(filters, parent):
    """Function that returns the code, amount, and amount uom of each estimated item
    belonging to a valid or submitted Item Availability Estimate

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        parent:  The parent of each one of these items, referring to Item Availability Estimate doctype
    Returns: A list of objects: [{'item_code': 'ITEMCODE-001', 'amount':'15.0', 'amount_uom': 'Pound'}]

    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, amount, amount_uom FROM `tabEstimated Item` 
        WHERE docstatus=1 AND parent='{parent}';""", as_dict=True
    )
    return result


def estimation_item_attributes(filters, estimation_item_code):
    """Function that returns the estimation UOM, estimation name and stock_uom for use 
    in the calculations and in the report.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        estimation_item_code:  The estimation item name, to find and obtain data from it.
    Returns: A list of dictionaries like this: 
    [{'name': 'CULTIVO-0069', 'estimation_name': 'Perejil', 'estimation_uom': 'Pound', 'stock_uom': 'Onza'}]
    """
    result = frappe.db.sql(
        f"""
        SELECT name, estimation_name, estimation_uom, stock_uom FROM `tabItem` WHERE name='{estimation_item_code}';
        """, as_dict=True
    )
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
        SELECT item_code, parent, stock_qty, stock_uom FROM `tabBOM Item` WHERE item_code='{estimation_item_code}';
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
        SELECT item, quantity, uom, item_name FROM `tabBOM` WHERE name='{bom}';
        """, as_dict=True
    )
    return result


def find_sales_items(filters, item_code):
    """Function that returns the item code and item name for sales items only.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        item_code: Item code for Item doctype
    """
    result = frappe.db.sql(
        f"""
        SELECT item_name, item_code FROM `tabItem` WHERE name='{item_code}' AND is_sales_item=1 AND include_in_estimations=1;
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
        SELECT from_uom, to_uom, value FROM `tabUOM Conversion Factor` WHERE from_uom='{from_uom}' AND to_uom='{to_uom}';
        """, as_dict=True
    )
    # Change the return to this variable to provide only the value of the conversion.
    if result:
        value_only = result[0]['value']
    return result


def find_sales_orders(filters):
    """Function that returns the item code and item name for sales items only.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        item_code: Item code for Item doctype
    """
    result = frappe.db.sql(
        f"""
        SELECT name FROM `tabSales Order` 
        WHERE docstatus=1 AND delivery_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'
        """, as_dict=True
    )
    return result


def find_sales_order_items(filters, parent):
    """Function that returns the code, amount, and amount uom of each estimated item
    belonging to a valid or submitted Item Availability Estimate

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        parent:  The parent of each one of these items, referring to Item Availability Estimate doctype
    Returns: A list of objects: [{'item_code': 'ITEMCODE-001', 'amount':'15.0', 'amount_uom': 'Pound'}]

    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, delivery_date, stock_qty, stock_uom FROM `tabSales Order Item` 
        WHERE docstatus=1 AND parent='{parent}';""", as_dict=True
    )
    return result
