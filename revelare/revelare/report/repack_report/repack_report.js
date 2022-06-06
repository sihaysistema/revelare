// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["repack-report"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      default: frappe.defaults.get_user_default("Company"),
      reqd: 1,
    },
    {
      fieldname: "fiscal_year",
      label: __("Fiscal Year"),
      fieldtype: "Link",
      options: "Fiscal Year",
      default: frappe.defaults.get_user_default("fiscal_year"),
      reqd: 1,
    },
    {
      fieldname: "period",
      label: __("Period"),
      fieldtype: "Select",
      options: ["Monthly", "Weekly"],
      default: "Monthly",
      reqd: 0,
    },
    {
      fieldname: "item_code",
      label: __("Item Code"),
      fieldtype: "Link",
      options: "Item",
      reqd: 0,
    },
    // {
    //   fieldname: "item_selected",
    //   label: __("Item Selected"),
    //   fieldtype: "Link",
    //   options: "Item",
    //   reqd: 0,
    //   get_query: function () {
    //     return {
    //       doctype: "Item",
    //       filters: {
    //         is_sales_item: 0,
    //         include_in_estimations: 1,
    //       },
    //     };
    //   },
    // },
  ],
};
