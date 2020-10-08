// Copyright (c) 2020, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Order per Stock Entry Detail', {
    // refresh: function(frm) {

    // },
    item: function (frm) {
        frappe.call({
            method: 'revelare.revelare.doctype.sales_order_per_stock_entry_detail.queries.get_items_available_for_sale',
            args: {
                item_code: frm.doc.item
            },
            freeze: false,
            callback: (r) => {
                // on success
                console.log(r.message);

                frm.doc.available_items = []

                for (const iterator of r.message) {
                    let row = frm.add_child('available_items', {
                        item_code: iterator.item_code,
                        stock_qty: iterator.stock_qty,
                        stock_uom: iterator.stock_uom,
                        datetime_added: iterator.datetime_added
                    });
                }

                frm.refresh_field('available_items');
            },
            error: (r) => {
                // on error
            }
        })
    }
});