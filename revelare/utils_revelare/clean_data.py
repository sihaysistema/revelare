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
    # data_dn = open(frappe.get_app_path("revelare",
    #                                 "utils_revelare",
    #                                 "data_prueba.json")).read()

    data_dn = json.dumps(data_tabla)

    # Declaracion DataFrame
    df = pd.read_json(data_dn, orient='columns')

    # Filtrado por vales
    # Filtrara todas las filas que contengan un valor en la columna numero
    filtrado_vale = df.loc[df['numero'] != '']

    # VERIFICACION: .empty returna true si el dataframe esta vacio, y 
    # true si tiene data
    if filtrado_vale.empty is False:
        # Obtiene los datos de la columna numero que hace referencia a los vales,
        # filtrando los duplicados
        vales = list(set(list(filtrado_vale['numero'])))
        # Ordena de menor a mayor
        vales.sort()

        # Crea estructura en formato json/dict para mejor manejo
        mis_vales = {}
        for vale in vales:
            vale_x = (filtrado_vale.loc[filtrado_vale['numero'] == vale]).to_json(orient='records')
            mis_vales[str(vale)] = json.loads(vale_x)

        vales_dn_si = json.dumps(mis_vales)

        # Retorna un tupla con un diccionario con los vales
        # y un lista de los vales encontrados
        return vales_dn_si, vales

    # Si el dataframe esta vacio
    else:
        return False
