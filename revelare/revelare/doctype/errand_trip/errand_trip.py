# Copyright (c) 2021, SHS and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class ErrandTrip(Document):
    pass

@frappe.whitelist()
def get_data(driver=''):
    doctype_list = ['Assets Repair', 'Asset Maintenance', 
                    'Purchase Receipt', 'Purcharse Order', 
                    'Stock Entry', 'Timesheet', 'ToDo', 'Delivery Note']

    data = []
    for doctype in doctype_list:
        get_list_doctypes = []
        filt = {}
        if doctype == 'Stock Entry':
            filt = {'docstatus':1, 'stock_entry_type':'Material Transfer'}
        elif doctype == 'Delivery Note':
            filt = {'docstatus':1}
        else:
            filt = {'docstatus':0}
            
        fieldnames = ['name']
        get_list_doctypes = frappe.db.get_values(doctype, filters=filt, fieldname=fieldnames, as_dict=1) or []

        if get_list_doctypes != []:
            for doc in get_list_doctypes:
                data.append({
                    'document_type': doctype,
                    'document': doc.get('name')
                })

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