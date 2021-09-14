# Copyright (c) 2021, SHS and contributors
# For license information, please see license.txt

import json
from datetime import datetime

import frappe
from frappe.model.document import Document
from frappe.utils import cstr, flt, get_date_str, nowdate, get_time_str


class ErrandTrip(Document):
    pass

@frappe.whitelist()
def get_data(driver=''):
    doctype_list = ['Asset Repair', 'Asset Maintenance Log', 
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
        fieldnames = []

        if doctype == 'Asset Repair':
            filt = [['docstatus','=',0]]
            fieldnames = ['name', 'failure_date']

        elif doctype == 'Asset Maintenance Log':
            filt = [['docstatus','=',0],['maintenance_status','=','Planned'],['maintenance_status','=','Overdue']]
            fieldnames = ['name', 'due_date']

        elif doctype == 'Purchase Order':
            filt = [['docstatus','=',0]]
            fieldnames = ['name', 'schedule_date']

        elif doctype == 'Stock Entry':
            # Si es stock entry tiene estar validado
            filt = {'docstatus' : 1, 'stock_entry_type':'Material Transfer'}
            fieldnames = ['name']

        elif doctype == 'ToDo':
            filt = [['docstatus','=',0]]
            fieldnames = ['name', 'date']

        elif doctype == 'Delivery Note':
            # Si es delivery note tiene que estar el documento validado
            filt = [['docstatus','=',0]]
            fieldnames = ['name']

        else:
            # Para los demas doctypes, se obtendran los que esten en draft
            filt = [['docstatus','=',0]]
            fieldnames = ['name']

        if len(fieldnames) == 2:
            get_list_doctypes = frappe.db.get_list(doctype, filters=filt, fields=fieldnames, order_by=f'{fieldnames[1]} desc') or []
        else:
            get_list_doctypes = frappe.db.get_list(doctype, filters=filt, fields=fieldnames) or []

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
    for d in data:
        d['requested_time'] = datetime.strptime(d['requested_time'], '%Y-%m-%d %H:%M:%S')

    data = sorted(data, key = lambda i: i['requested_time'],reverse=False)

    for d in data:
        d['requested_time'] = add_zeros_to_date(f'{get_date_str(d["requested_time"])} {d["requested_time"].hour}:{d["requested_time"].minute}:{d["requested_time"].second}')

    return data or []

def add_zeros_to_date(string):
    string = string.split(' ')
    string = [string[0]] + string[1].split(':')
    new_string = []
    for s in string:
        if len(s) == 1:
            if string.index(s) == 2:
                s = f':0{s}'
            else:
                s = f'0{s}'
            new_string.append(s)
        else:
            if string.index(s) == 0:
                new_string.append(f'{s} ')

            elif string.index(s) == 2:
                s = f':{s}'
                new_string.append(s)
    str_return = ''
    for new in new_string:
        str_return += new
    return str_return

@frappe.whitelist()
def get_doctypes():
    
    doctype = 'Errand Trip'
    filt = [['docstatus','=',1]]
    fieldnames = ['name']
    get_list_doctypes = frappe.db.get_list(doctype, filters=filt, fields=fieldnames, order_by=f'{fieldnames[1]} desc') or []

def dicToJSON(nomArchivo, diccionario):
    with open(str(nomArchivo+'.json'), 'w') as f:
        f.write(json.dumps(diccionario, indent=2, default=str))
