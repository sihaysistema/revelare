# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json

import frappe
import pandas as pd
from frappe import _, scrub


def execute(filters=None):
    return get_columns(filters), get_data(filters)

def get_columns(filters):
    '''Retorna las columnas a utilizar en el reporte'''

    columns = [
        {
            "label": _("ID"),
            "fieldname": "name_url",
            "fieldtype": "Data",
            "width": 365
        },
        {
            "label": _("Amount"),
            "fieldname": "amount",
            "fieldtype": "Data"
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

    if filters.category != None: # Si definimos la categoria.
        #**************** Procesamos los datos *****************************
        payments_entry = set_payment_entry(filters.from_date, filters.to_date, filters.category)
        journal_entry = set_journal_entry(filters.from_date, filters.to_date, filters.category)

        data = [] # Definimos data a mostrar vacía
        for pay in payments_entry: # Agregamos pyments_entry

            data.append({
                'name':pay['name'],
                'amount':pay['amount'],
                'type':'payment_entry',
                'name_url':pay['name_url']
            })

        for journal in journal_entry: # Agregamos journal_entry

            data.append({
                'name':journal['name'],
                'amount':journal['amount'],
                'type':'journal_entry',
                'name_url':journal['name_url']
            })

        data = rename_categories(data) # Agregamos link a cada item de la data
        # dicToJSON('data', data)
        # dicToJSON('filters', filters)
        data = formating_data_before_print(data, filters.category)

    else: # Mostramos el reporte vacío
        data = [{'name_url':'','amount':0}]

    return data

#Obteniendo pagos por categorias
def set_payment_entry(from_date, to_date, category):
    """
    Obtiene todos los pagos, que tengan que ver
    con flujo de efectivo.

    Returns:
        lista de diccionarios: [{cuenta, cagoria, ...},{cuenta, cagoria, ...}]
    """

    # Para filtrar si un documento esta validado o no, el digito debe estar como string
    # Ej: docstatus '1'
    payments = []
    if category != 'D.2 - Unicategorized Payments' and category != 'D.1 - Uncategorized Receipts':

        payments = frappe.db.sql(f'''
            SELECT name as name_url, paid_from, paid_to, posting_date, inflow_component,
            outflow_component, paid_amount AS amount, payment_type
            FROM `tabPayment Entry`
            WHERE inflow_component = '{category}' OR outflow_component = '{category}' AND payment_type != 'Internal Transfer'
            AND posting_date BETWEEN '{from_date}' AND '{to_date}' AND docstatus = 1 ''', as_dict=True)
    else:

        payments = frappe.db.sql(f'''
            SELECT name as name_url, paid_from, paid_to, posting_date, inflow_component,
            outflow_component, paid_amount AS amount, payment_type
            FROM `tabPayment Entry`
            WHERE inflow_component IS NULL AND outflow_component IS NULL AND payment_type != 'Internal Transfer'
            AND posting_date BETWEEN '{from_date}' AND '{to_date}' AND docstatus = 1 ''', as_dict=True)

    for item in payments:

        if item['payment_type'] == 'Receive':
            item['name'] =item['paid_to']

        elif item['payment_type'] == 'Pay':
            item['name'] = item['paid_from']
            item['amount'] = item['amount'] * -1

    return payments or []

# ******************** Inicio Logica Jounal Entry ********************

def set_journal_entry(from_date, to_date, category):
    """
    Función: Selecciona todas las journal entry,
    dependiendo de la categoria que se envie por parametro

    Args:
        from_date ([type]): [description]
        to_date ([type]): [description]
        category ([type]): [description]

    Returns:
        Lista de diccionarios: Lista de diccionarios para ser formatea al momento de enviar dicho valor al reporte
    """
    journal, undefined = get_journal_entry(from_date, to_date, category)

    if category == 'Uncategorized Outflows' or category == 'Uncategorized Inflows':
        journal_indefinite = []

        for undef in undefined:
            undef['posting_date'] = str(undef['posting_date'])

            if category == 'Uncategorized Inflows' and undef['debit'] > 0.0:
                undef['amount'] = undef['debit']
                journal_indefinite.append({
                    'name': undef['lb_name'],
                    'amount': undef['amount'],
                    'type': undef['account_type'],
                    'name_url': undef['url_name']
                })

            elif category == 'Uncategorized Outflows' and undef['credit'] > 0.0:
                undef['amount'] = (undef['credit'] * -1)

                journal_indefinite.append({
                    'name': undef['lb_name'],
                    'amount': undef['amount'],
                    'type': undef['account_type'],
                    'name_url': undef['url_name']
                })

        return journal_indefinite

    else:
        journal_entry = []

        if journal.get(category, False):
            journal = journal.get(category, False)

            for j in journal:
                journal_entry.append({
                    'lb_name': j['lb_name'],
                    'amount': j['amount'],
                    'type': j['account_type'],
                    'name_url': j['url_name']
                })
            return journal_entry

        else:
            return []


# es-GT: Obteniendo entradas de diario por categorias
def get_journal_entry(start_date, end_date, category):
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
    # journal_entry = get_query_journal_entry(start_date, end_date, category)
    journal_entry = get_query_journal_entry(start_date, end_date)

    journal_undefined_categories = []
    if journal_entry:
        #------------ Inicio Polizas definidas ------------
        df_journal = pd.DataFrame(json.loads(json.dumps(journal_entry))) # Pasamos data a Pandas
        df_journal = df_journal.fillna("")
        df_journal_categories = df_journal.query("inflow_component != '' or outflow_component != ''") # Obtenemos los componente definidos

        journal_categories = df_journal_categories.to_dict(orient='records')
        for journal in journal_undefined_categories:
            if journal.get('amount','') == '':

                if journal.get('debit', None) != 0:
                    journal['amount'] = journal.get('debit')

                elif journal.get('credit', None) != 0:
                    journal['amount'] = journal.get('credit')

        journal_entry = {}
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

        #------------ Fin Polizas definidas ------------

        df_journal_undefined_categories = df_journal.query("inflow_component == '' and outflow_component == ''")# obtenemos los componenete indefinidos
        journal_undefined_categories = df_journal_undefined_categories.to_dict(orient='records')

    return journal_entry, journal_undefined_categories

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
        journal_ = journal.values()
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
            pass
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
            journal['url_name']: get_accounts_for_journal_entries(journal['url_name'], journal['posting_date'])
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
                        SELECT JE.name AS url_name, JE.posting_date
                        FROM `tabJournal Entry` AS JE
                        INNER JOIN `tabJournal Entry Account` AS JEC
                        ON JEC.parent = JE.name AND JE.docstatus = 1 AND JE.posting_date BETWEEN '{from_date}' AND '{to_date}'
                        WHERE JEC.account_type = 'Bank' OR JEC.account_type = 'Cash' GROUP BY JEC.name;
                        ''', as_dict=True)
                        #AND (JEC.inflow_component = '{category}' OR JEC.outflow_Component = '')
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
        c['url_name'] = journal

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
    if len(journal_flatten) < 3:
        count = 0
        for journal_f in journal_flatten:
            if journal_f['account_type'] == 'Bank' or journal_f['account_type'] == 'Cash':
                count += 1
        if count == 1:
            return True
        else:
            return False
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
    journal_entry['D.1 - Uncategorized Receipts'] = []
    journal_entry['D.2 - Uncategorized Payments'] = []
    for category in undefined:
        if category['debit'] > 0:
            category['amount'] =  category['debit']
            if (journal_entry.get('D.1 - Uncategorized Receipts', None) != None):
                journal_entry['D.1 - Uncategorized Receipts'].append(category)
            else:
                journal_entry['D.1 - Uncategorized Receipts'] = category

        elif category['credit'] > 0:
            category['amount'] =  category['credit']
            if (journal_entry.get('D.2 - Uncategorized Payments', None) != None):
                journal_entry['D.2 - Uncategorized Payments'].append(category)
            else:
                journal_entry['D.2 - Uncategorized Payments'] = category
    return journal_entry

# ******************** Fin Logica Jounal Entry ********************


def rename_categories(data, from_date='', to_date=''):
    for d in data:
        one_string = '<a target="_blank" onclick="open_one_tab('
        two_string = ')">'
        three_string = '</a>'
        d['name_url'] = f"{one_string}'{d['name_url']}','{d['type']}'{two_string}{d['name_url']}{three_string}"
        # d['name'] = f"{one_string}'{d['name_url']}','{d['type']}'{two_string}{d['name']}{three_string}"
    return data

def formating_data_before_print(data, category):
    amount_total = 0 # Sumamos el valor de todos los items
    for d in reversed(data):
        amount_total += d['amount']


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

    if amount_total > 0:
        amount_total = str(amount_total)
        data.insert(0,{ # Insertamos dicha suma en la primera fila del reporte
                        'name_url': category,
                        'amount':str(positive_values_strong_1+amount_total+positive_values_strong_2)
                    })
    elif amount_total < 0:
        amount_total = str(amount_total)
        data.insert(0,{ # Insertamos dicha suma en la primera fila del reporte
                        'name_url': category,
                        'amount':str(negative_values_strong_1+amount_total+negative_values_strong_2)
                    })
    else:
        amount_total = str(amount_total)
        data.insert(0,{ # Insertamos dicha suma en la primera fila del reporte
                        'name_url': category,
                        'amount':str(neutral_values_strong_1+amount_total+neutral_values_strong_2)
                    })

    return data

# Para debug
def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
        f.close()

def escribe(texto):
    with open ('log.txt','a') as f:
        f.write(f'{texto}')
        f.close()
