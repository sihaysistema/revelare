// Copyright (c) 2019, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Configuration Revelare', {
	refresh: function (frm) {
		frm.add_custom_button(__('Test'), function () {
			frappe.call({
				method: "revelare.utils_revelare.delivery_note.template_impuestos",
				callback: function (r) {
					//console.log(r);
					//frappe.msgprint(r);
					//frm.doc.cae = r.message
					// frm.reload_doc()
				}
			})
		}).addClass("btn-primary");
	}
});