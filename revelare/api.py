# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json

from utils_revelare.clean_data import preparar_data_tabla
from utils_revelare.creator import crear_dn_si
from utils_revelare.creator import validar_configuracion


@frappe.whitelist()
def procesar_data(data):
    '''Funcion recibe la data del front-end parseandola adecuadamente
       para ser procesada

       parametros:
       ----------
       - data (object-array): Contiene informacion de datatable del frontend
    '''
    # Verifica que exista una configuracion valida
    conf_revelare = validar_configuracion()

    if conf_revelare[0] == 1:
        # Carga la data como json
        data_tabla = json.loads(data)

        # Prepara la data y agrupa por numeros de vale
        data_preparada = preparar_data_tabla(data_tabla)

        # Creador de Notas de Entraga y/o Facturas de Venta
        status_dn_si = crear_dn_si(data_preparada, conf_revelare[1])

        return status_dn_si
    
    if conf_revelare[0] == 2:
        return '''Existe mas de una configuracion para revelare, porfavor verifique que exista
        solo una <a href='#Form/Configuration Revelare/<b>arreglar</b></a>'''
    
    if conf_revelare[0] == 3:
        return '''No existe configuracion valida para revelare, porfavor cree o valide
        una nueva configuracion <a href='#Form/Configuration Revelare/<b>arreglar</b></a>'''


@frappe.whitelist()
def obtener_series():
    mis_series = {}

    naming_series = frappe.get_meta("Delivery Note").get_field("naming_series").options or ""
    naming_series = naming_series.split("\n")
    mis_series['delivery_note'] = naming_series

    naming_series_s = frappe.get_meta("Sales Invoice").get_field("naming_series").options or ""
    naming_series_s = naming_series_s.split("\n")
    mis_series['sales_invoice'] = naming_series_s
    #out = naming_series[0] or (naming_series[1] if len(naming_series) > 1 else None)

    return mis_series
