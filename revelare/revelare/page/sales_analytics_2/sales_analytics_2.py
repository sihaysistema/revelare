#!/usr/local/bin/python
# -*- coding: utf-8 -*-from __future__ import unicode_literals
import frappe
from frappe import _
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

@frappe.whitelist()
def obtenerDatosItem(codigoItem):
    """Funcion para obtener los datos necesarios desde la tabla UOM Conversion Detail e Item"""
    # El if verifica la existencia del dato solicitado, para que sea valido, debe existir y
    # tener un check con la unidad de medidad default en caso no exista
    # devuelve la unidad de medida default del item
    claveItem = str(codigoItem)

    if frappe.db.exists('UOM Conversion Detail', {'parent': claveItem, 'revelare_default_uom_sales_analytics_2': 1}):
        datosItem = frappe.db.get_values('UOM Conversion Detail',
                                         filters={'parent': claveItem, 'revelare_default_uom_sales_analytics_2': 1},
                                         fieldname=['conversion_factor', 'uom'],
                                         as_dict=1)
        return datosItem
    else:
        datosDefaultItem = frappe.db.get_values('Item',
                                                filters={'item_code': claveItem},
                                                fieldname=['stock_uom'],
                                                as_dict=1)
        return datosDefaultItem
