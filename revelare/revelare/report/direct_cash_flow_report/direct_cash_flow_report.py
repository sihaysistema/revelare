# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import frappe
from erpnext.accounts.utils import get_fiscal_year
from frappe import _, scrub
from frappe.utils import cint, flt, getdate
from frappe.utils.nestedset import NestedSet, get_root_of
from six import itervalues



def execute(filters=None):
    data = get_data(filters)
    return get_columns(filters), data

def get_columns(filters):
    '''Retorna las columnas a utilizar en el reporte'''
    ranges = get_period_date_ranges(filters)
    columns = [
        {
            "label": _("Components"),
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 200
        }
    ]

    # Genera las columnas en base al rango de fechas
    for dummy, end_date in ranges:
        period = get_period(end_date, filters)

        columns.append({
            "label": _(period),
            "fieldname":scrub(period),
            "fieldtype": "Float",
            "width": 120
        })
    return columns

def get_data(filters=None):
    # Obtenemos el listado de periodos a mostrar
    ranges = get_period_date_ranges(filters)

    # Obtenemos el arbol de categorias
    categories = get_categories()
    if not categories:
        return []

    # Agregando la indentación para mostrar en el reporte
    categories_by_name = filter_categories(categories)

    # Obteniendo los datos por categoria hija
    categories_child = get_categories_child()
    journal_entry = {}
    payment_entry = {}

    start_date = filters.from_date
    end_date = filters.to_date
    for root in categories_child:
        # Agregando entradas de diario por categoria
        if set_journal_entry(start_date, end_date, root['direct_cash_flow_component_name']) != []:
            journal_entry[root['direct_cash_flow_component_name']] = set_journal_entry(start_date, end_date, root['direct_cash_flow_component_name'])

        # Agregando entradas de pago por categoria
        if set_payment_entry(start_date, end_date, root['direct_cash_flow_component_name']) != []:
            payment_entry[root['direct_cash_flow_component_name']] = set_payment_entry(start_date, end_date, root['direct_cash_flow_component_name'])

    # Uniendo journal_entry y payment_entry
    data_by_categories = merging_dictionaries(journal_entry,payment_entry)

    # Calculando valor de cada documento en el campo amount
    #calculate_values(categories_by_name, data_by_categories)

    # Normalizando y uniendo categorias con journal_entry y payment_entry
    data_and_categories = formatting_data(data_by_categories, categories_by_name, ranges, filters)

    # Agregando datos a las columnas vacías
    data = adding_columns_to_data(data_and_categories, ranges, filters)
    dicToJSON('data_and_categories',data_and_categories)
    dicToJSON('ranges',ranges)
    dicToJSON('filters',filters)
    # Sumando la data del reporte
    data = accumulate_values_into_parents(data, ranges, filters)

    return data 

def get_period_date_ranges(filters):
    '''Obtiene el periodo en base al rango de fechas'''

    from dateutil.relativedelta import relativedelta
    from_date, to_date = getdate(filters.from_date), getdate(filters.to_date)

    increment = {
        "Monthly": 1,
        "Quarterly": 3,
        "Half-Yearly": 6,
        "Yearly": 12
    }.get(filters.range,1)

    periodic_daterange = []
    for dummy in range(1, 53, increment):
        if filters.range == "Weekly":
            period_end_date = from_date + relativedelta(days=6)
        else:
            period_end_date = from_date + relativedelta(months=increment, days=-1)

        if period_end_date > to_date:
            period_end_date = to_date
        periodic_daterange.append([from_date, period_end_date])

        from_date = period_end_date + relativedelta(days=1)
        if period_end_date == to_date:
            break

    return periodic_daterange

def get_period(posting_date, filters):
    '''retorna el periodo en base al filtro del reporte'''

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    if filters.range == 'Weekly':
        period = "Week " + str(posting_date.isocalendar()[1]) + " " + str(posting_date.year)
    elif filters.range == 'Monthly':
        period = str(months[posting_date.month - 1]) + " " + str(posting_date.year)
    elif filters.range == 'Quarterly':
        period = "Quarter " + str(((posting_date.month-1)//3)+1) +" " + str(posting_date.year)
    else:
        year = get_fiscal_year(posting_date, company=filters.company)
        period = str(year[2])

    return period

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

    return categories_by_name

#Obteniendo entradas de diario por categorias
def set_journal_entry(from_date, to_date, root):
    """Returns a dict like { "Journal Entry": [gl entries], ... }"""
    entry = []
    entry = frappe.db.sql(f'''
            SELECT JE.posting_date AS posting_date, 
            JEC.account AS lb_name,
            JEC.inflow_component AS inflow_component, 
            JEC.outflow_component AS outflow_component, 
            JEC.debit AS debit, JEC.credit AS credit
            FROM `tabJournal Entry` AS JE
            JOIN `tabJournal Entry Account` AS JEC ON JEC.parent = JE.name
            WHERE JEC.inflow_component = '{root}' 
            OR JEC.outflow_component = '{root}'
            AND JE.docstatus = 1
            AND JE.posting_date BETWEEN '{from_date}' AND '{to_date}' 
            ''', as_dict=True)

    for en in entry:
        if en['debit'] > 0 and en['inflow_component'] != None:
            en['amount'] =  en['debit']
        elif en['credit'] > 0 and en['outflow_component'] != None:
            en['amount'] =  en['credit']
    return entry or []

#Obteniendo entradas de diario por categorias
def set_payment_entry(from_date, to_date, root):
    """Returns a dict like { "paymets": [gl entries], ... }"""
    payments = []
    payments = frappe.db.sql(f'''
        SELECT name AS lb_name, posting_date, direct_cash_flow_component, paid_amount
        FROM `tabPayment Entry` WHERE direct_cash_flow_component = '{root}'
        AND posting_date BETWEEN '{from_date}' AND '{to_date}' 
        AND docstatus = 1
        ''', as_dict=True)

    for pay in payments:
        pay['amount'] = pay['paid_amount']


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
def formatting_data(data_by_categories, categories_by_name, ranges, filters):

    # Obteniendo campos necesarios para el reporte desde la data
    data = []
    for key, data_categories in data_by_categories.items():
        for values in data_categories:

            data.append({
                'name':values['lb_name'],
                'posting_date':values['posting_date'],
                'parent_direct_cash_flow_component': key,
                'cash_effect':'',
                'is_group': '',
                'indent': 0,
                'amount':values.get('amount')
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
            'amount' : 0
            })
        # Verificamos si hay documentos para agregar le de data
        for items in data:
            if items['parent_direct_cash_flow_component'] == name:

                categories_and_data.append({
                    'name' : items['name'],
                    'posting_date':items['posting_date'],
                    'parent_direct_cash_flow_component': categori['name'],
                    'cash_effect':items['cash_effect'],
                    'is_group':items['is_group'],
                    'indent':categori['indent'] + 1,
                    'amount':values.get('amount')
                    })

    return categories_and_data or []

# Calculando los totales de las categorias
def accumulate_values_into_parents(data_and_categories, ranges, filters):
    """accumulate children's values in parent category"""
    
    for item in reversed(data_and_categories):

        # Sumamos los documentos para en las categorias padre
        if item['is_group'] == '':
            
            for date_colum in ranges:
                period = get_period(date_colum[1], filters)
                period = scrub(period)
                
                if item.get(period) > 0:
                    # Obtenemos el nombre de componente padre y el monto
                    component_parent = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component')
                    amount = item.get(period)

                    # Buscamos en toda la lista, el compoente padre
                    for dictionary in data_and_categories:
                        cash_effect = dictionary['cash_effect']

                        if dictionary['name'] == component_parent:
                            
                            try:
                                # Sumamos o restamos el documento dependiendo del tipo de flujo del padre
                                if cash_effect == 'Inflow':
                                    dictionary[period] += amount
                                    
                                elif cash_effect == 'Outflow':
                                    dictionary[period] -= amount
                            except:
                                if cash_effect == 'Inflow':
                                    dictionary[period] = amount
                                    
                                elif cash_effect == 'Outflow':
                                    dictionary[period] = amount

        elif item['is_group'] == 0:
                
            for date_colum in ranges:
                period = get_period(date_colum[1], filters)
                period = scrub(period)
                
                if item.get(period, 0) != 0:
                    component_parent = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component','')
                    amount = item.get(period)

                    # Buscamos en toda la lista, el compoente padre
                    for dictionary in data_and_categories:
                        
                        # Sumamos la categoria hija en la categoria padre
                        if dictionary['name'] == component_parent:
                            dictionary[period] += amount
                    
        elif item['is_group'] == 1:
            for date_colum in ranges:
                period = get_period(date_colum[1], filters)
                period = scrub(period)

                if item.get(period, 0) != 0:
                    component_parent = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component','')
                    amount = item.get(period)
                    
                    # Buscamos en toda la lista, el compoente padre
                    for dictionary in data_and_categories:

                        # Sumamos la categoria hija en la categoria padre
                        if dictionary['name'] == component_parent:
                            dictionary[period] += amount


    return data_and_categories

def adding_columns_to_data(data, ranges, filters):
    for d in data:
        period_amount = ''
        if d.get('posting_date', None) != None:
            period_amount = get_period(d.get('posting_date'), filters)
            period_amount = scrub(period_amount)

        for from_date, to_date in ranges:
            period = get_period(to_date, filters)
            period = scrub(period)
            if period_amount == period:
                d[period] = d.get('amount')
            else:
                d[period] = 0

    return data


def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))