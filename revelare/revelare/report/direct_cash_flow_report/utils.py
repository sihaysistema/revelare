# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import calendar
import json
from datetime import date, datetime, time, timedelta

import frappe
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
