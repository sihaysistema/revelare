// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

let year_list = ['2021','2020','2019','2018','2017','2016','2015','2014','2013','2012','2011','2010']

frappe.query_reports["Historical Weekly Item Amounts"] = {
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
        fieldname: "year",
        label: __("Year of data"),
        fieldtype: "Select",
        options: year_list,
        default: "2021",
        reqd: 0
    },
    {
      fieldname: "year_selected",
      label: __("Year Selected"),
      fieldtype: "Select",
      options: year_list,
      default: "2021",
      reqd: 0
    },
    {
      fieldname: "is_sales_item",
      label: __("Is Sales Item"),
      fieldtype: "Check",
      reqd: 0
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
                "include_in_estimations":1
            }
        }
      },
    },
  ]
};
