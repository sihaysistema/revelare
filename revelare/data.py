# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe import _

# Permite trabajar con acentos, ñ, simbolos, etc
import os, sys
reload(sys)
sys.setdefaultencoding('utf-8')

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