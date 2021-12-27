# Copyright (c) 2020, Si Hay Sistema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
from datetime import datetime, timedelta

import frappe
import numpy as np
from frappe import _, _dict, scrub
from frappe.utils import cstr, flt, nowdate
from datetime import date, datetime, time, timedelta

def get_range_of_date(filters):
    """Funcion que obtiene el rango de fechas dado por el año que se le pase por parametro en el filtro

    Args:
        filters (year): 2021

    Returns:
        [list]: [[{'year':2021, 'wk':'01','from_date':2021-01-04', to_date: '2021-01-10', 'dic_name':'2021 week01'}]]
    """
    # Año actual
    current_year = datetime.today().year
    # Año desde el que se va a calcular
    flt_year = int(filters.year)

    data = []
    # Mientras el año del filtro sea menor obtenemos el listado de fechas
    while flt_year <= current_year:
        data.append(list_of_ranges_date(flt_year))
        # le sumamos un año al año desde el que se calculara
        flt_year += 1

    return data

def list_of_ranges_date(flt_year):
    """Retorna la lista de semanas dado por el año pasado por parametro

    Args:
        flt_year (int): 2021

    Returns:
        [list]: [
            Lista de diccionarios con campos necesarios para el rango de fechas,
            EJ:
            [{'year':2021, 'wk':'01','from_date':2021-01-04', to_date: '2021-01-10', 'dic_name':'2021 week01'}, ...]
            ]
    """
    # año sobre el cual se calcularan las fechas
    year = flt_year
    # Buscamos primer semana del año respecto al ISO-8601
    # Nota: El ISO-8601 es un forma que toma en cuenta el primer lunes de cada año, como primer día de la semana en cada año.
    # en el caso del año 2021 el lunes 04 de enero, es el primer día de la semana 1. el dia 03-01-2021, aun es semana 52 del año 2020
    first_week = date(year,1,1)

    while True:
        # Obtenemos una tupla
        # retorna tupla('año','#semana','#dia')
        data_of_year = datetime.isocalendar(first_week)
        # Ej: Validate = '2021 week2'
        validate = f'{data_of_year[0]} week{data_of_year[1]}'
        # si el año a validar esta en el string de validacion
        # '2020 week' in '2021 week2'
        if f'{year} week' in validate:
            if data_of_year[2] == 1:
                # Si ya es el mismo año y dia 1, rompemos el ciclo
                break
            else:
                first_week -= timedelta(days=1)
        else:
            # De lo contrario le sumamos un día a la fecha de la primer semana
            first_week += timedelta(days=1)

    # Fecha de inicio, es el primer día de la primer semana de cada año
    from_date = first_week.strftime('%Y-%m-%d')

    # Año a comparar
    year_ = year

    # Diccionario a retornar
    dic_date = []
    # Mientras year_ sea igual que year
    while year_ == year:
        # La fecha fin, sera el primer día (from_date) + 6 días
        to_date = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=6)
        # De tipo Date la pasamos a tipo String
        to_date = to_date.strftime('%Y-%m-%d')

        # Obtenemos el numero de semana de la fecha de inicio bajo el ISO-8601
        week_ = datetime.isocalendar(datetime.strptime(from_date, '%Y-%m-%d'))
        wk = str(week_[1]).zfill(2)

        if year == week_[0]:
            dic_date.append({'from_date':from_date, 'to_date':to_date, 'wk':wk, 'year':year, 'dic_name':f'{year} Week{wk}'})
        else:
            break
        """
        # Fecha a evualar sera la fecha de inicio para que no se pase de la fecha actual
        eval_date = datetime.strptime(from_date, '%Y-%m-%d')

        # Fecha actual.
        date_now = datetime.today()

        if eval_date < date_now:
            # Si la fecha a evaluar es menor, generamos el diccionario con el rango de fechs y el nombre del diccionario por # de semana
            dic_date.append({'from_date':from_date, 'to_date':to_date, 'wk':wk, 'year':year, 'dic_name':f'{year} Week{wk}'})
        else:
            # De lo contrario nos salimos del ciclo
            break
        """

        # Agregamos 7 dias a la fecha de inicio
        from_date = datetime.strptime(from_date, '%Y-%m-%d') + timedelta(days=7)

        # Revisamos si la fecha de la fecha de inicio aun esta en el año a obtener el rango de fechas
        year_ = from_date.year

        # Convetirmos la fecha de tipo Date a String
        from_date = from_date.strftime('%Y-%m-%d')

    # Retornamos el rango de fechas
    return dic_date


def search_list_of_dict_k(key_search, list_to_search):
    for item in list_to_search:
        if item.get(key_search,'') != '':
            return list_to_search.index(item)
    else:
        return None
