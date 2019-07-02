# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json


def crear_nota_entrega(documento):
    '''Funcion para crear nota de entrega'''

    delivery_note_tax = [{
        "charge_type": _('On net total'),
        "account_head": 'IVA - S',
        "cost_center": 'Main - S',
        "description": 'IVA @ 12.0',
        "included_in_print_rate": 1,
        "rate": 12
    }]

    delivery_note_items = [{
        "item_code": 'GAS-001',
        "item_name": 'Gasolina Regular',
        "rate": 24,
        "shs_dn_is_fuel": 1,
        "shs_dn_is_good": 0,
        "shs_dn_is_service": 0,
        "amount": 24,
        "qty": 1
    }]

    delivery_note = frappe.get_doc({"doctype": "Delivery Note",
                                    "title": documento['cliente'],
                                    "customer": documento['cliente'],
                                    "numero_vale_gaseco": documento['numero'],
                                    "name": documento['factura'],
                                    "company": "SHS",
                                    "items": delivery_note_items,
                                    "apply_discount_on": "Grand Total",
                                    # "taxes": delivery_note_tax,
                                    "docstatus": 1})
    DN_created = delivery_note.insert(ignore_permissions=True)

    return 'OK'