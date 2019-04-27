# Copyright (c) 2019, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _, scrub

def execute(filters=None):
    # Array que contendra n diccionarios donde cada diccionario
    # es una fila
    data = []

    columns = get_columns()

    # Si se selecciona un cliente en el filtro
    if (filters.customer):
        datos = get_specific_data(filters)
    else:
        datos = get_all_data(filters)

    # Prepara la data para ser adaptada
    data_preparada = prepare_data(datos)
    data.extend(data_preparada)
    # data.append({})
    data.extend(add_total_row(data_preparada))

    return columns, data


def get_columns():
    '''Retorna las columnas que conforman el reporte'''

    columns = [
        {
            "label": _("Identificador"),
            "fieldname": "identificador",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Fecha"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Cliente"),
            "fieldname": "cliente",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "label": _("Codigo del Producto"),
            "fieldname": "codigo_producto",
            "fieldtype": "Link",
            "options": "Item",
            "width": 100
        },
        {
            "label": _("Tarifa de la lista de precios"),
            "fieldname": "tarifa_lista",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("Monto"),
            "fieldname": "monto",
            "fieldtype": "Currency",
            "width": 100
        },
        {
            "label": _("UOM"),
            "fieldname": "uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 90
        },
        {
            "label": _("DIESEL"),
            "fieldname": "diesel",
            "fieldtype": "Float",
            "width": 80
        },
        {
            "label": _("REGULAR"),
            "fieldname": "regular",
            "fieldtype": "Float",
            "width": 80
        },
        {
            "label": _("SUPER"),
            "fieldname": "super",
            "fieldtype": "Float",
            "width": 80
        }
    ]

    return columns


def get_all_data(filters):
    '''Retorna todas las notas de entrega que se encuentren en el rango
       seleccionado
    '''

    delivery_note = frappe.db.sql('''SELECT posting_date, numero_vale_cliente,
                                            numero_vale_gaseco,
                                            name, customer_name, customer 
                                    FROM `tabDelivery Note`
                                    WHERE posting_date
                                    BETWEEN %(fecha_inicio)s AND %(fecha_final)s
                                    AND company=%(compa)s''', 
                                    {'fecha_inicio': str(filters.from_date),
                                     'fecha_final': str(filters.to_date),
                                     'compa': str(filters.company)}, as_dict=True)

    return delivery_note


def get_specific_data(filters):
    '''Retorna notas de entrega que se encuentren en el rango seleccionado
       y que pertenezcan a cliente seleccionado en el filtro
    '''

    delivery_note = frappe.db.sql('''SELECT posting_date, numero_vale_cliente,
                                            numero_vale_gaseco,
                                            name, customer_name, customer
                                    FROM `tabDelivery Note`
                                    WHERE posting_date
                                    BETWEEN %(fecha_inicio)s AND %(fecha_final)s
                                    AND customer_name=%(cliente)s AND company=%(compa)s''', 
                                    {'fecha_inicio': str(filters.from_date),
                                     'fecha_final': str(filters.to_date),
                                     'cliente': str(filters.customer),
                                     'compa': str(filters.company)}, as_dict=True)

    return delivery_note


def get_data_item(vale):
    '''Obtiene informacion de n items de la nota de entrega'''

    delivery_note_item = frappe.db.get_values('Delivery Note Item',
                                        filters={'parent': vale},
                                        fieldname=['item_code', 'qty', 'amount', 'uom',
                                                  'rate'], as_dict=1)

    return delivery_note_item


def prepare_data(data_delivery_note):
    '''Prepara la data para que se muestre en especificas columnas'''

    data = []

    for item_data in data_delivery_note:
        row = frappe._dict({
            # 'identificador': _(item_data.numero_vale_cliente),
            'identificador': _(item_data.numero_vale_gaseco),
            'posting_date': item_data.posting_date,
            'cliente': item_data.customer
            # "indent": flt(1)
        })

        item_info = get_data_item(item_data.name)
        row['codigo_producto'] = item_info[0]['item_code']
        row['monto'] = item_info[0]['amount']
        row['tarifa_lista'] = item_info[0]['rate']
        row['uom'] = item_info[0]['uom']

        if 'DIESEL' in item_info[0]['item_code']:
            row['diesel'] = float(item_info[0]['qty'])

        elif 'REGULAR' in item_info[0]['item_code']:
            row['regular'] = float(item_info[0]['qty'])

        elif 'SUPER' in item_info[0]['item_code']:
            row['super'] = float(item_info[0]['qty'])

        data.append(row)

    return data


def add_total_row(data_preparada):
    '''Agrega una fila extra donde tendran la totalizacion de x items'''

    data = []

    row_data_total = frappe._dict({
        "identificador": _("<b>TOTAL</b>")
    })

    total_diesel = 0
    total_regular = 0
    total_super = 0
    total_monto = 0

    for row_data in data_preparada:
        if row_data.diesel:
            total_diesel += row_data.diesel

        if row_data.regular:
            total_regular += row_data.regular

        if row_data.super:
            total_super += row_data.super

        total_monto += row_data.monto

    row_data_total['monto'] = total_monto
    row_data_total['diesel'] = total_diesel
    row_data_total['regular'] = total_regular
    row_data_total['super'] = total_super

    data.append(row_data_total)
    # data.append({})

    return data
