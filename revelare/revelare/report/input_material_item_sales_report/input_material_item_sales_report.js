// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Input Material Item Sales Report"] = {
	"filters": [
    {
			fieldname: "period",
			label: __("Periodicity"),
			fieldtype: "Select",
			options: [__("Weekly"), __("Monthly"), __("Quarterly"), __("Yearly")],
			reqd: 1,
			default: __("Sales Order")
		},
    {
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: "",
			reqd: 0
    },
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: "",
			reqd: 0
    },
    {
			fieldname: "sales_category",
			label: __("Sold"),
			fieldtype: "Select",
			options: [__("Actual"), __("Estimated"), __("Both")],
			reqd: 1,
			default: __("Actual")
    },
    {
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item",
			default: "",
			reqd: 0
		},
	]
};
