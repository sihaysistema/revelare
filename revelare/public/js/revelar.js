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
                (uom_row_i.revelare_default_uom_sales_analytics_2) ? frm.enable_save() : console.log('unckecked');
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

// Validando CustomField Journal Entry Account
frappe.ui.form.on('Journal Entry', {
    setup : function(frm){
        cur_frm.set_query("inflow_component", "accounts", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "cash_effect":"Inflow"
                }
            };
        });
        cur_frm.set_query("outflow_component", "accounts", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "cash_effect":"Outflow"
                }
            };
        });
    }
});

// Funcionalidad sobre tabla hija en Journal Entry
frappe.ui.form.on('Journal Entry Account', {
    account : function(frm, cdt,cdn){
        //Creamos objeto de la tabla hija
        let row = frappe.get_doc(cdt, cdn);
        // Validamos con un booleano si desde python el tipo de cuenta es 'cash' o 'bank'
        frappe.call({
            method: 'revelare.data.get_type_account',
            args: {
                account_name: row.account
            },
            callback: (r) => {
                console.log(r.message)
                if(r.message == true){

                    if(frm.credit_in_account_currency > 0){
                        //frappe.msgprint("Credit es > 0")
                        // Hacemos visible el campo outflow_component
                        var df=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df.hidden=0;

                        // Y ocultamos el campo inflow_component
                        var df2=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df2.hidden=1;
                        frm.refresh_fields();
                    } else if(frm.debit_in_account_currency > 0){
                        //frappe.msgprint("debit es > 0")
                        // Hacemos visible el campo inflow_component
                        var df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df.hidden=0;

                        // Y ocultamos el campo outflow_component
                        var df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df2.hidden=1;
                        frm.refresh_fields();
                    } else {
                        //frappe.msgprint("Default, debit y credit = 0")
                        // Hacemos visible el campo inflow_component
                        var df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df.hidden=0;

                        // Y ocultamos el campo outflow_component
                        var df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df2.hidden=1;
                        frm.refresh_fields();
                    }
                } else {
                    //frappe.msgprint("Campos ocultados")
                    // Ocultamos el campo inflow_component
                    var df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                    df.hidden=1;

                    // Ocultamos el campo direct_cash_flow_component
                    var df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                    df2.hidden=1;

                    row.inflow_component = ''
                    row.outflow_component = ''
                    frm.refresh_fields();
                }
            }
        })
    },
    party_type : function(frm, cdt,cdn){
        let row = frappe.get_doc(cdt, cdn);
        if(row.party_type == 'Customer'){
            //frappe.msgprint("Fijando valor inflow component")
            // Dandode el valor al campo respecto a Party Type
            cur_frm.set_value(row.inflow_component,'Receipts from Customers');
        }
        frm.refresh();
    }, 
    debit_in_account_currency : function(frm,cdt,cdn){
        //Creamos objeto de la tabla hija
        let row = frappe.get_doc(cdt, cdn);
        // Validamos con un booleano si desde python el tipo de cuenta es 'cash' o 'bank'
        frappe.call({
            method: 'revelare.data.get_type_account',
            args: {
                account_name: row.account
            },
            callback: (r) => {
                console.log(r.message)
                if(r.message == true){

                    // Si debito es => 0 Filtrar componenete, mostrar solo Inflow
                    let row = frappe.get_doc(cdt, cdn);
                    if(row.debit_in_account_currency > 0){
                        //frappe.msgprint("Debit trigger; debit > 0")
                        // Hacemos visible el campo inflow_component
                        var df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df.hidden=0;

                        // Y ocultamos el campo outflow_component
                        var df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df2.hidden=1;
                    } else {
                        //frappe.msgprint("Debit trigger; debit > 0")
                        // Hacemos visible el campo outflow_component
                        var df=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df.hidden=0;

                        // Y ocultamos el campo inflow_component
                        var df2=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df2.hidden=1;
                    }
                    frm.refresh();
                } else {
                    //frappe.msgprint("Campos ocultados")
                    // Ocultamos el campo inflow_component
                    var df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                    df.hidden=1;

                    // Ocultamos el campo direct_cash_flow_component
                    var df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                    df2.hidden=1;

                    row.inflow_component = ''
                    row.outflow_component = ''
                    frm.refresh_fields();
                }
            }
        })
    },
    credit_in_account_currency : function(frm,cdt,cdn){
        // Si credito es => 0 Filtrar componenete, mostrar solo Outflow
        let row = frappe.get_doc(cdt, cdn);

        frappe.call({
            method: 'revelare.data.get_type_account',
            args: {
                account_name: row.account
            },
            callback: (r) => {
                console.log(r.message)
                if(r.message == true){
                    if(row.credit_in_account_currency > 0){
                        // Hacemos visible el campo outflow_component
                        var df=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df.hidden=0;
            
                        // Y ocultamos el campo inflow_component
                        var df2=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df2.hidden=1;
                    }else {
                        // Hacemos visible el campo inflow_component
                        var df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df.hidden=0;
            
                        // Y ocultamos el campo outflow_component
                        var df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df2.hidden=1;
                    }
                    frm.refresh();
                } else {
                    //frappe.msgprint("Campos ocultados")
                    // Ocultamos el campo inflow_component
                    var df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                    df.hidden=1;

                    // Ocultamos el campo direct_cash_flow_component
                    var df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                    df2.hidden=1;

                    row.inflow_component = ''
                    row.outflow_component = ''
                    frm.refresh_fields();
                }
            }
        })

    }
});


// Validando customfield de Payment Entry
frappe.ui.form.on("Payment Entry", {
    setup: function(frm) {
        frm.set_query("direct_cash_flow_component", function() {
            return {
            filters: [
                ["Direct Cash Flow Component","is_group", "in", ["0"]]
            ]
            }
        });
    }
});
