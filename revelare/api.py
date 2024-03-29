# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

import frappe
from frappe import _
from frappe.utils import nowdate, get_datetime

from revelare.utils_revelare.clean_data import preparar_data_tabla
from revelare.utils_revelare.creator import crear_dn_si, validar_configuracion


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

        # Si el dataframe tiene data
        if data_preparada is not False:
            # Creador de Notas de Entraga y/o Facturas de Venta
            status_dn_si = crear_dn_si(data_preparada, conf_revelare[1])

            return status_dn_si

        # Si el dataframe no tiene data
        else:
            return 'No Data'

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


# ------------- ERRAND TRIP SECTION ------------- #

@frappe.whitelist()
def get_errand_trips():
    """
    Obtains active errandTrips

    Returns:
        list: list of dictionaries
    """
    return frappe.db.get_list('Errand Trip',
        filters={'status_doctype': 'active', 'docstatus': 0},
        fields=['name', 'driver', 'driver_name']
    ) or []


@frappe.whitelist()
def get_errand_trip_stops(name=''):
    """Gets the stops of X errand trip

    Args:
        name (str, optional): Errand Trip `name`. Defaults to ''.

    Returns:
        list: list of dictionaries
    """
    field_child_tbl = ['name', 'parent', 'idx', 'customer', 'requested_time',
                       'actual_arrival', 'document', 'document_type', 'contact_details',
                       'address_details', 'lat', 'lng', 'details',
                       'status', 'driver_comment']

    res = frappe.db.get_list('Errand Trip Stop',
        filters={'parent': name}, fields=field_child_tbl,
        order_by='actual_arrival ASC, requested_time ASC',
    ) or []

    with open("data-errand-trip.json", "w") as f:
        f.write(json.dumps(res, indent=2, default=str))
    return res


@frappe.whitelist()
def complete_trip(parent='', name=''):
    """Assign values to mark as completed

    Args:
        parent (str, optional): Errand Trip `name`. Defaults to ''.
        name (str, optional): Errand Trip Stop `name`. Defaults to ''.

    Returns:
        str: status
    """
    try:
        # Forma 1, sin notificar
        frappe.db.set_value('Errand Trip Stop', {'name': name, 'parent': parent}, {
            'actual_arrival': str(get_datetime()),
            'status': 'Completed'
        })

        # Forma 2, notificando (funciona solo dentro de la clase)
        # trip = frappe.get_doc('Errand Trip Stop', {'name': name, 'parent': parent})
        # trip.db_set('actual_arrival', str(get_datetime()))
        # trip.db_set('status', 'Completed')
        # trip.actual_arrival = str(get_datetime())
        # trip.status = 'Completed'
        # trip.notify_update()
        # trip.save()
        return "Completed"

    except:
        return frappe.get_traceback()

@frappe.whitelist()
def update_driver_comment(parent='', name='', comment=''):
    """Updates comments entered by the author

    Args:
        parent (str, optional): Errand Trip `name`. Defaults to ''.
        name (str, optional): Errand Trip Stop `name`. Defaults to ''.
        comment (str, optional): Driver's comment. Defaults to ''.

    Returns:
        str: status
    """
    frappe.db.set_value('Errand Trip Stop', {'name': name, 'parent': parent}, {
        'driver_comment': str(comment)
    })

    return "Updated comment"


@frappe.whitelist()
def undo_status_trip(parent='', name=''):
    """Reactivate the trip

    Args:
        parent (str, optional): Errand Trip `name`. Defaults to ''.
        name (str, optional): Errand Trip Stop `name`. Defaults to ''.

    Returns:
        str: status
    """
    frappe.db.set_value('Errand Trip Stop', {'name': name, 'parent': parent}, {
        'actual_arrival': None,
        'status': 'Active'
    })

    return "Trip has been activated again"


@frappe.whitelist()
def change_status_errand_trip(name):
    try:
        frappe.db.set_value('Errand Trip', {'name': name}, {
            'status_doctype': 'Errand Trip Completed',
        })
        return True

    except:
        return frappe.get_traceback()

# ------------- END ERRAND TRIP SECTION ------------- #


# DATOS PARA PAGE HISTORIAL VOLUMEN ANALYSIS
@frappe.whitelist()
def get_data_to_select():
    companies = frappe.db.get_list('Company', pluck='name')
    fiscal_years = frappe.db.get_list('Fiscal Year', pluck='name')

    return companies, fiscal_years

@frappe.whitelist()
def get_items():
    return frappe.db.get_list('Item', filters={
        'is_sales_item': 1
    }, fields=['name', 'item_name']) or []
