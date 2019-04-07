// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Delivery Note By Item"] = {
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
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			// default: "Select Customer",
			reqd: 0
		},
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
		}
		// {
		// 	fieldname: "range",
		// 	label: __("Range"),
		// 	fieldtype: "Select",
		// 	options: [
		// 		{ "value": "Weekly", "label": __("Weekly") },
		// 		{ "value": "Monthly", "label": __("Monthly") },
		// 		{ "value": "Quarterly", "label": __("Quarterly") },
		// 		{ "value": "Yearly", "label": __("Yearly") }
		// 	],
		// 	default: "Monthly",
		// 	reqd: 1
		// }
	]
	// ,
	// after_datatable_render: function (datatable_obj) {
	// 	$(datatable_obj.wrapper).find(".dt-row-0").find('input[type=checkbox]').click();
	// }
}
