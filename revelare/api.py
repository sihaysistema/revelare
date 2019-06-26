# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json

# Permite trabajar con acentos, ñ, simbolos, etc
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

@frappe.whitelist()
def convertir_data(data):
    data_tabla = json.loads(data)

    with open('mi_archivo.json', 'w') as f:
        f.write(json.dumps(data_tabla, indent=2))
        f.close()

    for i in data_tabla:
        frappe.msgprint(_(str(i)))

    # frappe.msgprint(_(str(data_tabla)))