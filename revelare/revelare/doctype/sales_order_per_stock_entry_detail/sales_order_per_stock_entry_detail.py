# -*- coding: utf-8 -*-
# Copyright (c) 2020, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class SalesOrderperStockEntryDetail(Document):
    pass


def create_delivery_note(doc, event):
    """
    Crea nuevas Notas de Entrega, con datos de Sales Order per Stock Entry Detail
    esto al momento de validar, los docs creacion quedan en estado borrrador

    Args:
        doc (Class): Instancia del Doctype Sales Order per Stock Entry Detail
        event (str): nombre del evento ejecutado
    """

    # Validacione xtra para evento
    if event == 'on_submit':
        if len(doc.selected_items) > 0:  # si hay data que trabajar

            item_list = []  # lista con claves correctas
            for item in doc.selected_items:
                item_list.append({
                    'item_code': item.item_code,
                    'qty': item.stock_qty,
                    'stock_uom': item.stock_uom
                })

            # Creacion de nuevo documento
            doc = frappe.get_doc({
                'doctype': 'Delivery Note',
                'title': doc.title,
                'customer': doc.customer,
                'items': item_list
            }).save(ignore_permissions=True)

        return

    return

    # frappe.msgprint(f"{doc}, {event}")
