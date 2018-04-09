// Copyright (c) 2018, Si Hay Sistema (SHS) and contributors
// For license information, please see license.txt

/*
// --- FUNCIONALIDAD EXTRA ---

// TO FIX: 1. Cuando se crea un nuevo producto desde un dialogo.
//         2. Recomendar no utilizar el dialogo para crear productos, sino a pantalla completa para acceder a todas las funciones
//            Se puede desactivar el dialogo personalizando el formulario correspondiente.
// frappe.ui.form.on("Item", {
//     // VERIFICACION AL GUARDAR DOCUMENTO: Cuando se guardar el documento, verificara en la tabla hija 'uoms'
//     // que exista un elemento default, si no existe un elemento default no permitira guardar el documento.
//     validate: function (frm, cdt, cdn) {
//         if (cur_frm.doc.uoms === undefined) {
//             frappe.msgprint('Por favor selecciona una unidad de medida default para Sales Analitycs 2');
//             frm.disable_save();
//         } else {
//             let uncheck = 0;
//             frm.doc.uoms.forEach((uom_element, index) => {
//                 if (uom_element.revelare_default_uom_sales_analytics_2) {
//                     frm.enable_save();
//                     uncheck++;
//                 }
//             });
//             if (uncheck < 1) {
//                 // FIX MESSAGE
//                 frappe.msgprint('Por favor selecciona una unidad de medida default para Sales Analitycs');
//                 frm.disable_save();
//             }
//         }
//     }
// });
*/

// UOM Conversion Detail TABLA HIJA DE Item
frappe.ui.form.on('UOM Conversion Detail', {
    // Ejecuta la funcion cuando exista una interaccion con 'revelare_default_uom_sales_analytics_2'
    revelare_default_uom_sales_analytics_2: function (frm, cdt, cdn) {
        let check = 0;
        // Recorre los elementos de la tabla hija ubicandose exactamente en la fila en que 
        // estemos trabajando, esto para obtener datos exactos.
        frm.doc.uoms.forEach((uom_row_i, index_i) => {
            if (uom_row_i.name == cdn) {
                (uom_row_i.revelare_default_uom_sales_analytics_2) ? frm.enable_save(): console.log('unckecked');
                // FORMA 2! RECOMENDADA ES5 > :)
                // Unicamente va permitir que exista un elemento seleccionado
                frm.doc.uoms.forEach((uom_row, indice) => {
                    if (uom_row.revelare_default_uom_sales_analytics_2) {
                        check++;
                        if (check > 1) {
                            frappe.msgprint('Solamente debe haber un elemento seleccionado');
                            frm.doc.uoms[index_i].revelare_default_uom_sales_analytics_2 = 0;
                            refresh_field('uoms');
                            // console.log(uom_row_i.revelare_default_uom_sales_analytics_2)
                        }
                    }
                });
            }
        });
    }
});