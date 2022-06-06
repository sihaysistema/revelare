# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from datetime import date, datetime, timedelta


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
    first_week = date(year, 1, 1)

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
            dic_date.append({'from_date': from_date, 'to_date': to_date, 'wk': wk, 'year': year, 'dic_name': f'{year} Week{wk}'})
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
    """Funcion que busca una llave en una lista de diccionarios

    Args:
        key_search (str): llave a buscar en la lista de diccionarios
        list_to_search (list): lista de diccionarios a buscar

    Returns:
        int or None: Valor que retornara el indice si lo encuentra o nulo si no lo encuentra
    """

    # Por cada diccionario en la lista
    for item in list_to_search:
        # Si en el objeto existe la llave buscada
        if item.get(key_search, '') != '':
            # Retornamos el indice de dicho objeto
            return list_to_search.index(item)
    else:
        # Si termina el for, retonamos nulo
        return None


def search_list_of_dict_v(value_search, key_to_seach, list_to_search):
    """Funcion que busca un valor y una llave en una lista de diccionarios

    Args:
        value_search (str): Valor a buscar en la list de diccionarios
        key_to_seach (str): Llave a buscar en la lista de diccionarios
        list_to_search (list): Lista de diccionarios donde se buscará

    Returns:
        int or None: Retorna el indice si los encuentra o nulo si no los encuentra
    """
    # Por cada objeto en la lista de diccionarios
    for item in list_to_search:
        # Buscamos la llave que nos pasaron el el objeto
        if item.get(key_to_seach, '') != '':
            # Si existe la llave, buscamos el valor que nos pasaron
            if item.get(key_to_seach) == value_search:
                # Si lo encuentra retornamos el indice de dicho valor
                return list_to_search.index(item)
    # Si no encuentra la lleve o el valor, retorna nulo
    else:
        return None


def search_week_in_range(year, from_date, data_of_date):
    """Funcion que busca los indices dentro de la estrutura de rangos de fechas por semana

    Args:
        year (str): año en el cual se buscara dicho rango de fechas
        from_date (str): fecha donde empieza la semana a buscar
        data_of_date (list): estructura de datos donde se buscara dicha fecha

    Returns:
        (int, int) or None: Indices para acceder a dicha semana en la estructura de rango de fechas
    """
    # Convertimos el año en cadena
    year_ = int(f'{year}')
    # Asignamos los valores de nulo a los indices
    index_1 = None
    index_2 = None
    # Buscamos por cada año
    for year_range in data_of_date:
        # Buscamos por cada semana
        for week in year_range:
            # Si el año y el inicio de semana se encuentran en el rango validado
            if week['year'] == year_ and week['from_date'] == from_date:
                # Asignamos los valores de los indices para poder acceder
                index_2 = year_range.index(week)
                index_1 = data_of_date.index(year_range)
    return index_1, index_2


def is_digit(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_string(value):
    return value.lower().isalpha()
