# Copyright (c) 2020, Si Hay Sistema and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import json
from datetime import datetime, timedelta

import frappe
import numpy as np
from frappe import _, _dict, scrub
from frappe.utils import cstr, flt, nowdate


def total_item_availability_estimates(filters):
    """
    Returns a list of dictionaries that contain the sum of item availability
    estimate name, amounts and uom that fall within a date range
    """
    # Esta función no la utilizamos
    result = frappe.db.sql(
        f"""
      SELECT ei.item_code, SUM(ei.amount) as amount, ei.amount_uom
      FROM `tabItem Availability Estimate` as iae
      INNER JOIN `tabEstimated Item` as ei
      ON iae.name = ei.parent
      WHERE iae.docstatus = 1
      AND ei.docstatus = 1
      AND (iae.start_date AND iae.end_date
           BETWEEN '{filters.from_date}' AND '{filters.to_date}')
      GROUP BY ei.item_code;
      """, as_dict=True
    )
    return result


def total_item_availability_estimate_attributes(filters):
    """
    Returns a list of dictionaries that contain the item availability estimate
    name, estimation name, estimation uom, stock uom, total amount, amount uom
    """
    result = frappe.db.sql(
        f"""
    SELECT name, estimation_name, estimation_uom, stock_uom,
                 estimate.item_name, estimate.amount, estimate.amount_uom
    FROM `tabItem`
    INNER JOIN
      (SELECT ei.item_code, ei.item_name, SUM(ei.amount) as amount, ei.amount_uom
       FROM `tabItem Availability Estimate` as iae
       INNER JOIN `tabEstimated Item` as ei
       ON iae.name = ei.parent
       WHERE iae.docstatus = 1
       AND ei.docstatus = 1
       AND (iae.start_date AND iae.end_date BETWEEN '{filters.from_date}' AND '{filters.to_date}')
       GROUP BY ei.item_code) as estimate
       WHERE name=estimate.item_code;
    """, as_dict=True
    )
    return result

# Este query obtiene todos los items de las ordenes de venta, cuya FECHA DE ENTREGA coincide con las fechas de los filtros del reporte.
# Se utiliza la fecha de entrea estipulada para hacer más precisa la estimación.
def total_sales_items(filters):

    doctype = filters.sales_from
    type_of_report = filters.sales_from

    date_doc = ''
    if filters.sales_from == 'Sales Order':
        date_doc = 'delivery_date'
    elif filters.sales_from == 'Delivery Note':
        date_doc = 'posting_date'
    elif filters.sales_from == 'Sales Invoice':
        date_doc = 'due_date'

    filt = [['docstatus','=',1],[date_doc,'>=',filters.from_date],[date_doc,'<=',filters.to_date]]
    fieldnames = ['name']
    get_list_doctypes = frappe.db.get_list(doctype, filters=filt, fields=fieldnames) or []

    data = []
    for doc in get_list_doctypes:
        doctype = f'{type_of_report} Item'
        filt = [['parent','=',doc['name']]]
        fieldnames = ['parent','item_code', 'delivery_date', 'SUM(stock_qty) AS stock_qty','stock_uom']
        items = frappe.db.get_list(doctype, filters=filt, fields=fieldnames, group_by='item_code')
        data = data + items

    # Hemos dejado de utilizar este query y lo omologamos al codigo anterior
    result = frappe.db.sql(
        f"""
    SELECT soi.item_code, soi.delivery_date,
	         SUM(soi.stock_qty) as stock_qty, soi.stock_uom
    FROM `tabSales Order Item` as soi
    WHERE soi.parent IN
      (SELECT so.name FROM `tabSales Order` AS so
        WHERE so.docstatus=1
        AND (delivery_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'))
    GROUP BY soi.item_code;
    """, as_dict=True
    )

    return data


def item_availability_estimates_range(filters):
    """Function that returns the name of the submitted Item Availability Estimates
    that fall between the dates selected in the filter.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
    """
    result = frappe.db.sql(
        f"""
        SELECT name FROM `tabItem Availability Estimate`
        WHERE docstatus=1 AND start_date AND end_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'
        """, as_dict=True
    )
    return result


def periods_estimated_items(filters, parent):
    """Function that returns the code, amount, and amount uom of each estimated item
    belonging to a valid or submitted Item Availability Estimate

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        parent:  The parent of each one of these items, referring to Item Availability Estimate doctype
    Returns: A list of objects: [{'item_code': 'ITEMCODE-001', 'amount':'15.0', 'amount_uom': 'Pound'}]

    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, amount, amount_uom FROM `tabEstimated Item`
        WHERE docstatus=1 AND parent='{parent}';""", as_dict=True
    )
    return result


def estimation_item_attributes(filters, estimation_item_code):
    """Function that returns the estimation UOM, estimation name and stock_uom for use
    in the calculations and in the report.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        estimation_item_code:  The estimation item name, to find and obtain data from it.
    Returns: A list of dictionaries like this:
    [{'name': 'CULTIVO-0069', 'estimation_name': 'Perejil', 'estimation_uom': 'Pound', 'stock_uom': 'Onza'}]
    """
    result = frappe.db.sql(
        f"""
        SELECT name, estimation_name, estimation_uom, stock_uom FROM `tabItem` WHERE name='{estimation_item_code}';
        """, as_dict=True
    )
    return result


def total_bom_items_sold(filters, estimation_item_code):
    """
    Returns the total sold quantity for an estimation item's bom items
    """


def find_bom_items(filters, estimation_item_code):
    """Function that returns the item_code, parent, stock_qty, stock_uom used in BOM Item, to prepare conversion for use
    in the calculations, and to find BOM names that will help find Sales Items.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        estimation_item_code:  The estimation item name, to find the BOM Items where it is listed, so that we may find the BOMs being used.
    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, parent, stock_qty, stock_uom
        FROM `tabBOM Item`
        WHERE item_code='{estimation_item_code}'
        AND docstatus=1;
        """, as_dict=True
    )
    return result


def find_boms(filters, bom):
    """Function that returns the item, quantity and uom to obtain from this bom, such that we may go find Sales Items.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        bom:  The bom name or ID
    """
    result = frappe.db.sql(
        f"""
        SELECT item, quantity, uom, item_name
        FROM `tabBOM`
        WHERE name='{bom}'
        AND docstatus=1;
        """, as_dict=True
    )
    return result


def find_sales_items(filters, item_code):
    """Function that returns the item code and item name for sales items only.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        item_code: Item code for Item doctype
    """
    result = frappe.db.sql(
        f"""
        SELECT item_name, item_code FROM `tabItem` WHERE name='{item_code}' AND is_sales_item=1 AND include_in_estimations=1;
        """, as_dict=True
    )
    return result


def find_conversion_factor(from_uom, to_uom):
    """Function that returns the item code and item name for sales items only.

    Args:
        from_uom: Unit that user wishes to convert from, i.e. Kilogram
        to_uom: Unit that the user wishes to convert to, i.e. Gram
    Returns: A list containing the following object:
        {
            name: the individual ID name for the conversion factor
            from_uom: the name of the origin UOM
            to_uom: the name of the target UOM
            value: the amount by which origin amount must be multiplied to obtain target amount.
        }
        Updated: returns the value of the 'value' key only.
    """

    ## Validar si la dos UOM son iguales, no se hace conversion y se retorna 1,
    #  Si no se encuentra la conversion se muestra un mensaje que diga,
    # "Unit conversion factor for {from_uom} uom to {to_uom} uom not found, creating a new one, please make sure to specify the correct conversion factor."
    # Agregar un link, que cree un nuevo doctype de conversion, ya con los datos cargados que faltan.

    if from_uom == to_uom:
        return [{
            'from_uom':from_uom,
            'to_uom': to_uom,
            'value': 1
        }]
    else:
        result = frappe.db.sql(
            f"""
            SELECT from_uom, to_uom, value FROM `tabUOM Conversion Factor` WHERE from_uom='{from_uom}' AND to_uom='{to_uom}';
            """, as_dict=True
        )

        if result:
            return result
        else:
            frappe.msgprint(f'Unit conversion factor for {from_uom} uom to {to_uom} uom not found, creating a new one, please make sure to specify the correct conversion factor.')

            return [{
            'from_uom':from_uom,
            'to_uom': to_uom,
            'value': 0
            }]


        # result = frappe.db.sql(
        #     f"""
        #     SELECT from_uom, to_uom, value FROM `tabUOM Conversion Factor` WHERE from_uom='{from_uom}' AND to_uom='{to_uom}';
        #     """, as_dict=True
        # )
        # # Change the return to this variable to provide only the value of the conversion.
        # if result:
        #     value_only = result[0]['value']
        # return result


def find_sales_orders(filters):
    """Function that returns the item code and item name for sales items only.

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        item_code: Item code for Item doctype
    """
    result = frappe.db.sql(
        f"""
        SELECT name FROM `tabSales Order`
        WHERE docstatus=1 AND delivery_date BETWEEN '{filters.from_date}' AND '{filters.to_date}'
        """, as_dict=True
    )
    return result


def find_sales_order_items(filters, parent):
    """Function that returns the code, amount, and amount uom of each estimated item
    belonging to a valid or submitted Item Availability Estimate

    Args:
        filters (dict): filters.from_date, filters.to_date, filters.company, filters.show_sales, filters.periodicty
        parent:  The parent of each one of these items, referring to Item Availability Estimate doctype
    Returns: A list of objects: [{'item_code': 'ITEMCODE-001', 'amount':'15.0', 'amount_uom': 'Pound'}]

    """
    result = frappe.db.sql(
        f"""
        SELECT item_code, delivery_date, stock_qty, stock_uom FROM `tabSales Order Item`
        WHERE docstatus=1 AND parent='{parent}';""", as_dict=True
    )
    return result


def total_sales_items_draft(filters):
    """Funtion that return name of each sales order in draft, to obtain the items.

    Args:
        filters ([type]): [description]
    """
    data = []

    # Comentar desde aquí

    #Obtenemos el doctype de venta a buscar
    doctype = filters.sales_from
    type_of_report = filters.sales_from

    # date_doc obtiene el campo de fecha sobre el que se validara el reporte
    date_doc = ''
    if filters.sales_from == 'Sales Order':
        # Para Sales Order sera delivery_date
        date_doc = 'delivery_date'
    elif filters.sales_from == 'Delivery Note':
        # Para Delivery Note sera posting_date
        date_doc = 'posting_date'
    elif filters.sales_from == 'Sales Invoice':
        # Para Sales Invoice sera due_date
        date_doc = 'due_date'

    # filtros: Docstatus=Draft(0), fecha_pedido entre filtros de fecha, autorepeat: Que no este vacío.
    filt = [['docstatus','=',0],[date_doc,'>=',filters.from_date],[date_doc,'<=',filters.to_date],['auto_repeat','!=',' ']]
    # Campos: name, fecha_pedido
    fieldnames = ['name', date_doc]
    get_list_doctypes = frappe.db.get_list(doctype, filters=filt, fields=fieldnames) or []

    for sales in get_list_doctypes:
        doctype_i = f'{doctype} Item'
        filt = [['parent','=',sales['name']]]
        fieldnames = ['parent','item_code', 'delivery_date', 'SUM(stock_qty) AS stock_qty','stock_uom']
        items = frappe.db.get_list(doctype_i, filters=filt, fields=fieldnames, group_by='item_code')
        for i in items:
            i[date_doc] = sales[date_doc]

        data += items

    # Comentar hasta aquí
    data1 = future_documents(filters)

    data += data1
    return data

def future_documents(filters):
    """Obtiene las repeticiones futuras en el rando de fecha dado en los filtros

    Args:
        filters ([type]): [description]
    """
    # Verificando auto repeticiones
    data_items = []
    try:
        date_now = datetime.strptime(nowdate(),"%Y-%m-%d").date()
        end_date = datetime.strptime(filters.to_date,"%Y-%m-%d").date()
        start_date = datetime.strptime(filters.from_date, "%Y-%m-%d").date()
        sales_from = filters.sales_from

        filt = [['status','=','Active'],['end_date','>=',filters.from_date], ['reference_doctype','=',sales_from]]
        fieldnames = ['name', 'start_date', 'end_date','reference_document', 'reference_doctype']
        l_doctypes = frappe.db.get_list('Auto Repeat', filters=filt, fields=fieldnames) or []

        data = []
        for doc in l_doctypes:
            filt = {'parent':doc['name']}
            fieldnames = ['parent','day']
            items = frappe.db.get_values('Auto Repeat Day', filters=filt, fieldname=fieldnames, as_dict=1)
            for i in items:
                i['start_date'] = doc['start_date']
                i['end_date'] = doc['end_date']
                i['reference_document'] = doc['reference_document']
                i['reference_doctype'] = doc['reference_doctype']
            data.append({doc['name']:items})

        for d in data:
            for k,v in d.items():
                for value in v:
                    date_now = datetime.strptime(nowdate(),"%Y-%m-%d").date()

                    doctype_i = f'{value["reference_doctype"]} Item'
                    filt = [['parent','=',value['reference_document']]]
                    fieldnames = ['parent','item_code', 'delivery_date', 'SUM(stock_qty) AS stock_qty','stock_uom']
                    items = frappe.db.get_list(doctype_i, filters=filt, fields=fieldnames, group_by='item_code')

                    start_date_to_use = None

                    if value['start_date'] > start_date:
                        start_date_to_use = value['start_date']
                    else:
                        start_date_to_use = start_date

                    end_date_to_use = None
                    if value['end_date'] <= end_date:
                        end_date_to_use = value['end_date']
                    else:
                        end_date_to_use = end_date

                    # Si la fecha de inicio de repeticion es menor a la fecha actual, empezamos a contar desde hoy
                    if start_date_to_use < date_now:
                        start_date_to_use =  date_now

                    end_date1 = end_date + timedelta(1)

                    start_date_to_use = datetime.strftime(start_date_to_use, "%Y-%m-%d")
                    end_date1 = datetime.strftime(end_date1, "%Y-%m-%d")
                    date_now = datetime.strftime(date_now, "%Y-%m-%d")


                    days_of_week = {'Monday':'Mon', 'Tuesday':'Tue', 'Wednesday':'Wed', 'Thursday':'Thu', 'Friday':'Fri', 'Saturday':'Sat', 'Sunday':'Sun'}
                    wmask = days_of_week[value['day']]
                    count_days = np.busday_count(start_date_to_use, end_date1, weekmask=wmask)

                    for i in range(0, count_days):
                        data_items += items

    except:
        data_items = []

    return data_items or []


# Para debug
def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))

