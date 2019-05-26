# Copyright (c) 2019, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import json
from frappe import _, scrub

def execute(filters=None):
    # Array que contendra n {objetos} donde cada {objeto}
    # es una fila
    data = []

    columns = get_columns()

    # Si se selecciona un cliente en el filtro, se retornara
    # la data especifica para x cliente
    if (filters.customer):
        datos = get_specific_data(filters)

    # Selecciona toda la data que encuentre
    else:
        datos = get_all_data(filters)

    # Prepara la data para ser adaptada
    data_preparada = prepare_data(datos)
    data.extend(data_preparada)
    # data.append({})
    data.extend(add_total_row(data_preparada))

    return columns, data


def get_columns():
    '''Retorna las columnas a utilizar en el reporte'''

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
        }
    ]

    # Obtiene las columnas configuras para el reporte
    dat_config = get_configured_columns()

    # Por cada columna configurada encontrada la agregara
    for i in dat_config:
        columns.append({
            "label": str(i['column_name']),
            "fieldname": str(i['column_name']).lower(),
            "fieldtype": "Float",
            "width": 80
        })

    return columns


def get_all_data(filters):
    '''Retorna todas las notas de entrega que se encuentren en el rango
       de fechas seleccionado
    '''

    # campo viejo es -> numero_vale_gaseco
    delivery_note = frappe.db.sql('''SELECT posting_date, numero_vale_cliente,
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

    # campo viejo es -> numero_vale_gaseco
    delivery_note = frappe.db.sql('''SELECT posting_date, numero_vale_cliente,
                                            name, customer_name, customer
                                    FROM `tabDelivery Note`
                                    WHERE posting_date
                                    BETWEEN %(fecha_inicio)s AND %(fecha_final)s
                                    AND customer=%(cliente)s AND company=%(compa)s''',
                                    {'fecha_inicio': str(filters.from_date),
                                     'fecha_final': str(filters.to_date),
                                     'cliente': str(filters.customer),
                                     'compa': str(filters.company)}, as_dict=True)

    return delivery_note


def get_data_item(vale):
    '''Obtiene informacion de n items de x nota de entrega'''

    delivery_note_item = frappe.db.get_values('Delivery Note Item',
                                              filters={'parent': vale},
                                              fieldname=['item_code', 'qty', 'amount', 'uom',
                                                        'rate'], as_dict=1)

    return delivery_note_item


def prepare_data(data_delivery_note):
    '''Prepara la data para que se muestre en especificas columnas'''

    data = []
    # Obtiene las columnas configuradas para el reporte
    columnas_productos = get_configured_columns()

    # Por cada nota de entrega encontrada
    for item_data in data_delivery_note:
        # Obtiene n items por x nota de entrega
        item_info = get_data_item(item_data.name)

        n_items = len(item_info)

        for x in range(0, n_items):
            row = frappe._dict({
                'identificador': '<b>{}</b>'.format(item_data.numero_vale_cliente),
                'posting_date': item_data.posting_date,
                'cliente': item_data.customer
            })
            row['codigo_producto'] = item_info[x]['item_code']
            row['monto'] = item_info[x]['amount']
            row['tarifa_lista'] = item_info[x]['rate']
            row['uom'] = item_info[x]['uom']

            # filtra y compara que el item exista en la configuracion de columnas para el reporte
            columna = filter(lambda xx: xx['item_code'] == item_info[x]['item_code'], columnas_productos)

            # Intentara acceder a la cantidad de X producto, si ocurre un error quiere decir que no
            # existe en la configuracion de columnas por lo que no se agregara y procedera con las que
            # si
            try:
                row[str(columna[0]['column_name']).lower()] = float(item_info[x]['qty'])
            except:
                pass
            else:
                data.append(row)

    return data


def add_total_row(data_preparada):
    '''Agrega una fila extra donde tendran la totalizacion de x items'''

    data = []
    # Obtiene las columnas configuradas para el reporte
    columnas_productos = get_configured_columns()

    row_data_total = frappe._dict({
        "identificador": _("<b>TOTAL</b>")
    })

    # Totales por cantidad item - columna
    for i in columnas_productos:
        total_columna = filter(lambda xx: xx['codigo_producto'] == i['item_code'], data_preparada)
        data_col = []

        for y in total_columna:
            data_col.append(y[str(i['column_name']).lower()])

        row_data_total[str(i['column_name']).lower()] = reduce(lambda x, yy: x + yy, data_col)

    # Total monto reporte
    total_mt = []
    total_monto = filter(lambda z: z['monto'], data_preparada)
    for t in total_monto:
        total_mt.append(t['monto'])
    
    row_data_total['monto'] = reduce(lambda b, c: b + c, total_mt)

    data.append(row_data_total)

    return data


def get_configured_columns():
    '''Obtiene la configuracion de columnas'''

    data_validada = validar_configuracion()

    if data_validada[0] == 1:
        columnas_configuradas = frappe.db.get_values('Columnas Reporte', 
                                                     filters={'parent': str(data_validada[1])},
                                                     fieldname=['item_code', 'column_name'], as_dict=1)
        return columnas_configuradas
    else:
        return []


def validar_configuracion():
    '''Permite verificar que exista una configuracion validada,
       retorna 1 de 3 opciones:
       1 : Una configuracion valida
       2 : Hay mas de una configuracion
       3 : No hay configuraciones
    '''

    # verifica que exista un documento validado, docstatus = 1 => validado
    if frappe.db.exists('Configuration Revelare', {'docstatus': 1}):

        configuracion_valida = frappe.db.get_values('Configuration Revelare',
                                                   filters={'docstatus': 1},
                                                   fieldname=['name'], as_dict=1)
        if (len(configuracion_valida) == 1):
            return (int(1), str(configuracion_valida[0]['name']))

        elif (len(configuracion_valida) > 1):
            return (int(2), 'Error 2')

    else:
        return (int(3), 'Error 3')
