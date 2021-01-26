# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from frappe import _
from datetime import datetime
from erpnext.accounts.report.utils import convert  # value, from_, to, date
import json
from frappe.utils import nowdate, cstr, flt

import pandas as pd
import numpy as np
import math


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    """
    Defines the report column structure
    """
    columns = [
        {
            "label": _("Item"),
            "fieldname": "A",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Estimated Per Period"),
            "fieldname": "B",
            "fieldtype": "Data",
            "width": 145
        },
        {
            "label": _("UOM"),
            "fieldname": "C",
            "fieldtype": "Data",
            "width": 90
        },
        {
            "label": _("Total UOM Sold"),
            "fieldname": "D",
            "fieldtype": "Data",
            "width": 120
        },
        {
            "label": _("Sold Per Period"),
            "fieldname": "E",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Remainder Available"),
            "fieldname": "F",
            "fieldtype": "Data",
            "width": 140
        },
    ]
    return columns


def get_data(filters):
    """
    Accesses and processes the data for the report
    """
    # Empty Row
    empty_row = {}
    data = [empty_row]
    return data
