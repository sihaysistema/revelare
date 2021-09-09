# Copyright (c) 2021, SHS and contributors
# For license information, please see license.txt

import json

import frappe
from frappe.utils import nowdate, cstr, flt, get_datetime
from frappe.model.document import Document

class ErrandTrip(Document):
    pass

@frappe.whitelist()
def get_data(driver=''):
    doctype_list = ['Assets Repair', 'Asset Maintenance Log', 
                    'Purchase Receipt', 'Purchase Order', 
                    'Stock Entry', 'Timesheet', 'ToDo', 'Delivery Note', 'Shipment']

    # Purchase Receipt: No tiene campo de fecha de solicitud
    # Stock Entry: No tiene campo, solo fecha de posteo)
    # Timesheet: No tiene fecha de solicitud
    # Delivery Note: No tiene campo de solicitud de fechas
    # Shipment: No tiene fecha de solicitud

    data = []
    for doctype in doctype_list:
        get_list_doctypes = []
        filt = {}
        if doctype == 'Asset Repair':
            filt = {'docstatus' : 0}
            fieldnames = ['name', 'failure_date']

        elif doctype == 'Asset Maintenance Log':
            filt = {'docstatus': 0, 'maintenance_status' : 'Planned', 'maintenance_status':'Overdue'}
            fieldnames = ['name', 'due_date']

        elif doctype == 'Purchase Order':
            filt = {'docstatus' : 0}
            fieldnames = ['name', 'schedule_date']

        elif doctype == 'Stock Entry':
            # Si es stock entry tiene estar validado
            filt = {'docstatus' : 1, 'stock_entry_type':'Material Transfer'}
            fieldnames = ['name']

        elif doctype == 'ToDo':
            filt = {'docstatus' : 0}
            fieldnames = ['name', 'date']

        elif doctype == 'Delivery Note':
            # Si es delivery note tiene que estar el documento validado
            filt = {'docstatus' : 1}
            fieldnames = ['name']

        else:
            # Para los demas doctypes, se obtendran los que esten en draft
            filt = {'docstatus' : 0}
            fieldnames = ['name']

        get_list_doctypes = frappe.db.get_values(doctype, filters=filt, fieldname=fieldnames, as_dict=1) or []

        if get_list_doctypes != []:
            for doc in get_list_doctypes:
                
                if doctype == 'Asset Repair':
                    data.append({
                    'document_type': doctype,
                    'document': doc.get('name'),
                    'requested_time': f'{doc.get("failure_date")} 08:00:00'
                    })

                elif doctype == 'Asset Maintenance Log':
                    data.append({
                    'document_type': doctype,
                    'document': doc.get('name'),
                    'requested_time': f'{doc.get("due_date")} 08:00:00'
                    })

                elif doctype == 'Purchase Order':
                    data.append({
                    'document_type': doctype,
                    'document': doc.get('name'),
                    'requested_time': f'{doc.get("schedule_date")} 08:00:00'
                    })

                elif doctype == 'Stock Entry':
                    data.append({
                    'document_type': doctype,
                    'document': doc.get('name'),
                    'requested_time': f'{nowdate()} 08:00:00'
                    })

                elif doctype == 'ToDo':
                    data.append({
                    'document_type': doctype,
                    'document': doc.get('name'),
                    'requested_time': f'{doc.get("date")} 08:00:00'
                    })

                elif doctype == 'Delivery Note':

                    # date_now = nowdate().split('-')
                    #date_now = f'{date_now[2]}-{date_now[1]}-{date_now[0]}'
                    
                    data.append({
                    'document_type': doctype,
                    'document': doc.get('name'),
                    'requested_time': f'{nowdate()} 08:00:00'
                    })

                else:
                    data.append({
                    'document_type': doctype,
                    'document': doc.get('name'),
                    'requested_time': f'{nowdate()} 08:00:00'
                    })

    # shortear por requested_time

    """
    filt = {'docstatus':0}
    doctype = 'Purchase Receipt'
    fieldnames = ['name']
    get_purchase_receipt = frappe.db.get_values(doctype, filters=filt, fieldname=fieldnames, as_dict=1)
    for purchase_receipt in get_purchase_receipt:
        purchase_receipt['document_type'] = 'Purchase Receipt'
        purchase_receipt['document'] = purchase_receipt['name'],
        purchase_receipt['address'] = 'Cliente1-Shipping',

    get_purchase_receipt = get_purchase_receipt + get_purchase_receipt"""

    return data or []

def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
