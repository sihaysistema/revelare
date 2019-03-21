# -*- coding: utf-8 -*-
# Copyright (c) 2019, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet

class CategoryCashFlowGroup(NestedSet):
	nsm_parent_field = 'parent'

	def on_update(self):
		# super(Location, self).on_update()
		NestedSet.on_update(self)

	def on_trash(self):
		# NestedSet.validate_if_child_exists(self)
		NestedSet.on_update(self)
		# self.remove_ancestor_location_features()
		super(CategoryCashFlowGroup, self).on_update()

@frappe.whitelist()
def get_children(doctype, parent=None, location=None, is_root=False):
	if parent is None or parent == 'All Categories Cash Flow':
		parent = ''
	
	return frappe.db.sql("""
		SELECT 
			name AS value,
			is_group AS expandable
		FROM
			`tabCategory Cash Flow Group` comp
		WHERE
			IFNULL(parent, "")=%(parentt)s
	""", {'parentt': frappe.db.escape(parent)}, as_dict=1)

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args
	args = frappe.form_dict
	doc = make_tree_args(**args)

	if args.parent == 'All Categories Cash Flow':
		args.parent = None

	frappe.get_doc(doc).insert()

def on_doctype_update():
	frappe.db.add_index("Category Cash Flow Group", ["lft", "rgt"])
