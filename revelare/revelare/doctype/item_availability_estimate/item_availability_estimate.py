# -*- coding: utf-8 -*-
# Copyright (c) 2020, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class ItemAvailabilityEstimate(Document):
    def on_submit(self):
        self.status = 'Submitted'
        frappe.db.set_value(self.doctype, self.name, "status", self.status)

    def on_cancel(self):
        self.status = 'Cancelled'
        frappe.db.set_value(self.doctype, self.name, "status", self.status)

    def validate(self):
        self.status = 'Draft'
        frappe.db.set_value(self.doctype, self.name, "status", self.status)

