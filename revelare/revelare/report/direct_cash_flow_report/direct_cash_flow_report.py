# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import datetime
import json
from datetime import datetime

import frappe
import numpy as np
import pandas as pd
from erpnext.accounts.utils import get_fiscal_year
from frappe import _, scrub
from frappe.utils import cint, flt, getdate
from six import itervalues


def execute(filters=None):
    data = get_data(filters)
    columns = get_columns(filters)
    return columns, data

def get_columns(filters):
    """
    Asinga las columnas por periodo delimitado en el reporte

    Args:
        filters (diccionario): company, fom_date, to_date, range 

    Returns:
        Lista: Lista de diccionarios
    """    
    ranges = get_period_date_ranges(filters)
    columns = [
        {
            "label": _("Components"),
            "fieldname": "name",
            "fieldtype": "Data",
            "width": 365
        }
    ]

    # Genera las columnas en base al rango de fechas
    for dummy, end_date in ranges:
        fecha_dt = datetime.strptime(str(end_date), '%Y-%m-%d')
        period = get_period(fecha_dt, filters)

        columns.append({
            "label": _(period),
            "fieldname":scrub(period),
            "fieldtype": "Data",
            "width": 120
        })
    return columns

def get_data(filters=None):
    """Función para obtener y procesar los datos, para el reporte

    Args:
        filters ([type], optional): [description]. Defaults to None.

    Returns:
        lista de diccionarios: Una lista de diccionarios, en orden ascendente, cada clave corresponde a un
        nombre de columna declarado en la función anterior, y el valor es lo que se mostrará.
    """    
    # Obtenemos el listado de periodos a mostrar
    ranges = get_period_date_ranges(filters)

    # Obtenemos el árbol de categorias
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

    journal_entry = get_journal_entry(start_date, end_date)
    payment_entry, undefined_payment_categories = get_payment_entry(start_date, end_date)

    # Agregando categorias no definidas de entras de diario y pagos
    # journal_entry = add_undefined_entries(journal_entry, undefined_journal_entries)
    payment_entry = add_undefined_payments(payment_entry, undefined_payment_categories)

    
    # Uniendo journal_entry y payment_entry
    data_by_categories = merging_dictionaries(journal_entry,payment_entry)

    # Normalizando y uniendo categorias con journal_entry y payment_entry
    data_and_categories = formatting_data(data_by_categories, categories_by_name, filters)


    # Agregando datos a las columnas vacías
    data = adding_columns_to_data(data_and_categories, ranges, filters)

    dicToJSON('data',data)
    # Sumando la data del reporte
    data = accumulate_values_into_parents(data, ranges, filters)
    dicToJSON('data',data)
    # Sumando cuentas hijas
    data = add_values_of_sub_accounts(data)
    data = rename_category(data)

    data = insert_link_to_categories(data, filters.from_date,filters.to_date)

    # Agregando color a cada dato
    data = adding_color_to_data(data, ranges, filters)

    # TODO: Cuando se maneje consolidado el flujo de caja se va a indicar el nombre de la compania en esta celda
    # Y se le agregara un totalizador
    

    return data 

# ******************** Inicio Logica de Rangos de Fecha ********************

def get_period_date_ranges(filters):
    """
    Función: Obtiene el periodo en base al rango de fechas

    Args:
        filters ([type]): [description]

    Returno:
        Lista de listas: Listas de listas, con dos elementos. Cada sublista
        con la fecha inicial y la fecha final del rango de fechas seleccionado.
    """

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
    """
    Función: Para obtener el periodo en base a los filtros del reporte

    Args:
        posting_date ([type]): [description]
        filters ([type]): [description]

    Returns:
        Lista de diccionarios: Listas de diccionarios, con las etiquetas de cada periodo
    """    
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

def get_categories():
    """
    Función: Obtiene todas las categorias del árbol de los componentes de flujo de caja directo

    Returns:
        Lista de diccionarios: Lista de diccionarios, que obtiene el orden de las categorias
        delimitado en el árbol de flujo de caja directo
    """    
    return frappe.db.sql("""
        SELECT name, 
        parent_direct_cash_flow_component,
        lft, rgt, cash_effect,is_group
        FROM `tabDirect Cash Flow Component` 
        ORDER BY lft
        """, as_dict=True)

def filter_categories(categories, depth=10):
    """
    Función: Para agregar la propiedad indent, al árbol de categorias

    Args:
        categories ([type]): [description]
        depth (int, optional): [description]. Defaults to 10.

    Returns:
        Lista de diccionarios: Lista de diccionarios, con la propiedad de indentación
        para mostrar el reporte indentado
    """    
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

# ******************** Fin Logica de Rangos de Fecha ********************

# ******************** Inicio Logica Jounal Entry ********************

# es-GT: Obteniendo entradas de diario por categorias
def get_journal_entry(start_date, end_date):
    """
    Función: Obtiene y procesa las polizas de diario, que tengan que ver con 
    salidas o entradas de flujo de caja

    Args:
        start_date ([type]): [description]
        end_date ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, con las cuentas de polizasd de diario
        filtradas repecto al flujo de caja.
    """
    journal_entry = get_query_journal_entry(start_date, end_date)

    # Pasandolo a Pandas
    df_journal = pd.DataFrame(json.loads(json.dumps(journal_entry)))
    df_journal = df_journal.fillna("")

    journal_entry = {}
    # Obtenemos los componente definidos
    df_journal_categories = df_journal.query("inflow_component != '' or outflow_component != ''")
    journal_categories = df_journal_categories.to_dict(orient='records')
    for journal in journal_categories:
        if journal['inflow_component'] != '':
            try:
                journal_entry[journal['inflow_component']].append(journal)
            except:
                journal_entry[journal['inflow_component']] = [journal]
        elif journal['outflow_component'] != '':
            try:
                journal_entry[journal['outflow_component']].append(journal)
            except:
                journal_entry[journal['outflow_component']] = [journal]

    """# obtenemos los componenete indefinidos
    df_journal_undefined_categories = df_journal.query("inflow_component == '' and outflow_component == ''")

    journal_undefined_categories = df_journal_undefined_categories.to_dict(orient='records')
    for journal in journal_undefined_categories:
        if journal.get('amount','') == '':
            if journal.get('debit', None) != 0:
                journal['amount'] = journal.get('debit')
            elif journal.get('credit', None) != 0:
                journal['amount'] = journal.get('credit')"""
    #return journal_entry, journal_undefined_categories
    return journal_entry

# Obtiene el formato de Journal entries
# def get_query_journal_entry(from_date, to_date):
#     entry = []
#     entry = frappe.db.sql(f'''
#             SELECT JE.posting_date AS posting_date, 
#             JE.docstatus,
#             JEC.account AS lb_name,
#             JEC.inflow_component AS inflow_component, 
#             JEC.outflow_component AS outflow_component, 
#             JEC.debit AS debit, JEC.credit AS credit,
#             JEC.account_type
#             FROM `tabJournal Entry` AS JE
#             JOIN `tabJournal Entry Account` AS JEC ON JEC.parent = JE.name AND JE.docstatus = 1 AND JEC.docstatus = 1
#             AND JE.posting_date BETWEEN '{from_date}' AND '{to_date}' AND JEC.account_type = 'Bank'  OR JEC.account_type = 'Cash'
#             ''', as_dict=True)
            

#     for en in entry:
#         en['posting_date'] = str(en['posting_date'])
#         if en['debit'] > 0 and en['inflow_component'] != None:
#             en['amount'] =  en['debit']
#         elif en['credit'] > 0 and en['outflow_component'] != None:
#             en['amount'] =  en['credit']
#     return entry or []

def get_query_journal_entry(from_date, to_date):
    """
    Función: Para obtener cuenta de polizas especificás para el reporte, 
    cuentas que son de tipo efectivo(Cash) o banco(Bank)

    Args:
        from_date ([type]): [description]
        to_date ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, con los elementos formateados
        para mostrar en el reporte
    """    
    individual_entries = individual_journal_entries(from_date, to_date)
    new_journal_entry = [] # Polizas validas para reporte
    for journal in individual_entries: # por cada poliza
        journal_flatten = [] # Aplanamos el array
        journal_ = list(journal.values())
        for j in journal_:
            for item in j:# Accedemos hasta el diccionario
                journal_flatten.append(item)# Agregamos la cuenta a la poliza

        if there_is_only_one_cash_flow_account(journal_flatten): # si es caso 1
            for ju in journal_flatten: 
                if ju.get('account_type') == 'Bank' or ju.get('account_type') == 'Cash': # Si es cash o bank
                    new_journal_entry.append(ju) # lo agregamos a la data
        elif all_cash_or_bank_accounts(journal_flatten):
            pass
        elif there_are_different_accounts(journal_flatten):
            """ 
            El caso 3, se ha analizado la forma de determinar cual fue el flujo de caja 
            realizado en la transacción, pero no es coherente al momento de asignar le la categoria,
            para mostrar en el reporte de flujo de caja directo.
            """
            debit = 0
            credit = 0
            for journal_f in journal_flatten:
                if journal_f['account_type'] == 'Bank' or journal_f['account_type'] == 'Cash':
                    if journal_f['debit'] > 0.0:
                        debit += journal_f['debit']
                    elif journal_f['credit'] > 0.0:
                        credit += journal_f['credit']
        return new_journal_entry

def individual_journal_entries(from_date, to_date):
    """
    Función: Genera la homologación de las polizas de ERPNEXT,
    en formato JSON o Diccionario para Python.

    Args:
        from_date ([type]): [description]
        to_date ([type]): [description]

    Returns:
        Lista de Diccionarios: Lista de diccionarios, divididos por poliza, por medio de un diccionario
    """    
    list_journal_entries = get_list_journal_entries(from_date, to_date)
    individual_entries = []
    for journal in list_journal_entries:
        individual_entries.append({
            journal['name']: get_accounts_for_journal_entries(journal['name'], journal['posting_date'])
        })
    return individual_entries

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
                        SELECT JE.name, JE.posting_date
                        FROM `tabJournal Entry` AS JE
                        INNER JOIN `tabJournal Entry Account` AS JEC 
                        ON JEC.parent = JE.name AND JE.docstatus = 1 AND JE.posting_date BETWEEN '{from_date}' AND '{to_date}'
                        WHERE JEC.account_type = 'Bank' OR JEC.account_type = 'Cash' GROUP BY name;
                        ''', as_dict=True)
    return list_journal_entries

def get_accounts_for_journal_entries(journal, posting_date):
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
                outflow_component, debit, credit, account_type 
                FROM `tabJournal Entry Account` WHERE parent = '{journal}';
                ''', as_dict=True)
    for c in accounts:
        c['posting_date']= str(posting_date)
        if c['debit'] > 0 and c['inflow_component'] != None:
            c['amount'] =  c['debit']
        elif c['credit'] > 0 and c['outflow_component'] != None:
            c['amount'] =  c['credit']
    return accounts

def all_cash_or_bank_accounts(journal_flatten):
    """
    Función: Verifica si, la poliza recibida por parametro,
    tiene solo una cuenta de tipo efectivo(Cash) o banco(Bank)

    Args:
        journal_flatten ([type]): [description]

    Returns:
        Boolean: Verdadero o Falso
    """    
    for journal_f in journal_flatten:
        if journal_f['account_type'] != 'Bank' and journal_f['account_type'] != 'Cash':
            return False
    return True

def there_is_only_one_cash_flow_account(journal_flatten):
    """
    Función: Verifica si, la poliza recibida por parametro,
    tiene solo cuentas de tipo efectivo(Cash) o banco(Bank)

    Args:
        journal_flatten ([type]): [description]

    Returns:
        Boolean: Verdadero o Falso
    """    
    count = 0
    for journal_f in journal_flatten:
        if journal_f['account_type'] == 'Bank' or journal_f['account_type'] == 'Cash':
            count += 1
    if count == 1:
        return True
    else: 
        return False

def there_are_different_accounts(journal_flatten):
    """
    Función: Verifica si, la poliza recibida por parametro,
    tiene más de tres cuentas una cuenta y entre ellas exista
    una cuenta distinta a efectivo(Cash) o banco(Bank)

    Args:
        journal_flatten ([type]): [description]

    Returns:
        Boolean: Verdadero o Falso
    """    
    if len(journal_flatten) > 2:
        count_cash = 0
        count_dif = 0
        for journal_f in journal_flatten:
            if journal_f['account_type'] == 'Bank' or journal_f['account_type'] == 'Cash':
                count_cash += 1
            elif journal_f['account_type'] != 'Bank' or journal_f['account_type'] != 'Cash':
                count_dif += 1
        if count_cash > count_dif and count_dif != 0: # si hay mas cuentas que no tengan que ver con dinero
            return True
        elif count_cash > 1 and count_dif != 0: # si hay mas cuentas que tienen que ver con dinero
            return True

    return False

def add_undefined_entries(journal_entry, undefined):
    """
    Función: Agrega las polizas de diario sin categoria,
    a las entras de diario con categoria.

    Args:
        journal_entry ([type]): [description]
        undefined ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, con cuenta de polizas de diario
        con la categoria definida o indefinida.
    """    
    journal_entry['Uncategorized Inflows'] = []
    journal_entry['Uncategorized Outflows'] = []
    for category in undefined:
        if category['debit'] > 0:
            category['amount'] =  category['debit']
            if (journal_entry.get('Uncategorized Inflows', None) != None):
                journal_entry['Uncategorized Inflows'].append(category)
            else: 
                journal_entry['Uncategorized Inflows'] = category
                
        elif category['credit'] > 0:
            category['amount'] =  category['credit']
            if (journal_entry.get('Uncategorized Outflows', None) != None):
                journal_entry['Uncategorized Outflows'].append(category)
            else:
                journal_entry['Uncategorized Outflows'] = category    
    return journal_entry

# ******************** Fin Logica Jounal Entry ********************

# ******************** Inicio Logica Payment Entry ********************
def get_query_payment_entry(from_date, to_date):
    payments = []
    payments = frappe.db.sql(f'''
        SELECT paid_to AS lb_name, paid_from, paid_to, posting_date, 
        inflow_component, outflow_component, paid_amount AS amount, payment_type
        FROM `tabPayment Entry` WHERE posting_date 
        BETWEEN '{from_date}' AND '{to_date}' AND docstatus = 1
    ''', as_dict=True)

    for pay in payments:
        pay['posting_date'] = str(pay['posting_date'])
    return payments

def get_payment_entry(from_date, to_date):
    payment_entry = get_query_payment_entry(from_date, to_date)
    df_payment = pd.DataFrame(json.loads(json.dumps(payment_entry)))
    # obtenemos los componenete indefinidos
    df_payment = df_payment.fillna("")
    df_payment_undefined_categories = df_payment.query("inflow_component == '' and outflow_component == '' and payment_type != 'Internal Transfer'")

    # Obtenemos los componente definidos
    df_payment_categories = df_payment.query("inflow_component != '' or outflow_component != ''")

    payment_undefined_categories = df_payment_undefined_categories.to_dict(orient='records')
    payment_categories = df_payment_categories.to_dict(orient='records')

    payments = {}
    for payment in payment_categories:
        if payment['inflow_component'] != '':
            try:
                payments[payment['inflow_component']].append(payment)
            except:
                payments[payment['inflow_component']] = [payment]
        elif payment['outflow_component'] != '':
            try:
                payments[payment['outflow_component']].append(payment)
            except:
                payments[payment['outflow_component']] = [payment]

    for d in payments.values():
        for item in d:
            if item['payment_type'] == 'Receive':
                item['lb_name'] =item['paid_to']
            elif item['payment_type'] == 'Pay':
                item['lb_name'] =item['paid_from']

    for d in payment_undefined_categories:
        if d['payment_type'] == 'Receive':
            d['lb_name'] =d['paid_to']
        elif d['payment_type'] == 'Pay':
            d['lb_name'] =d['paid_from']

    return payments, payment_undefined_categories

# ******************** Fin Logica Payment Entry ********************

# ******************** Inicio Logica Process Data ********************

def add_undefined_payments(payment, undefined):
    """
    Función: Agrega las cuenta de entras de diario sin categoria,
    a las cuenta de entras de diario con categoria.

    Args:
        journal_entry ([type]): [description]
        undefined ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, con entras de diario
        con la categoria definida o indefinida.
    """    
    payment['Uncategorized Inflows'] = []
    payment['Uncategorized Outflows'] = []
    for category in undefined:
        if category['payment_type'] == 'Receive':
            if (payment.get('Uncategorized Inflows', None) != None):
                payment['Uncategorized Inflows'].append(category)
            else: 
                payment['Uncategorized Inflows'] = category
                
        elif category['payment_type'] == 'Pay':
            if (payment.get('Uncategorized Outflows', None) != None):
                payment['Uncategorized Outflows'].append(category)
            else:
                payment['Uncategorized Outflows'] = category    
    return payment

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

def merging_dictionaries(journal_entry,payment_entry):
    """
    Función: Para unir las lista de diccionaris,
    de polizas y entradas de diario.
    #Fusionando journal_entry y payments_entry

    Args:
        journal_entry ([type]): [description]
        payment_entry ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, 
        con entras y polizas de pago, en una misma estructura.
    """    
    data= {}
    for category, detail in journal_entry.items():
        data[category] = detail

    for category, detail in payment_entry.items():
        if data.get(category):
            data[category].extend(detail)
        else:
            data[category] = detail
        
    return data

# Calculando totales
def calculate_values(categories_by_name, data_by_categories, peirod_list=None):
    # Function calculate values
    for data_categories in data_by_categories.values():
        
        for data in data_categories:
            d = categories_by_name.get(data['direct_cash_flow_component'])
            
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

def formatting_data(data_by_categories, categories_by_name, filters):
    """
    Función: Normaliza los datos en una sola lista de diccionarios
    Devuelve los datos con el siguiente formato.
    {
        'name':'name',
        'posting_date':'posting_date',
        'parent_direct_cash_flow_component':'parent',
        'cash_effect':'cash_effect',
        'is_group':'is_group',
        'indent':'indent',
        'amount':'amount'
    }

    Args:
        data_by_categories ([type]): [description]
        categories_by_name ([type]): [description]
        filters ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios ordenas con el formato necesario para mostrar
        los valores en el reporte
    """    

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
                    'posting_date' : items['posting_date'],
                    'parent_direct_cash_flow_component' : categori['name'],
                    'cash_effect' : items['cash_effect'],
                    'is_group' : items['is_group'],
                    'indent' : categori['indent'] + 1,
                    'amount' : items.get('amount')
                    })

    return categories_and_data or []

def accumulate_values_into_parents(data_and_categories, ranges, filters):
    """
    Función: Suma los datos, de las polizas y entras de pago. 
    En las categorias del árbol de flujo de caja, por rango deliminatado.
    # Calculando los totales de las categorias

    Args:
        data_and_categories ([type]): [description]
        ranges ([type]): [description]
        filters ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, con el monto sumado
        por rando de fecha delimitado en el reporte
    """    

    for item in reversed(data_and_categories):

        # Sumamos los documentos para en las categorias padre
        if item['is_group'] == '':
            
            for date_colum in ranges:
                fecha_dt = datetime.strptime(str(date_colum[1]), '%Y-%m-%d')
                period = get_period(fecha_dt, filters)
                period = scrub(period)
                
                if item.get(period) > 0:
                    # Obtenemos el nombre de componente padre y el monto
                    component_parent = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component')
                    # Buscamos en toda la lista, el componente padre
                    for dictionary in reversed(data_and_categories):
                        cash_effect = dictionary['cash_effect']

                        if dictionary['name'] == component_parent:

                            try:

                                # Sumamos o restamos el documento dependiendo del tipo de flujo del padre
                                if cash_effect == 'Inflow':
                                    dictionary[period] += item.get(period)

                                elif cash_effect == 'Outflow':
                                    # haciendo negativo el hijo
                                    item[period] = (item.get(period)*-1)
                                    dictionary[period] += item.get(period)

                            except:
                                if cash_effect == 'Inflow':
                                    dictionary[period] = item.get(period)

                                elif cash_effect == 'Outflow':
                                    item[period] = (item.get(period)*-1)
                                    dictionary[period] = item.get(period)

        elif item['is_group'] == 0:
                
            for date_colum in ranges:
                fecha_dt = datetime.strptime(str(date_colum[1]), '%Y-%m-%d')
                period = get_period(fecha_dt, filters)
                period = scrub(period)
                
                if item.get(period, 0) != 0:
                    component_parent = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component','')
                    amount = item.get(period)

                    # Buscamos en toda la lista, el compoente padre
                    for dictionary in reversed(data_and_categories):
                        
                        # Sumamos la categoria hija en la categoria padre
                        if dictionary['name'] == component_parent:
                            dictionary[period] += amount
                    
        elif item['is_group'] == 1:
            for date_colum in ranges:
                fecha_dt = datetime.strptime(str(date_colum[1]), '%Y-%m-%d')
                period = get_period(fecha_dt, filters)
                period = scrub(period)

                if item.get(period, 0) != 0:
                    component_parent = data_and_categories[data_and_categories.index(item)].get('parent_direct_cash_flow_component','')
                    amount = item.get(period)
                    
                    # Buscamos en toda la lista, el compoente padre
                    for dictionary in reversed(data_and_categories):

                        # Sumamos la categoria hija en la categoria padre
                        if dictionary['name'] == component_parent:
                            dictionary[period] += amount
    

    return data_and_categories

def add_values_of_sub_accounts(data):
    """
    Función: Suma los valores de las cuentas que se repiten
    en el reporte.
    # Sumando valores de las cuentas hijas

    Args:
        data ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios,
        suma y elimina las cuentas repetidas.
    """    
    for d in range(0, len(data)-1):
        if (d+1) < len(data)-1:
            if data[d]['name'] == data[d+1]['name']:
                for key, values in data[d].items():
                        if data[d][key] != data[d+1][key] and key != 'posting_date':
                            if data[d][key] != 0:
                                data[d][key] = data[d][key] + data[d+1][key]
                            elif data[d][key] == 0:
                                data[d][key] = data[d+1][key]
                data.pop(d+1)
    return data

def adding_columns_to_data(data, ranges, filters):
    """
    Función: Rellena, los campos que no tienen
    datos, con 0, para mostrar los datos correctamente
    en el reporte.
    # Agregando datos a las columnas que no tienen

    Args:
        data ([type]): [description]
        ranges ([type]): [description]
        filters ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios, con data
        llena para mostrar en el reporte.
    """    
    for d in data:
        period_amount = ''
        if d.get('posting_date', None) != None:
            fecha_dt = datetime.strptime(str(d.get('posting_date')), '%Y-%m-%d')
            period_amount = get_period(fecha_dt, filters)
            period_amount = scrub(period_amount)

        for date_colum in ranges:
            fecha_dt = datetime.strptime(str(date_colum[1]), '%Y-%m-%d')
            period = get_period(fecha_dt, filters)
            period = scrub(period)
            if period_amount == period:
                d[period] = d.get('amount')
            else:
                d[period] = 0

    return data

def adding_color_to_data(data, ranges, filters):
    """Agrega color a los datos al momento de mostrar los en el reporte
    Args:
        data ([list]): {Fila por cada item}
        ranges ([list]): {Tangos de fechas en los que se opera}
        filters ([list]): {Delimitan los rangos de fechas}
    return: diccionario
    """    

    # --------- Valores Positivos ----------
    positive_values_strong_1 = "<span style='color: #006600; background-color: white; float: right; text-align: right; vertical-align: text-top;'><strong>"
    positive_values_strong_2 = "</strong></span>"
    positive_values_1 = "<span style='color: #006600; background-color: white; float: right; text-align: right; vertical-align: text-top;'>"
    positive_values_2 = "</span>"

    # --------- Valores Negativos ----------
    negative_values_strong_1 = "<span style='color: #CC0000; background-color: white; float: right; text-align: right; vertical-align: text-top;'><strong>"
    negative_values_strong_2 = "</strong></span>"
    negative_values_1 = "<span style='color: #CC0000; background-color: white; float: right; text-align: right; vertical-align: text-top;'>"
    negative_values_2 = "</span>"

    # --------- Valores nulos ----------
    neutral_values_strong_1 = "<span style='color: black; background-color: #FFFFFF; float: right; text-align: right; vertical-align: text-top;'><strong>"
    neutral_values_strong_2 = "</strong></span>"
    neutral_values_1 = "<span style='color: black; background-color: #FFFFFF; float: right; text-align: right; vertical-align: text-top;'>"
    neutral_values_2 = "</span>"

    quantity_style_few_1 = "<span style='color: black; background-color: blue; float: right; text-align: right; vertical-align: text-top;'><strong>"
    quantity_style_few_2 = "</strong></span>"
    item_link_open = "<a href='#Form/Item/"
    item_link_open_end = "' target='_blank'>"
    item_link_close = "</a>"

    # Obtenemos cada fila de la data
    for row_item in data:

        # Por cada fila le agregara un color dependiendo del valor
        for date_colum in ranges:
            fecha_dt = datetime.strptime(str(date_colum[1]), '%Y-%m-%d')
            period = get_period(fecha_dt, filters)
            period = scrub(period)
            row_item[period] = "{:.2f}".format(
                float(row_item[period]))
            if float(row_item[period]) > 0:
                if row_item['is_group'] == '':
                    row_item[period] = positive_values_1 + \
                        str(row_item[period])+positive_values_2
                else:
                    row_item[period] = positive_values_strong_1 + \
                        str(row_item[period])+positive_values_strong_2

            elif float(row_item[period]) == 0:
                if row_item['is_group'] == '':
                    row_item[period] = neutral_values_1 + \
                        str(row_item[period])+neutral_values_2
                else:
                    row_item[period] = neutral_values_strong_1 + \
                        str(row_item[period])+neutral_values_strong_2
            else:
                if row_item['is_group'] == '':
                    row_item[period] = negative_values_1 + \
                        str(row_item[period])+negative_values_2
                else: 
                    row_item[period] = negative_values_strong_1 + \
                        str(row_item[period])+negative_values_strong_2
    return data

def rename_category(data):
    """
    Función: Para renombrar, la primera categoria
    Company por Total Cash Flow

    Args:
        data ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios con data a mostrar en el reporte
        ya procesada.
    """    
    data[0]['name']='Total cash flow'
    return data

def insert_link_to_categories(data, from_date='', to_date=''):
    """
    Función: Agrega link, a cada categoría para genererar 
    el reporte de detalle de flujo de caja

    Args:
        data ([type]): [description]
        from_date (str, optional): [description]. Defaults to ''.
        to_date (str, optional): [description]. Defaults to ''.

    Returns:
        Lista de diccionarios: Lita de dicionarios, con el link para 
        abrir una nueva ventana con el reporte desde JS.
    """    
    for d in data:
        if d['is_group'] != 1 and d['is_group'] != '':
            one_string = '<a target="_blank" onclick="open_detailed_cash_flow_report('
            two_string = ')">'
            three_string = '</a>'
            d['name'] = f"{one_string}'{d['name']}','{from_date}','{to_date}'{two_string}{d['name']}{three_string}"
        
        if d['name'] == 'Uncategorized Inflows' or d['name'] == 'Uncategorized Outflows':
            one_string = '<a target="_blank" onclick="open_detailed_cash_flow_report('
            two_string = ')">'
            three_string = '</a>'
            d['name'] = f"{one_string}'{d['name']}','{from_date}','{to_date}'{two_string}{d['name']}{three_string}"
    return data

# ******************** Fin Logica Process Data ********************

# Para debug
def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
