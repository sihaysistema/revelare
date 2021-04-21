# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import frappe
from frappe import _, scrub


def execute(filters=None):
    columns, data = [], []
    return get_columns(filters), get_data(filters)

def get_columns(filters):
    '''Retorna las columnas a utilizar en el reporte'''
    
    columns = [
        {
            "label": _("ID"),
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 365
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Int",
        }
    ]

    return columns

def get_data(filters=None):
    """Obtiene los datos pasados por la url al momento de instanciar el 
    el reporte

    Args:
        

    Returns:
        [lista][diccionarios]: [{'name':'Operations','amount':200}]
    """

    # Forma de pasar filtros por url
    # #query-report/Cash%20Flow%20Detail?from_date=2021-01-02
    payments_entry = set_payment_entry(filters.from_date, filters.to_date, 'Interest Received from Investment')
    journal_entry = set_journal_entry(filters.from_date, filters.to_date, 'Interest Received from Investment')
    # dicToJSON('payments_entry',payments_entry)
    # dicToJSON('journal_entry',journal_entry)
    data = []
    for pay in payments_entry:
        data.append({
            'name':pay['name'],
            'amount':pay['amount'],
            'type':'payment_entry',
            'name_url':pay['name_url']
        })
    for journal in journal_entry:
        data.append({
            'name':journal['name'],
            'amount':journal['amount'],
            'type':'journal_entry',
            'name_url':journal['name_url']
        })
    data = rename_categories(data)

    amount_total = 0
    for d in reversed(data):
        amount_total += d['amount']
    data.insert(0,{
                    'name':'Interest Received from Investment',
                    'amount':amount_total
                })

    return data 

#Obteniendo pagos por categorias
def set_payment_entry(from_date, to_date, cartegory):
    """
    Obtiene todos los pagos, que tengan que ver
    con flujo de efectivo.

    Returns:
        lista de diccionarios: [{cuenta, cagoria, ...},{cuenta, cagoria, ...}]
    """    

    # Para filtrar si un documento esta validado o no, el digito debe estar como string
    # Ej: docstatus '1'
    payments = []
    payments = frappe.db.sql(f'''
        SELECT name as name_url, paid_from, paid_to, posting_date, inflow_component, 
        outflow_component, paid_amount AS amount, payment_type
        FROM `tabPayment Entry` 
        WHERE inflow_component = 'Interest Received from Investment' OR outflow_component = 'Interest Received from Investment'
        AND posting_date BETWEEN '{from_date}' AND '{to_date}' AND docstatus = 1 ''', as_dict=True)

    for item in payments:
        if item['payment_type'] == 'Receive':
            item['name'] =item['paid_to']
        elif item['payment_type'] == 'Pay':
            item['name'] =item['paid_from']

    return payments or []

def set_journal_entry(from_date, to_date, cartegory):
    entry = []
    entry = frappe.db.sql(f'''
            SELECT JE.posting_date AS posting_date, 
            JE.docstatus,
            JE.name as name_url,
            JEC.account AS name,
            JEC.inflow_component AS inflow_component, 
            JEC.outflow_component AS outflow_component, 
            JEC.debit AS debit, JEC.credit AS credit,
            JEC.account_type
            FROM `tabJournal Entry` AS JE
            JOIN `tabJournal Entry Account` AS JEC ON JEC.parent = JE.name 
            AND JE.docstatus = 1 AND JEC.docstatus = 1
            AND JE.posting_date BETWEEN '{from_date}' AND '{to_date}' 
            AND JEC.account_type = 'Bank'  OR JEC.account_type = 'Cash'
            WHERE JEC.inflow_component = 'Interest Received from Investment' 
            OR JEC.outflow_component = 'Interest Received from Investment'
            ''', as_dict=True)
            

    for en in entry:
        en['posting_date'] = str(en['posting_date'])
        if en['debit'] > 0 and en['inflow_component'] != None:
            en['amount'] =  en['debit']
        elif en['credit'] > 0 and en['outflow_component'] != None:
            en['amount'] =  en['credit']
    return entry or []

def rename_categories(data, from_date='', to_date=''):
    for d in data:
        one_string = '<a target="_blank" onclick="open_one_tab('
        two_string = ')">'
        three_string = '</a>'
        d['name'] = f"{one_string}'{d['name_url']}','{d['type']}'{two_string}{d['name']}{three_string}"
    return data

# Para debug
def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
