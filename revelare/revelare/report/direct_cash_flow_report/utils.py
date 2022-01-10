# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import calendar
import json
from datetime import date, datetime, time, timedelta

import frappe
from dateutil.relativedelta import relativedelta
from frappe import _, _dict, scrub
from frappe.utils import cint, flt, getdate


def get_period_date_ranges(filters):
    """
    Función: Obtiene el periodo en base al rango de fechas

    Args:
        filters ([type]): [description]

    Returno:
        Lista de listas: Listas de listas, con dos elementos. Cada sublista
        con la fecha inicial y la fecha final del rango de fechas seleccionado.
    """

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


#********* Estas funciones ya no las utilizamos por que ahora nos guíamos por medio de la longitud del la lista. ******
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
