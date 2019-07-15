// Copyright (c) 2019, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Configuration Revelare', {
	refresh: function (frm) {

		frappe.call({
			method: "revelare.api.obtener_series",
			callback: function (r) {
				// console.log(r.message);
				// console.log(r.message['delivery_note']);

				frm.set_df_property("serie_para_notas_de_entrega", "options", r.message['delivery_note']);
				frm.refresh_field('serie_para_notas_de_entrega');

				// frm.set_value('serie_para_factura_de_venta', r.message['sales_invoice'])
				frm.set_df_property("serie_para_factura_de_venta", "options", r.message['sales_invoice']);
				frm.refresh_field('serie_para_factura_de_venta');
			}
		})

	}
});