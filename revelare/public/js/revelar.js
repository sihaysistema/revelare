// Copyright (c) 2018, Si Hay Sistema (SHS) and contributors
// For license information, please see license.txt

// UOM Conversion Detail TABLA HIJA DE Item
frappe.ui.form.on('UOM Conversion Detail', {
    // Ejecuta la funcion cuando exista una interaccion con 'revelare_default_uom_sales_analytics_2'
    revelare_default_uom_sales_analytics_2: function (frm, cdt, cdn) {
        // Recorre los elementos de la tabla hija ubicandose exactamente en la fila en que 
        // estemos trabajando, esto para obtener datos exactos.
        frm.doc.uoms.forEach((uom_row_i, index_i) => {
            if (uom_row_i.name == cdn) {
                // Verifica si tiene check o no
                (uom_row_i.revelare_default_uom_sales_analytics_2) ? console.log('checked'): console.log('unckecked')

                let check = 0;
                // Recorre todas las filas de uoms verificando que existan un solo elemento seleccionado
                $.each(frm.doc.uoms || [], function (i, d) {
                    if (d.revelare_default_uom_sales_analytics_2) {
                        check += 1
                        if (check > 1) {
                            frappe.msgprint('Solamente debe haber un elemento seleccionado')
                            frm.doc.uoms[index_i].revelare_default_uom_sales_analytics_2 = 0
                            refresh_field('uoms');
                            // console.log(uom_row_i.revelare_default_uom_sales_analytics_2)
                        }
                    }
                });
            }
        });
    }
});