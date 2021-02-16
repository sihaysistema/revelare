# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import frappe
from frappe import _, scrub
from frappe.utils.nestedset import NestedSet, get_root_of
from six import itervalues


def execute(filters=None):
    data = get_data(filters, accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False,
        ignore_accumulated_values_for_fy=False , total = True)
    return get_columns(), data

def get_columns():
    '''Retorna las columnas a utilizar en el reporte'''
    columns = [
        {
            "label": _("Components"),
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Period 1"),
            "fieldname": "amount",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Period 2"),
            "fieldname": "period_2",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Total"),
            "fieldname": "total",
            "fieldtype": "Currency",
            "width": 100
        }
    ]
    return columns

def get_data(filters=None, accumulated_values=1, only_current_fiscal_year=True, ignore_closing_entries=False,
        ignore_accumulated_values_for_fy=False , total = True):
    categories = get_categories()
    if not categories:
        return []

    filtered_categories, categories_by_name, parent_children_map = filter_categories(categories)

    categories_child = get_categories_child()
    journal_entry = {}
    payment_entry = {}

    for root in categories_child:
        # Agregando entradas de diario por categoria
        if set_journal_entry(filters, root['direct_cash_flow_component_name']) != []:
            journal_entry[root['direct_cash_flow_component_name']] = set_journal_entry(filters, root['direct_cash_flow_component_name'])
        else:
            pass

        # Agregando entradas de pago por categoria
        if set_payment_entry(filters, root['direct_cash_flow_component_name']) != []:
            payment_entry[root['direct_cash_flow_component_name']] = set_payment_entry(filters, root['direct_cash_flow_component_name'])
        else:
            pass

    # Uniendo journal_entry y payment_entry
    data_by_categories = merging_dictionaries(journal_entry,payment_entry)
    # Calculando valor de cada documento
    calculate_values(categories_by_name, data_by_categories)

    # Normalizando y uniendo categorias con journal_entry y payment_entry
    data_and_categories = formatting_data(data_by_categories, categories_by_name)

    # Sumando la data del reporte
    data = accumulate_values_into_parents(data_and_categories)
    return data 

# Obtenemos las categorias
def get_categories():
    return frappe.db.sql("""
        SELECT name, 
        parent_direct_cash_flow_component,
        lft, rgt, cash_effect,is_group
        FROM `tabDirect Cash Flow Component` 
        ORDER BY lft
        """, as_dict=True)

# Filtro de cargorias
def filter_categories(categories, depth=10):
    parent_children_map = {}
    categories_by_name = {}
    filtered_categories = []
    for d in categories:
        categories_by_name[d.name] = d
        parent_children_map.setdefault(d.parent_direct_cash_flow_component or None, []).append(d)

    def add_to_list(parent, level):
        if level < depth:
            children = parent_children_map.get(parent) or []

            for child in children:
                child.indent = level
                filtered_categories.append(child)
                add_to_list(child.name, level + 1)

    add_to_list(None, 0)

    return filtered_categories, categories_by_name, parent_children_map

#Obteniendo entradas de diario por categorias
def set_journal_entry(filters, root):
    """Returns a dict like { "account": [gl entries], ... }"""
    entry = []
    entry = frappe.db.sql(f'''
        SELECT JE.posting_date AS posting_date, 
        JEC.account AS lb_name,
        JEC.direct_cash_flow_component AS direct_cash_flow_component, 
        JEC.debit AS debit, JEC.credit AS credit,
        JEC.debit_in_account_currency AS debit_in_account_currency,
        JEC.credit_in_account_currency AS credit_in_account_currency,
        JEC.account_currency AS acconut_currency
        FROM `tabJournal Entry` AS JE
        JOIN `tabJournal Entry Account` AS JEC ON JEC.parent = JE.name
        WHERE JEC.direct_cash_flow_component = '{root}'
        AND JE.posting_date BETWEEN '{filters.from_date}' AND '{filters.to_date}' 
        ''', as_dict=True)

    return entry or []

#Obteniendo entradas de diario por categorias
def set_payment_entry(filters, root):
    """Returns a dict like { "account": [gl entries], ... }"""
    payments = []
    payments = frappe.db.sql(f'''
        SELECT name AS lb_name, posting_date, direct_cash_flow_component, paid_amount  
        FROM `tabPayment Entry` WHERE direct_cash_flow_component = '{root}'
        AND posting_date BETWEEN '{filters.from_date}' AND '{filters.to_date}' 
        ''', as_dict=True)

    return payments or []

#Obteniendo categorias hijas
def get_categories_child():
    list_childs = frappe.db.sql('''
        SELECT name as components, parent, is_group, cash_effect,
        lft, rgt, direct_cash_flow_component_name
        FROM `tabDirect Cash Flow Component` WHERE is_group = 0
        ''', as_dict = True)
    
    return list_childs

#Fusionando journal_entry y payments_entry
def merging_dictionaries(journal_entry,payment_entry):
    data= {}
    for category, detail in journal_entry.items():
        data[category] = detail
        
    for category, detail in payment_entry.items():
        if data.get(category):
            data[category].extend(detail)
            print(f'esta categoria ya esta {category}')
        else:
            data[category] = detail
        
    return data

# Calculando totales
def calculate_values(categories_by_name, data_by_categories, peirod_list=None):
    # Function calculate values
    for data_categories in data_by_categories.values():
        
        for data in data_categories:
            d = categories_by_name.get(data['direct_cash_flow_component'])
            if not d:
                """
                frappe.msgprint(
                        _("No se ha podido recuperar la información de {0}.".format(data['direct_cash_flow_component'])), 
                        title="Error",
                        raise_exception=1)
                """
                pass
            
            if 'debit' in data:
                if data['debit'] > 0.0:
                    data['amount'] = data['debit']
                else:
                    data['amount'] = data['credit']
                    
            elif 'credit' in data:
                if data['credit'] > 0.0:
                    data['amount'] = data['credit']
                else:
                    data['amount'] = data['debit']

            elif 'paid_amount' in data:
                data['amount'] = data['paid_amount']

# Normaliza los datos en una sola lista de diccionarios
def formatting_data(data_by_categories, categories_by_name):
    # Obteniendo campos necesarios para el reporte desde la data
    data = []
    for key, data_categories in data_by_categories.items():
        for values in data_categories:
            data.append({
                'name':values['lb_name'],
                'posting_date':values['posting_date'],
                'parent_direct_cash_flow_component': key,
                'cash_effect':'',
                'is_group': 0,
                'indent': 0,
                'amount':values['amount']
            })
            
    # Agregando data a categorias
    categories_and_data = []
    for name, categori in categories_by_name.items():
        categories_and_data.append({
            'name' : categori['name'],
            'parent_direct_cash_flow_component': categori['parent_direct_cash_flow_component'],
            'cash_effect':categori['cash_effect'],
            'is_group':categori['is_group'],
            'indent':categori['indent'],
            'amount':0
            })
        # Verificamos si hay documentos para agregar le de data
        for items in data:
            if items['parent_direct_cash_flow_component'] == name:
                categories_and_data.append({
                    'name' : items['name'],
                    'parent_direct_cash_flow_component': categori['name'],
                    'cash_effect':items['cash_effect'],
                    'is_group':items['is_group'],
                    'indent':categori['indent'] + 1,
                    'amount':items['amount']
                    })
    
    return categories_and_data or []

# Calculando los totales de las categorias
def accumulate_values_into_parents(data_and_categories, period_list=None):
    """accumulate children's values in parent category"""
    
    for item in reversed(data_and_categories):
        
        # Sumamos los documentos para en las categorias padre
        if item['is_group'] == 0 and item['cash_effect'] == '':
            
            # Obtenemos el nombre de componente padre y el monto
            component = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component')
            amount = item.get('amount')

            # Buscamos en toda la lista, el compoente padre
            for dictionary in data_and_categories:
                cash_effect = dictionary['cash_effect']
                if dictionary['name'] == component:
                    
                    # Sumamos o restamos el documento dependiendo del tipo de flujo del padre
                    if cash_effect == 'Inflow':
                        dictionary['amount'] += amount
                    elif cash_effect == 'Outflow':
                        dictionary['amount'] -= amount
        else:
            component = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component')
            amount = item.get('amount')
            
            # Buscamos en toda la lista, el compoente padre
            for dictionary in reversed(data_and_categories):
                # Sumamos la categoria hija en la categoria padre
                if dictionary['name'] == component:
                    dictionary['amount'] += amount
            
    return data_and_categories

