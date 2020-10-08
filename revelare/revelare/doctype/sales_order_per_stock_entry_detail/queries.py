# Copyright (c) 2020, Si Hay Sistema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
# from frappe.utils import get_datetime, nowdate, nowtime
# from frappe import _
# from frappe.utils import flt


@frappe.whitelist()
def get_items_available_for_sale(item_code):
    """
    Query para obtener info de todos los items disponibles, solo de aquellos
    docs que esten validados y que tengan marcada la opcion disponible para la venta

    Args:
        item_code (str): Codigo item a consultar

    Returns:
        list: Lista Diccionarios, cada diccionario hace referencia a una fila de la DB
    """

    # Por si se formatea la datetime -> DATE_FORMAT(SED.creation, '%Y-%m-%d %H:%m:%s') AS datetime_added

    data = frappe.db.sql(
        f"""
            SELECT SED.parent, SED.item_code, SED.qty AS stock_qty, SED.stock_uom,
            SED.available_for_sale, SED.creation AS datetime_added
            FROM `tabStock Entry Detail` AS SED
            JOIN `tabStock Entry` AS SE ON SE.name = SED.parent
            WHERE SE.docstatus = 1 AND SED.available_for_sale = 1 AND
            SED.item_code = '{item_code}'
        """, as_dict=True
    )

    return data or []
