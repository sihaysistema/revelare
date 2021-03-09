# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _, scrub

def execute(filters=None):
    columns = get_columns(filters)
    # data = get_data(filters)
    data = []
    return columns, data

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

    """
    # Genera las columnas en base al rango de fechas
    for dummy, end_date in ranges:
        period = get_period(end_date, filters)

        columns.append({
            "label": _(period),
            "fieldname":scrub(period),
            "fieldtype": "Float",
            "width": 120
        })
    """
    return columns

def get_data(filters):
    data = [{'name':'Hola'},{'name':'Hola'},{'name':'Hola'}]
    data = adding_columns_to_data(data, ranges, filters)
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

def adding_columns_to_data(data, ranges, filters):
    for d in data:
        for from_date, to_date in ranges:
            period = get_period(to_date, filters)
            period = scrub(period)
            d[period] = 0

    return data
