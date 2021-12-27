// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Sales Item Availability por Item"] = {
  "filters": [
    {
        fieldname: "company",
        label: __("Company"),
        fieldtype: "Link",
        options: "Company",
        default: frappe.defaults.get_user_default("Company"),
        reqd: 1
    },
    {
        fieldname: "from_date",
        label: __("From Date"),
        fieldtype: "Date",
        default: "",
        reqd: 0,

        on_change: function (report) {
            const to_date = frappe.datetime.add_days(report.filters[1].value, 6);
            frappe.query_report.set_filter_value("to_date", to_date);
            //frappe.query_report.set_filter_value("to_date", frappe.datetime.add_days(report.filters[1].value, 6));
        },
    },
    {
        fieldname: "to_date",
        label: __("To Date"),
        fieldtype: "Date",
        default: "",
        reqd: 0
    },
    {
        fieldname: "sales_from",
        label: __("Sales From"),
        fieldtype: "Select",
        options: [__("Sales Order"), __("Delivery Note"), __("Sales Invoice")],
        reqd: 1,
        default: __("Sales Order")
    },
    {
      fieldname: "is_sales_item",
      label: __("Is Sales Item"),
      fieldtype: "Check",
      options: [__("Sales Order"), __("Delivery Note"), __("Sales Invoice")],
      reqd: 0,
      default: __("Sales Order")
    },
    {
      fieldname: "item_selected",
      label: __("Item Selected"),
      fieldtype: "Link",
      options: "Item",
      reqd: 0,
      get_query: function () {
        return {
            "doctype": "Item",
            "filters": {
                "is_sales_item": 0,
                //"include_in_estimations": 1,
                "disabled":0
            }
        }
      },
    }
    // {
    //     fieldname: "show_sales",
    //     label: __("Show Sales"),
    //     fieldtype: "Check",
    //     reqd: 0,
    //     default: 0
    // }
]
};
