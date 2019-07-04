# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

import json
import pandas as pd


def preparar_data_tabla(data_tabla):
    '''Funcion encargada de preparar la data con la ayuda de pandas, filtra y agrupa
       en base al numero de vales encontrados
    '''

    # Data dummy prueba
    data_dn = json.loads(open(frappe.get_app_path("revelare",
                                                  "utils_revelare",
                                                  "data_prueba.json")).read())

    # Declaracion DataFrame
    df = pd.read_json(data_dn, orient='columns')

    # Filtrado por vales
    # Filtrara todas las filas que contengan un valor en la columna numero
    filtrado_vale = df.loc[df['numero'] != '']

    # Obtiene los datos de la columna numero que hace referencia a los vales,
    # filtrando los duplicados
    vales = list(set(list(filtrado_vale['numero'])))
    # Ordena de menor a mayor
    vales.sort()

    mis_vales = []
    for vale in vales:
        # Para cada vale creara un objeto (diccionario)
        mi_vale = {}

        # Crea un array de objetos, donde cada objeto son todas las filas 
        # con el mismo numero de vale
        vale_x = (filtrado_vale.loc[filtrado_vale['numero'] == vale]).to_json(orient='records')
        mi_vale[str(vale)] = json.loads(vale_x)

        mis_vales.append(mi_vale)

    vales_dn_si = json.dumps(mis_vales)

    return vales_dn_si
