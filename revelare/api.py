# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json

from utils_revelare.clean_data import preparar_data_tabla
from utils_revelare.creator import crear_dn_si


@frappe.whitelist()
def procesar_data(data):
    '''Funcion recibe la data del front-end parseandola adecuadamente
       para ser procesada

       parametros:
       ----------
       - data (object-array): Contiene informacion de datatable del frontend
    '''

    # Carga la data como json
    data_tabla = json.loads(data)

    # Prepara la data y agrupa por numeros de vale
    data_preparada = preparar_data_tabla(data_tabla)

    # Creador de Notas de Entraga y/o Facturas de Venta
    status_dn_si = crear_dn_si(data_preparada)

    return status_dn_si


@frappe.whitelist()
def obtener_clientes():
   pass


@frappe.whitelist()
def obtener_items():
   pass


@frappe.whitelist()
def obtener_series():
   pass