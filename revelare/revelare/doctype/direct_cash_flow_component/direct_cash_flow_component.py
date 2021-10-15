# -*- coding: utf-8 -*-
# Copyright (c) 2021, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


from frappe.utils import flt
from frappe import _

from frappe.utils.nestedset import NestedSet, get_root_of

class DirectCashFlowComponent(NestedSet):
    pass

    # def on_update(self):
        #super(DirectCashFlowComponent, self).on_update()
        #self.validate_one_root()

def on_doctype_update():
    frappe.db.add_index("Direct Cash Flow Component", ["lft", "rgt"])
