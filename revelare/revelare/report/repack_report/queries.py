# Copyright (c) 2013, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def get_stock_value_data(from_date, to_date, item=None,period='Monthly'):
    periodicity = {'Monthly':'MONTH', 'Weekly':'WEEK'}

    filter_for_item = f"AND sed.item_code='{item}'" if item is not None else ''

    # hacer consulta personalizada a la base de datos
    return frappe.db.sql(f"""
                SELECT se.posting_date, {periodicity[period]}(se.posting_date) AS `{period}`,
                    sed.item_code, sed.item_name, SUM(sed.qty) AS `qty`, sed.uom
                FROM `tabStock Entry` AS se
                INNER JOIN `tabStock Entry Detail` AS sed
                ON se.name = sed.parent
                WHERE se.docstatus=1 AND se.stock_entry_type = 'Repack' AND sed.t_warehouse != ''
                AND se.posting_date BETWEEN '{from_date}' AND '{to_date}' {filter_for_item}
                GROUP BY {periodicity[period]}(se.posting_date), sed.item_code
                ORDER BY se.posting_date
                """, as_dict=True)
