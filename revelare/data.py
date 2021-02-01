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
def get_type_account(account_name=''):
    try:
        if frappe.db.exists('Account', {'account_type':'Bank','name':account_name}):
            return True
        elif frappe.db.exists('Account', {'account_type':'Cash','name':account_name}):
            return True
        else:
            return False
    except:
        return False