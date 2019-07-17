# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _
import json


def detalles_configuracion(id_conf):
    '''Funcion encargada de obtener detalles de la configuracion
       para revelare'''

    detalles = frappe.db.get_values('Configuration Revelare',
                                    filters={'name': str(id_conf), 'docstatus': 1},
                                    fieldname=['serie_para_factura_de_venta',
                                               'serie_para_notas_de_entrega',
                                               'name'], as_dict=1)
    return detalles


def validar_configuracion():
    '''Permite verificar que exista una configuración validada para revelare,
       retorna 1 de 3 opciones.
       Retornos:
       --------
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


def template_impuestos():
    '''Funcion encargada de obtener el template de impuestos a
       utilizar en la creacion de Delivery Note, Sales Invoice,
       en base a la Configuracion de revelare.

       Retornos:
       --------
       data_impuestos (array/dicts): Retorna un array, donde cada
       posicion es un dict con informacion de x cuenta
    '''

    c_valida = validar_configuracion()

    if c_valida[0] == 1:
        configuracion = frappe.db.get_values('Configuration Revelare',
                                             filters={'name': c_valida[1], 'docstatus': 1},
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


def detalles_item(item_code):
    '''Funcion encargada de obtener la data necesaria por item para realizar los calculos
       de impuestos extras.

       Parametros:
       ----------
       item_code (str): Codigo del producto a consultar

       Retorno:
       -------
       info_item[0] (dict): Diccionario con las propiedades de x item consultado
    '''
    if frappe.db.exists('Item', {'item_code': item_code}):
        info_item = frappe.db.get_values('Item', filters = {'item_code': item_code},
                            fieldname = ['facelec_tax_rate_per_uom_selling_account',
                                        'facelec_tax_rate_per_uom', 'facelec_is_fuel',
                                        'facelec_is_good', 'facelec_is_service',
                                        'item_code'], as_dict = 1)

        return info_item[0]
    else:
        frappe.msgprint(_('Item {} no existe en la base de datos'.format(item_code)))


def crear_nota_entrega(documento, no_vale, conf):
    '''Funcion encargada de crear las notas de entrega
       Parametros:
       ----------
       documento (array/dicts): Array de diccionarios donde cada posicion es un
       item para x vale
       no_vale (str): Numero de vale

       Retornos:
       --------
    '''
    serie_doc = detalles_configuracion(conf)  # Obtiene las series para DN
    delivery_note_tax = template_impuestos()  # Obtiene template tax para DN

    if no_vale:
        # Obtencion de items por vale
        delivery_note_items = []
        # Por cada fila agrupada por vale de datatable
        for i in documento:
            item = {}  ## por cada item creara un objeto + properties
            item_tax = detalles_item(i['producto'])  # Variable guarda info del item

            item['item_code'] = i['producto']
            item['rate'] = i['precio']
            item['shs_dn_is_fuel'] = item_tax['facelec_is_fuel']
            item['shs_dn_is_good'] = item_tax['facelec_is_good']
            item['shs_dn_is_service'] = item_tax['facelec_is_service']
            item['amount'] = float(i['precio']) * float(i['cantidad'])
            item['qty'] = i['cantidad']

            # Inicio calculos por item (Fuels, Goods, Services)
            item['shs_dn_other_tax_amount'] = (float(item_tax['facelec_tax_rate_per_uom']) * 
                                            (float(i['cantidad']) * 1))

            item['shs_dn_amount_minus_excise_tax'] = ((float(i['cantidad']) * float(i['precio'])) -
                                                    (float(i['cantidad']) * 1) * float(item_tax['facelec_tax_rate_per_uom']))

            # asignacion tipo de producto
            item['shs_dn_is_fuel'] = item_tax['facelec_is_fuel']
            item['shs_dn_is_good'] = item_tax['facelec_is_good']
            item['shs_dn_is_service'] = item_tax['facelec_is_service']

            # Calculos para combustibles
            if item_tax['facelec_is_fuel']:
                item['shs_dn_gt_tax_net_fuel_amt'] = (float(item['shs_dn_amount_minus_excise_tax']) / 
                                                    (1 + (float(delivery_note_tax[0]['rate']) / 100)))

                item['shs_dn_sales_tax_for_this_row'] = (float(item['shs_dn_gt_tax_net_fuel_amt']) *
                                                        (float(delivery_note_tax[0]['rate']) / 100))

            # Calculos para bienes
            if item_tax['facelec_is_good']:
                item['shs_dn_gt_tax_net_goods_amt'] = (float(item['shs_dn_amount_minus_excise_tax']) / 
                                                    (1 + (float(delivery_note_tax[0]['rate']) / 100)))

                item['shs_dn_sales_tax_for_this_row'] = (float(item['shs_dn_gt_tax_net_goods_amt']) *
                                                        (float(delivery_note_tax[0]['rate']) / 100))

            # Calculos para servicios
            if item_tax['facelec_is_service']:
                item['shs_dn_gt_tax_net_services_amt'] = (float(item['shs_dn_amount_minus_excise_tax']) / 
                                                        (1 + (float(delivery_note_tax[0]['rate']) / 100)))

                item['shs_dn_sales_tax_for_this_row'] = (float(item['shs_dn_gt_tax_net_services_amt']) *
                                                        (float(delivery_note_tax[0]['rate']) / 100))

            delivery_note_items.append(item)


        total_fuel = 0
        total_service = 0
        total_goods = 0
        total_iva = 0

        # Por cada item del array de items
        # Totaliza por combustible, bienes, servicios y total IVA
        for x in delivery_note_items:
            # Vericacion y acumulacion combustibles
            if 'shs_dn_gt_tax_net_fuel_amt' in x:
                total_fuel += x['shs_dn_gt_tax_net_fuel_amt']

            # Verificacion y acumulacion bienes
            if 'shs_dn_gt_tax_net_goods_amt' in x:
                total_goods += x['shs_dn_gt_tax_net_goods_amt']

            # Verificacion y acumulacion servicios
            if 'shs_dn_gt_tax_net_services_amt' in x:
                total_service += x['shs_dn_gt_tax_net_services_amt']

            # Verificacion y acumulacion IVA total para el documento trabajado
            if 'shs_dn_sales_tax_for_this_row' in x:
                total_iva += x['shs_dn_sales_tax_for_this_row']

        # Creacion nota de entrega
        try:
            # SI no existe la nota de entrega
            if not frappe.db.exists('Delivery Note', {'numero_vale_gaseco': documento[0]['numero']}):
                # Creacion propiedades nota entrega
                delivery_note = frappe.get_doc({"doctype": "Delivery Note",
                                                "naming_series": serie_doc[0]['serie_para_notas_de_entrega'],
                                                "title": documento[0]['cliente'],
                                                "customer": documento[0]['cliente'],
                                                "numero_vale_gaseco": documento[0]['numero'],
                                                "name": documento[0]['factura'],
                                                "company": "SHS",
                                                "items": delivery_note_items,
                                                "shs_dn_gt_tax_fuel": total_fuel,
                                                "shs_dn_gt_tax_goods": total_goods,
                                                "shs_dn_gt_tax_services": total_service,
                                                "shs_dn_total_iva": total_iva,
                                                "apply_discount_on": "Grand Total",
                                                "taxes": delivery_note_tax,
                                                "docstatus": 1})

                # Inserta la nota de entrega a la base de datos
                DN_created = delivery_note.insert(ignore_permissions=True)
        except:
            frappe.msgprint(_('Error al intentar crear la nota de entrega con el vale {}'.format(str(documento[0]['numero']))))
        else:
            return 'OK delivery note created'
            # frappe.msgprint(_('OK Creado'))


def crear_factura_venta(documento):
    '''Funcion encargada de crear la facturas de venta
       Parametros:
       ----------
       documento (array/dicts): Array de diccionarios donde cada posicion es un
       item para x factura

       Retornos:
       --------
    '''

    sales_inv_tax = template_impuestos()

    # Obtencion de items por vale
    sales_inv_items = []
    # Por cada fila agrupada por vale de datatable
    for i in documento:
        item = {}
        item_tax = detalles_item(i['producto'])  # Variable contiene info del item

        item['item_code'] = i['producto']
        item['rate'] = i['precio']
        item['facelecis_fuel'] = item_tax['facelec_is_fuel']
        item['facelec_is_good'] = item_tax['facelec_is_good']
        item['facelec_is_service'] = item_tax['facelec_is-service']
        item['amount'] = float(i['precio']) * float(i['cantidad'])
        item['qty'] = i['cantidad']

        # Inicio calculos por item (Fuels, Goods, Services)
        item['facelec_other_tax_amount'] = (float(item_tax['facelec_tax_rate_per_uom']) * 
                                          (float(i['cantidad']) * 1))

        item['facelec_amount_minus_excise_tax'] = ((float(i['cantidad']) * float(i['precio'])) -
                                                 (float(i['cantidad']) * 1) * float(item_tax['facelec_tax_rate_per_uom']))

        # asignacion tipo de producto
        item['facelecis_fuel'] = item_tax['facelec_is_fuel']
        item['facelec_is_good'] = item_tax['facelec_is_good']
        item['facelec_is_service'] = item_tax['facelec_is_service']

        # Calculos para combustibles
        if item_tax['facelec_is_fuel']:
            item['facelec_gt_tax_net_fuel_amt'] = (float(item['facelec_amount_minus_excise_tax']) / 
                                                  (1 + (float(delivery_note_tax[0]['rate']) / 100)))

            item['facelec_sales_tax_for_this_row'] = (float(item['facelec_gt_tax_net_fuel_amt']) *
                                                    (float(delivery_note_tax[0]['rate']) / 100))

        # Calculos para bienes
        if item_tax['facelec_is_good']:
            item['facelec_gt_tax_net_goods_amt'] = (float(item['facelec_amount_minus_excise_tax']) / 
                                                  (1 + (float(delivery_note_tax[0]['rate']) / 100)))

            item['facelec_sales_tax_for_this_row'] = (float(item['facelec_gt_tax_net_goods_amt']) *
                                                    (float(delivery_note_tax[0]['rate']) / 100))

        # Calculos para servicios
        if item_tax['facelec_is_service']:
            item['facelec_gt_tax_net_services_amt'] = (float(item['facelec_amount_minus_excise_tax']) / 
                                                     (1 + (float(delivery_note_tax[0]['rate']) / 100)))

            item['facelec_sales_tax_for_this_row'] = (float(item['facelec_gt_tax_net_services_amt']) *
                                                    (float(delivery_note_tax[0]['rate']) / 100))

        sales_inv_items.append(item)


    total_fuel = 0
    total_service = 0
    total_goods = 0
    total_iva = 0

    # Por cada item del array de items
    # Totaliza por combustible, bienes, servicios y total IVA
    for x in sales_inv_items:
        # Vericacion y acumulacion combustibles
        if 'facelec_gt_tax_net_fuel_amt' in x:
            total_fuel += x['facelec_gt_tax_net_fuel_amt']

        # Verificacion y acumulacion bienes
        if 'facelec_gt_tax_net_goods_amt' in x:
            total_goods += x['facelec_gt_tax_net_goods_amt']

        # Verificacion y acumulacion servicios
        if 'facelec_gt_tax_net_services_amt' in x:
            total_service += x['facelec_gt_tax_net_services_amt']

        # Verificacion y acumulacion IVA total para el documento trabajado
        if 'facelec_sales_tax_for_this_row' in x:
            total_iva += x['facelec_sales_tax_for_this_row']

    # Creacion factura de venta en funcion del vale
    try:
        # SI no existe la factura de venta
        if not frappe.db.exists('Sales Invoice', {'numero_vale_gaseco': documento[0]['numero']}):
            # Creacion propiedades nota entrega
            delivery_note = frappe.get_doc({"doctype": "Delivery Note",
                                            "title": documento[0]['cliente'],
                                            "customer": documento[0]['cliente'],
                                            "numero_vale_gaseco": documento[0]['numero'],
                                            "name": documento[0]['factura'],
                                            "company": "SHS",
                                            "items": delivery_note_items,
                                            "shs_dn_gt_tax_fuel": total_fuel,
                                            "shs_dn_gt_tax_goods": total_goods,
                                            "shs_dn_gt_tax_services": total_service,
                                            "shs_dn_total_iva": total_iva,
                                            "apply_discount_on": "Grand Total",
                                            "taxes": delivery_note_tax,
                                            "docstatus": 1})

            # Inserta la nota de entrega a la base de datos
            SI_created = delivery_note.insert(ignore_permissions=True)
    except:
        frappe.msgprint(_('Error al intentar crear la nota de entrega con el vale {}'.format(str(documento[0]['numero']))))
    else:
        return 'OK delivery note created'
        # frappe.msgprint(_('OK Creado'))


def crear_dn_si(documento, conf_name):
    '''Funcion encargada de verificar la creacion de Notas de Entrega
       y/o Facturas de Venta
    '''

    data_tabla = json.loads(documento[0])

    # lista que contiene los vales encontrados en datatable
    vales = documento[1]

    # Por cada vale de datatable
    for vale in vales:
        # estado_doc = crear_nota_entrega(data_tabla[vale], vale)
        estado_doc = crear_nota_entrega(data_tabla[vale], vale, conf_name)
        # frappe.msgprint(_(str(data_tabla[vale])))
    # TODO: TRABAJAR LOG ESPECIFICANDO ERRORES...ETC...
    return estado_doc
