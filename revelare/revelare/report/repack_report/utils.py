# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from datetime import date, datetime as dt, timedelta
import calendar


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
    first_week = date(year, 1, 1)

    while True:
        # Obtenemos una tupla
        # retorna tupla('año','#semana','#dia')
        data_of_year = dt.isocalendar(first_week)
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
        to_date = dt.strptime(from_date, '%Y-%m-%d') + timedelta(days=6)
        # De tipo Date la pasamos a tipo String
        to_date = to_date.strftime('%Y-%m-%d')

        # Obtenemos el numero de semana de la fecha de inicio bajo el ISO-8601
        week_ = dt.isocalendar(dt.strptime(from_date, '%Y-%m-%d'))
        wk = str(week_[1]).zfill(2)

        if year == week_[0]:
            dic_date.append({'from_date': from_date, 'to_date': to_date, 'wk': wk, 'year': year, 'dic_name': f'Week{wk}'})
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
        from_date = dt.strptime(from_date, '%Y-%m-%d') + timedelta(days=7)

        # Revisamos si la fecha de la fecha de inicio aun esta en el año a obtener el rango de fechas
        year_ = from_date.year

        # Convetirmos la fecha de tipo Date a String
        from_date = from_date.strftime('%Y-%m-%d')

    # Retornamos el rango de fechas
    return dic_date


# Get list of dictionaries with
# name of the month, start and end date for the selected year.
def list_of_ranges_month(flt_year):
    """Retorna la lista de meses dado por el año pasado por parametro

    Args:
        flt_year (int): 2021

    Returns:
        [list]: [
            Lista de diccionarios con campos necesarios para el rango de fechas,
            EJ:
            [{'year':2021, 'month':'01','from_date':2021-01-01', to_date: '2021-01-31', 'dic_name':'2021 month01'}, ...]
            ]
    """
    # año sobre el cual se calcularan las fechas
    year = flt_year
    # Buscamos primer mes del año respecto al ISO-8601
    # Nota: El ISO-8601 es un forma que toma en cuenta el primer lunes de cada año, como primer día de la semana en cada año.
    # en el caso del año 2021 el lunes 04 de enero, es el primer día de la semana 1. el dia 03-01-2021, aun es semana 52 del año 2020
    first_month = date(year, 1, 1)

    while True:
        # Obtenemos una tupla
        # retorna tupla('año','#semana','#dia')
        data_of_year = dt.isocalendar(first_month)
        # Ej: Validate = '2021 week2'
        validate = f'{data_of_year[0]} month{data_of_year[1]}'
        # si el año a validar esta en el string de validacion
        # '2020 week' in '2021 week2'
        if f'{year} month' in validate:
            if data_of_year[2] == 1:
                # Si ya es el mismo año y dia 1, rompemos el ciclo
                break
            else:
                first_month -= timedelta(days=1)
        else:
            # De lo contrario le sumamos un día a la fecha de la primer semana
            first_month += timedelta(days=1)

    # Fecha de inicio, es el primer día de la primer mes de cada año
    from_date = first_month.strftime('%Y-%m-%d')

    year_ = year

    dic_date = []
    while year_ == year:
        to_date = dt.strptime(from_date, '%Y-%m-%d') + timedelta(
            days=calendar.monthrange(year, dt.strptime(from_date, '%Y-%m-%d').month)[1] - 1)
        to_date = to_date.strftime('%Y-%m-%d')
        month_ = dt.strptime(from_date, '%Y-%m-%d').month
        month_name = calendar.month_name[month_]
        if year == data_of_year[0]:
            dic_date.append({'from_date': from_date, 'to_date': to_date, 'month_number': month_, 'month': month_name, 'year': year,
                             'dic_name': f'{year} {month_name}'})
            # 'dic_name': f'{year} {month_name}'})
        else:
            break

        from_date = dt.strptime(from_date, '%Y-%m-%d') + timedelta(
            days=calendar.monthrange(year, dt.strptime(from_date, '%Y-%m-%d').month)[1])

        year_ = from_date.year

        from_date = from_date.strftime('%Y-%m-%d')

    return dic_date


def get_isoYear_start_and_endDate(year='2020'):
    # Buscamos primer semana del año respecto al ISO-8601
    # Nota: El ISO-8601 es un forma que toma en cuenta el primer lunes de cada año, como primer día de la semana en cada año.
    # en el caso del año 2021 el lunes 04 de enero, es el primer día de la semana 1. el dia 03-01-2021, aun es semana 52 del año 2020
    year = int(year)
    first_week = date(year, 1, 1)

    while True:
        # Obtenemos una tupla
        # retorna tupla('año','#semana','#dia')
        data_of_year = dt.isocalendar(first_week)
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

    last_week = date(year, 12, 31)
    while True:
        last_of_year = dt.isocalendar(last_week)
        last_validate = f'{last_of_year[0]} week{last_of_year[1]}'
        if f'{year} week' in last_validate:
            if last_of_year[2] == 7:
                break
            else:
                last_week += timedelta(days=1)
        else:
            last_week -= timedelta(days=1)

    # Fecha de inicio, es el primer día de la primer semana de cada año
    from_date = first_week.strftime('%Y-%m-%d')
    to_date = last_week.strftime('%Y-%m-%d')
    return from_date, to_date
