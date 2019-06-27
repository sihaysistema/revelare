# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json
from utils.clean_data import preparar_data_tabla

# Permite trabajar con acentos, ñ, simbolos, etc
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')


@frappe.whitelist()
def convertir_data(data):
    '''Funcion reciba la data del front-end parseandola adecuadamente
       para ser procesada

       parametros:
       ----------
       - data (object-array): Contiene informacion de datatable del frontend
    '''

    data_tabla = json.loads(data)

    # with open('mi_archivo.json', 'w') as f:
    #     f.write(json.dumps(data_tabla, indent=2))
    #     f.close()

    # for i in data_tabla:
    #     crear_nota_entrega(i)
    hola = crear_nota_entrega(data_tabla[0])
    # frappe.msgprint(_(str(data_tabla[0])))
    return hola


def crear_nota_entrega(documento):
    '''Funcion para crear nota de entrega'''

    delivery_note_tax = [{
        "charge_type": _('On net total'),
        "account_head": 'IVA - S',
        "cost_center": 'Main - S',
        "description": 'IVA @ 12.0',
        "included_in_print_rate": 1,
        "rate": 12
    }]

    delivery_note_items = [{
        "item_code": 'GAS-001',
        "item_name": 'Gasolina Regular',
        "rate": 24,
        "shs_dn_is_fuel": 1,
        "shs_dn_is_good": 0,
        "shs_dn_is_service": 0,
        "amount": 24,
        "qty": 1
    }]

    delivery_note = frappe.get_doc({"doctype": "Delivery Note",
                                    "title": documento['cliente'],
                                    "customer": documento['cliente'],
                                    "numero_vale_gaseco": documento['numero'],
                                    "name": documento['factura'],
                                    "company": "SHS",
                                    "items": delivery_note_items,
                                    "apply_discount_on": "Grand Total",
                                    # "taxes": delivery_note_tax,
                                    "docstatus": 1})
    DN_created = delivery_note.insert(ignore_permissions=True)

    return 'OK'
# {
#     "cantidad": "", 
#     "monto_del_vale": "", 
#     "producto": "", 
#     "precio": "", 
#     "total_factura": "", 
#     "factura": "", 
#     "serie": "mamam", 
#     "numero": "", 
#     "cliente": ""
#   }

def crear_factura(documento):
    pass


def calculos_impuestos(documento):
    pass
