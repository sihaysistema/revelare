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
from revelare.revelare.report.direct_cash_flow_report_copy.queries import (
    get_accounts_for_journal_entries, get_categories, get_categories_child,
    get_list_journal_entries, get_query_payment_entry)
from revelare.revelare.report.direct_cash_flow_report_copy.utils import (
    all_cash_or_bank_accounts, get_period, get_period_date_ranges,
    there_are_different_accounts, there_is_only_one_cash_flow_account)
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
    columns.append({
        "label": _('Total Amount'),
        "fieldname":'total_amount',
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
    # categories_child = get_categories_child()
    journal_entry = {}
    payment_entry = {}

    start_date = filters.from_date
    end_date = filters.to_date

    journal_entry = get_journal_entry(start_date, end_date)
    payment_entry = get_payment_entry(start_date, end_date)

    # Uniendo journal_entry y payment_entry
    data_by_categories = merging_dictionaries(journal_entry,payment_entry)
    if data_by_categories == {}:
        return {'name': _('no se encontraron polizas ni entradas de pago en el año')}
    data_and_categories = formatting_data(data_by_categories, categories_by_name, filters)
    # Agregando datos a las columnas vacías
    data = adding_columns_to_data(data_and_categories, ranges, filters)
    # Sumando la data del reporte
    data = accumulate_values_into_parents(data, ranges, filters)
    # Sumando cuentas hijas
    data = add_values_of_sub_accounts(data)
    data = add_total_column(data)

    data[0]['name']='Total cash flow'

    data = insert_link_to_categories(data, filters.from_date,filters.to_date)

    # Agregando color a cada dato
    data = adding_color_to_data(data, ranges, filters)

    # TODO: Cuando se maneje consolidado el flujo de caja se va a indicar el nombre de la compania en esta celda
    # Y se le agregara un totalizador


    return data

# ******************** Inicio Logica de Rangos de Fecha ********************

def filter_categories(categories):
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
        categories_by_name[d['name']] = d

        parent_children_map.setdefault(d['parent_direct_cash_flow_component'] or 'root', []).append(d)

    def add_to_list(parent, level):
        children = parent_children_map.get(parent) or []

        for child in children:
            child['indent'] = level
            add_to_list(child['name'], level + 1)
    add_to_list('root', 0)

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
    journal_entry = get_journal_entry_format(start_date, end_date)
    # Pasando a Pandas
    df_journal = pd.DataFrame(json.loads(json.dumps(journal_entry)))
    df_journal = df_journal.fillna("")

    # Obtenemos los componente definidos
    journal_entry = {}
    df_journal_categories = df_journal
    df_journal_categories = df_journal.query("inflow_component != '' or outflow_component != ''")

    journal_categories = df_journal_categories.to_dict(orient='records')
    for journal in journal_categories:
        if journal['inflow_component'] != '':
            journal_entry.setdefault(journal['inflow_component'], []).append(journal)

        elif journal['outflow_component'] != '':
            journal_entry.setdefault(journal['outflow_component'], []).append(journal)

    # obtenemos los componenete indefinidos
    df_journal_undefined_categories = df_journal.query("inflow_component == '' and outflow_component == ''")

    journal_undefined_categories = df_journal_undefined_categories.to_dict(orient='records')

    journal_undefined = {}
    for journal in journal_undefined_categories:
        if journal.get('debit', 0) != 0:
            journal['amount'] = journal.get('debit')
            journal_entry.setdefault('D.1 - Uncategorized Receipts', []).append(journal)


        elif journal.get('credit', 0) != 0:
            journal['amount'] = journal.get('credit')
            journal_entry.setdefault('D.2 - Uncategorized Payments', []).append(journal)

    journal_entry = [ {k:v} for k, v in journal_entry.items()]

    return journal_entry

def get_journal_entry_format(from_date, to_date):
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
    if individual_entries != []:
        for journal in individual_entries: # por cada poliza
            journal_flatten = [] # Aplanamos el array
            journal_ = journal.values()
            for j in journal_:

                for item in j:# Accedemos hasta el diccionario
                    journal_flatten.append(item)# Agregamos la cuenta a la poliza
            if there_is_only_one_cash_flow_account(journal_flatten): # si es caso 1
                new_journal_entry.append(journal_flatten[0]) # lo agregamos a la data

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
    else:
        return []
    for journal in new_journal_entry:
        journal['posting_date'] = journal['posting_date'].strftime('%Y-%m-%d')
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
    individual_entries = {}

    for journal in list_journal_entries:
        individual_entries.setdefault(journal['url_name'] or None, []).append(journal)

    individual_entries = [ {k:v} for k, v in individual_entries.items()]

    return individual_entries

# ******************** Fin Logica Jounal Entry ********************

# ******************** Inicio Logica Payment Entry ********************

def get_payment_entry(from_date, to_date):
    payment_entry = get_query_payment_entry(from_date, to_date)
    if payment_entry != []:
        df_payment = pd.DataFrame(json.loads(json.dumps(payment_entry)))
        # obtenemos los componenete indefinidos
        df_payment = df_payment.fillna("")
        df_payment_undefined_categories = df_payment.query("inflow_component == '' and outflow_component == '' and payment_type != 'Internal Transfer'")
        payment_undefined_categories = df_payment_undefined_categories.to_dict(orient='records')

        # Obtenemos los componente definidos
        df_payment_categories = df_payment.query("inflow_component != '' or outflow_component != ''")

        payment_categories = df_payment_categories.to_dict(orient='records')
        payment_entry = payment_categories

        payments = {}
        for payment in payment_categories:
            if payment['inflow_component'] != '':
                payments.setdefault(payment['inflow_component'], []).append(payment)

            elif payment['outflow_component'] != '':
                payments.setdefault(payment['outflow_component'], []).append(payment)

        payments = [ {k:v} for k, v in payments.items()]

        for d in payments:
            for item in d.values():
                if item[0]['payment_type'] == 'Receive':
                    item[0]['lb_name'] = item[0]['paid_to']
                elif item[0]['payment_type'] == 'Pay':
                    item[0]['lb_name'] = item[0]['paid_from']

        for d in payment_undefined_categories:
            if d['payment_type'] == 'Receive':
                d['lb_name'] = d['paid_to']
                d['inflow_component'] = 'D.1 - Uncategorized Receipts'

            elif d['payment_type'] == 'Pay':
                d['lb_name'] = d['paid_from']
                d['outflow_component'] = 'D.2 - Uncategorized Payments'

        payment_undefined = {}
        for d in payment_undefined_categories:
            if d['inflow_component'] != '':
                payment_undefined.setdefault(d['inflow_component'], []).append(d)

            elif d['outflow_component'] != '':
                payment_undefined.setdefault(d['outflow_component'], []).append(d)

        payment_undefined = [ {k:v} for k, v in payment_undefined.items()]

    else:
        return [], []
    payments += payment_undefined

    return payments

# ******************** Fin Logica Payment Entry ********************

# ******************** Inicio Logica Process Data ********************

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
    if journal_entry != []:
        for category in  journal_entry:
            for element in list(category.values())[0]:
                data.setdefault(list(category.keys())[0], []).append(element)

    if payment_entry != []:
        for category in payment_entry:
            for element in list(category.values())[0]:
                data.setdefault(list(category.keys())[0], []).append(element)

    return data

def formatting_data(data_by_categories, categories_by_name, filters):
    """
    Función: Normaliza los datos en una sola lista de diccionarios Devuelve los datos con el siguiente formato.
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
        data_by_categories ([type]): [description], categories_by_name ([type]): [description], filters ([type]): [description]

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
                    'amount' : items['amount']
                    })

    return categories_and_data

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
                                if cash_effect == 'Inflow' or (cash_effect == 'Group' and  dictionary["name"] == 'D.1 - Uncategorized Receipts'):
                                    dictionary[period] += item.get(period)

                                elif cash_effect == 'Outflow' or (cash_effect == 'Group' and  dictionary["name"] == 'D.2 - Uncategorized Payments'):
                                    # haciendo negativo el hijo
                                    item[period] = (item.get(period)*-1)
                                    dictionary[period] += item.get(period)



                            except:


                                if cash_effect == 'Inflow' or (cash_effect == 'Group' and  dictionary["name"] == 'D.1 - Uncategorized Receipts'):
                                    dictionary[period] = item.get(period)

                                elif cash_effect == 'Outflow' or (cash_effect == 'Group' and  dictionary["name"] == 'D.2 - Uncategorized Payments'):
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

                    # Buscamos en toda la lista, el componente padre
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
    """ Aquí si funcionaba
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
    """
    new_datalist = [] # Creamos una nueva lista
    for element in data: # Recorremos la lista anterior
        if len(new_datalist) != 0: # Verificamos si la lista ya tiene algún elemento
            add = True # Inicialiamos un booleano para validar si agrega

            for new_element in new_datalist: # Recorremos la lista nueva
                if new_element.get('name', None) == element['name'] and \
                   new_element.get('parent_direct_cash_flow_component', None) == element['parent_direct_cash_flow_component']: # Verificamos que sea la misma cuenta y componente

                    for key, value in new_element.items(): # Recorremos los valores de nuevo elemento
                        if key != 'name' and key != 'posting_date' and key != 'cash_effect' and key != 'indent' and key  != 'amount' and \
                           key != 'parent_direct_cash_flow_component' and key != 'is_group': # Eliminamos los valores, que no son numericos

                            new_element[key] = new_element[key] + element[key] # Sumamos el elemento retpetido con el elemento base
                            # new_element = Elemento base; element = Elemento repetido

                    add = False # Si esta repetido, no se grega

            if add: # Validamos si agregamos
                new_datalist.append(element)

        else: # Si la lista esta vacía entonces agreamos el elemento
            new_datalist.append(element)

    return new_datalist

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
                d[period] = d.get('amount', 0)
            else:
                d[period] = 0

    return data

def add_total_column(data):
    # Recorremos la data fila por fila
    for row in data:
        total_sum = 0
        for element in row.items():
            # leemos las llaves de los diccionarios y comparamos
            exclude = ['name', 'parent', 'cash_effect', 'is_group', 'indent', 'amount', 'parent_direct_cash_flow_component', 'posting_date']
            # Eliminamos llaves que no tengan que ver con el rango de tiempo
            if element[0] not in exclude:
                # Sumamos cada columna
                total_sum += float(element[1])
        row['total_amount'] = total_sum
    return data

def adding_color_to_data(data, ranges, filters):
    # dicToJSON('data', data)
    # dicToJSON('ranges', ranges)
    # dicToJSON('filters', filters)
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

    # Obtenemos cada fila de la data
    for row_item in data:

        for keys in row_item:
            # Validamos por cada llave de la fila
            exclude = ['name', 'posting_date', 'parent_direct_cash_flow_component', 'cash_effect', 'is_group', 'indent', 'amount']
            # Si no se incluye en la variable de exclusiones
            if keys not in exclude:
                # Convertirmos el valor a float de dos desimales
                row_item[keys] = float("{:.2f}".format(float(row_item[keys])))

                # Por cada fila le agregara un color dependiendo del valor
                if row_item[keys] > 0:
                    if row_item['is_group'] == '':
                        row_item[keys] = positive_values_1 + str(row_item[keys])+positive_values_2
                    else:
                        row_item[keys] = positive_values_strong_1 + str(row_item[keys])+positive_values_strong_2
                elif row_item[keys] == 0:
                    if row_item['is_group'] == '':
                        row_item[keys] = neutral_values_1 + str(row_item[keys])+neutral_values_2
                    else:
                        row_item[keys] = neutral_values_strong_1 + str(row_item[keys])+neutral_values_strong_2
                else:
                    if row_item['is_group'] == '':
                        row_item[keys] = negative_values_1 + str(row_item[keys])+negative_values_2
                    else:
                        row_item[keys] = negative_values_strong_1 + str(row_item[keys])+negative_values_strong_2
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
            one_string = '<a onclick="open_detailed_cash_flow_report('
            two_string = ')">'
            three_string = '</a>'
            d['name'] = f"{one_string}'{d['name']}','{from_date}','{to_date}'{two_string}{d['name']}{three_string}"

        undefined = ['D.2 - Uncategorized Payments', 'D.1 - Uncategorized Receipts']
        if d['name'] in undefined:
            one_string = '<a onclick="open_detailed_cash_flow_report('
            two_string = ')">'
            three_string = '</a>'
            d['name'] = f"{one_string}'{d['name']}','{from_date}','{to_date}'{two_string}{d['name']}{three_string}"
    return data

# ******************** Fin Logica Process Data ********************

# Para debug
def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
