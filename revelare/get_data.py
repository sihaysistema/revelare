#!/usr/local/bin/python
# -*- coding: utf-8 -*-from __future__ import unicode_literals
import frappe
from frappe import _
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@frappe.whitelist()
def mostrarData(datoFront):
    """Funcion para obtener los datos necesarios desde la tabla UOM Conversion Detail"""
    # El if verifica la existencia del dato solicitado, en caso no exista
    # devuelve el mensaje 'No existe'
    if frappe.db.exists('UOM Conversion Detail', {'parent': datoFront, 'revelare_default_uom_sales_analytics_2': 1}):
        return '{} Si tiene check unidad defautl'.format(datoFront)
    else:
        return '{} no tiene unidad default'.format(datoFront)
