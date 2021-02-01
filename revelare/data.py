# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _


@frappe.whitelist()
def crear_registros():

    registro = frappe.new_doc("Category Cash Flow Group")
    registro.category_cash_flow_group_name = 'All Categories Cash Flow'
    registro.name = 'All Categories Cash Flow'
    registro.old_parent = ''
    registro.is_group = 1
    registro.parent = ''
    registro.parent_category_cash_flow_group = ''
    registro.save()

    return 'ok'

@frappe.whitelist()
def crear_registros_component(direct_cash_flow_component_name, parent_direct_cash_flow_component, cash_effect, is_group):

    registro = frappe.new_doc("Direct Cash Flow Component")
    registro.direct_cash_flow_component_name = direct_cash_flow_component_name
    registro.parent_direct_cash_flow_component = parent_direct_cash_flow_component
    registro.cash_effect = cash_effect
    registro.old_parent = ''
    registro.is_group = is_group
    registro.save()

    return 'ok'