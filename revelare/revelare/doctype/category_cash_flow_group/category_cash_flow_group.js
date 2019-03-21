// Copyright (c) 2019, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Category Cash Flow Group', {
	setup: function (frm) {
		frm.set_query("parent", function () {
			return {
				"filters": {
					"is_group": 1
				}
			};
		});
	},
	refresh: function (frm) {
		frm.add_custom_button(__('Crear record'), function () {
			frappe.call({
				method: "revelare.data.crear_registros",
				callback: function (data) {
					console.log(data.message);
				}
			})
		}).addClass("btn-primary");
	}
});
