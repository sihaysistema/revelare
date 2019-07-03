# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json


def validar_configuracion():
    '''Permite verificar que exista una configuración validada para revelare,
       retorna 1 de 3 opciones:
       1 = Una configuracion valida
       2 = Hay mas de una configuracion
       3 = No hay configuraciones
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


@frappe.whitelist()
def template_impuestos():
    '''Funcion encargada de obtener el template de impuestos a
       utilizar en la creacion de Delivery Note en base a la
       Configuracion de revelare
    '''

    c_valida = validar_configuracion()

    if c_valida[0] == 1:
        configuracion = frappe.db.get_values('Configuration Revelare',
                                             filters={'name': c_valida[1]},
                                             fieldname=['template_impuestos_venta'],
                                             as_dict=1)

        data_impuestos = frappe.db.get_values('Sales Taxes and Charges',
                                              filters={'parent': configuracion[0]['template_impuestos_venta']},
                                              fieldname=['charge_type', 'base_tax_amount',
                                                         'tax_amount', 'description',
                                                         'base_tax_amount_after_discount_amount',
                                                         'base_total', 'included_in_print_rate',
                                                         'rate', 'account_head', 'cost_center',
                                                         'tax_amount_after_discount_amount',
                                                         'total'], as_dict=1)

        return data_impuestos


def crear_nota_entrega(documento):
    '''Funcion para crear nota de entrega'''

    delivery_note_tax = template_impuestos()

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

