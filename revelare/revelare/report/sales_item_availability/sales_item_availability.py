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
            "width": 120
        },
        {
            "label": _("Quantity"),
            "fieldname": "quantity",
            "fieldtype": "Float",
            "width": 120
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            "hidden": 0,
            "width": 120
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 120
        },
        {
            "label": _("Sales Item"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Possible Quantity"),
            "fieldname": "possible_quantity",
            "fieldtype": "Int",
            "width": 120
        }
    ]

    return columns

def get_data(filters):
    empty_row = {}
    data = [empty_row]

    return data


'''
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