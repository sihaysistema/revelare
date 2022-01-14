# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
from datetime import datetime, timedelta

import frappe
import numpy as np
from frappe import _, _dict, scrub
from frappe.utils import cstr, flt, nowdate


def get_categories():
    """
    Función: Obtiene todas las categorias del árbol de los componentes de flujo de caja directo

    Returns:
        Lista de diccionarios: Lista de diccionarios, que obtiene el orden de las categorias
        delimitado en el árbol de flujo de caja directo
    """
    return frappe.db.sql("""
        SELECT name, parent_direct_cash_flow_component, cash_effect,is_group
        FROM `tabDirect Cash Flow Component`
        ORDER BY lft
        """, as_dict=True)


def get_list_journal_entries(from_date, to_date):
    """
    Función: Obtiene el listado de polizas de diario que contengan al menos una
    cuenta de tipo efectivo o banco.

    Args:
        from_date ([type]): [description]
        to_date ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, con nombre y fecha de la poliza.
    """
    list_journal_entries = frappe.db.sql(f'''
        SELECT JE.name AS `url_name`, JEC.account AS `lb_name`, JE.docstatus, JE.posting_date,
        JEC.inflow_component, JEC.outflow_component, JEC.debit, JEC.credit, JEC.account_type,
        CASE
        WHEN JEC.debit > 0 THEN JEC.debit
        WHEN JEC.credit > 0 THEN JEC.credit
        END AS amount
        FROM `tabJournal Entry` AS JE
        INNER JOIN `tabJournal Entry Account` AS JEC ON JE.name = JEC.parent
        WHERE JE.docstatus = 1
        AND (JE.posting_date BETWEEN '{from_date}' AND '{to_date}')
        AND (JEC.account_type = 'Bank' OR JEC.account_type = 'Cash')
    ''', as_dict=True)
    return list_journal_entries


def get_accounts_for_journal_entries(journal):
    """
    Función: Obtiene las cuentas que integran la poliza,
    recibida por parametro.

    Args:
        journal ([type]): [description]
        posting_date ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios de las cuentas por cada poliza
    """
    accounts = frappe.db.sql(f'''
        SELECT account AS lb_name, inflow_component,
        outflow_component, debit, credit, account_type,
        CASE
        WHEN debit > 0 AND (inflow_component != '' OR inflow_component != null)
            THEN debit
        WHEN credit > 0 AND (outflow_component != '' OR outflow_component != null)
            THEN credit
        END AS amount
        FROM `tabJournal Entry Account` WHERE parent = '{journal}'
        AND ( (inflow_component IS NOT NULL OR inflow_component != '')
            OR (outflow_component IS NOT NULL OR outflow_component != '') )
                ''', as_dict=True)
    return accounts


def get_categories_child():
    """
    Función: Obtiene las categorías que no de tipo grupo
    y tienen un flujo de caja asignado, salida o entrada.
    #Obteniendo categorias hijas

    Returns:
        Lista de diccionarios: Lista de diccionarios, con
        categorias, que no son grupo.
    """
    list_childs = frappe.db.sql('''
        SELECT name as components, parent, is_group, cash_effect,
        lft, rgt, direct_cash_flow_component_name
        FROM `tabDirect Cash Flow Component` WHERE is_group = 0
        ''', as_dict = True)

    return list_childs

def get_query_payment_entry(from_date, to_date):
    payments = frappe.db.sql(f'''
        SELECT paid_to AS lb_name, paid_from, paid_to, posting_date,
        inflow_component, outflow_component, paid_amount AS amount, payment_type
        FROM `tabPayment Entry` WHERE posting_date
        BETWEEN '{from_date}' AND '{to_date}' AND docstatus = 1 AND payment_type != 'Internal Transfer'
    ''', as_dict=True)
    if payments != []:
        for pay in payments:
            pay['posting_date'] = str(pay['posting_date'])
    return payments
