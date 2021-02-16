// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Direct Cash Flow Report"] = {
    "filters": [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.defaults.get_global_default("year_start_date"),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.defaults.get_global_default("year_end_date"),
            reqd: 1
        },
        {
            fieldname: "range",
            label: __("Range"),
            fieldtype: "Select",
            options: [
                { "value": "Weekly", "label": __("Weekly") },
                { "value": "Monthly", "label": __("Monthly") },
                { "value": "Quarterly", "label": __("Quarterly") },
                { "value": "Semi-Anual", "label": __("Semi-Anual") },
                { "value": "Yearly", "label": __("Yearly") }
            ],
            default: "Monthly",
            reqd: 1
        }
    ]
};
