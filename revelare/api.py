# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json

from utils_revelare.clean_data import preparar_data_tabla
from utils_revelare.delivery_note import crear_nota_entrega


@frappe.whitelist()
def convertir_data(data):
    '''Funcion reciba la data del front-end parseandola adecuadamente
       para ser procesada

       parametros:
       ----------
       - data (object-array): Contiene informacion de datatable del frontend
    '''

    # Carga la data como json
    data_tabla = json.loads(data)

    # Limpiar y preparar data json
    # data_preparada = preparar_data_tabla(data_tabla)


    # with open('mi_archivo.json', 'w') as f:
    #     f.write(json.dumps(data_tabla, indent=2))
    #     f.close()

    # for i in data_tabla:
    #     crear_nota_entrega(i)
    # hola = crear_nota_entrega(data_tabla[0])
    # frappe.msgprint(_(str(data_tabla[0])))
    return 'OK'


def validador_operaciones(data_prep):
    '''Funcion encargada de verificar si es necesario crear uno
       de los siguientes documentos:
       - Nota de entrega
       - Factura de Venta

       Parametros:
       ----------
       * data_prep (array-json): Array-json
    '''

    for documento in data_prep:
        # Verificacion notas de entrega
        if documento['numero']:
            if not frappe.db.exists('Delivery Note', {'numero_vale_gaseco': documento['numero']}):
                status_nota_entrega = crear_nota_entrega(documento)

                return status_nota_entrega

        # Verificacion facturas
        if documento['factura']:
            pass