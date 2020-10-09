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

                // Limpia las filas de las tablas hijas
                frm.doc.available_items = [];

                frm.doc.selected_items = [];
                frm.refresh_field('selected_items');

                for (const iterator of r.message) {
                    let row = frm.add_child('available_items', {
                        item_code: iterator.item_code,
                        stock_qty: iterator.stock_qty,
                        stock_uom: iterator.stock_uom,
                        datetime_added: iterator.datetime_added
                    });
                }

                frm.refresh_field('available_items');
                frm.save()
            },
            error: (r) => {
                // on error
            }
        })
    },
    select: function(frm){
        let selected = frm.get_selected('selected_items');

        if ('available_items' in selected) {
            console.log(selected); // mostramos los seleccioanods, show the selected items

            // en esta lista se guardaran los registros para la otra tabla hija
            // This list iwll store the items for the other child table.
            let my_list = []

            selected.available_items.forEach(element => {
                console.log(element);

                // Recorremos la tabla hija origen para obtener sus valores
                //now we iterate again to obtain the values we want
                frm.doc.available_items.forEach((row, index) => {
                    if (row.name === element) {
                        // Al Array agregamos lso elementos seleccionados, esto
                        // se ira a guardar a la tabla hija destino
                        var current_val = {  // cada iteracion es data para una nueva fila en la tabla hija
                            item_code: row.item_code,
                            stock_qty: row.stock_qty,
                            stock_uom: row.stock_uom,
                            datetime_added: row.datetime_added
                        }
                        my_list.push(current_val)
                        current_val = {}  // reiniamos el valor
                    };
                });
            });

            // console.log(my_list)

            // Itera la lista de filas seleccionadas en la primera tabla hija
            for (const iterator of my_list) {
                // En cada iteracion agrega una fila a la tabla hija selected_items
                frm.add_child("selected_items", iterator);
                // console.log(iterator);
            }

            // frm.doc.selected_items = [];
            frm.refresh_field("selected_items");

            // Tras agregado los valores a la nueva tabla hija, eliminamos las ya no necesaria
            // de la tabla hija original
            var tbl = frm.doc.available_items || [];
            var i = tbl.length;

            while (i--)
            {
                if(tbl[i].__checked == 1) {  // Elimina las especicas seleccionadas
                    cur_frm.get_field("available_items").grid.grid_rows[i].remove();
                }
            }

            frm.refresh_field("available_items");
        }
    }
});