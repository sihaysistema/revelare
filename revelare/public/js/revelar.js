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
    },
});

// Funcionalidad sobre tabla hija en Journal Entry
frappe.ui.form.on('Journal Entry Account', {
    account : function(frm, cdt,cdn){
        validate_cash_flow_component(frm, cdt, cdn);
    },
    party_type : function(frm, cdt,cdn){
        let row = frappe.get_doc(cdt, cdn);
        if(row.party_type == 'Customer'){
            // Dandode el valor al campo respecto a Party Type
            cur_frm.set_value(row.inflow_component,'Receipts from Customers');
        }
        frm.refresh();
    }, 
    debit_in_account_currency : function(frm,cdt,cdn){
        validate_cash_flow_component(frm, cdt, cdn, field='debit');
    },
    credit_in_account_currency : function(frm,cdt,cdn){
        validate_cash_flow_component(frm, cdt, cdn, field='credit');
    },
    form_render : function(frm, cdt, cdn){
        validate_cash_flow_component(frm, cdt, cdn);
    }
});

function validate_cash_flow_component(frm, cdt, cdn, field=''){
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
                // En el campo debito, si el debito es = 0 y el credito es > 0
                if(row.credit_in_account_currency > 0 && (row.debit_in_account_currency == 0 || row.debit_in_account_currency == undefined)){
                    // Hacemos visible el campo outflow_component
                    let df=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                    df.hidden=0;
        
                    // Y ocultamos el campo inflow_component
                    let df2=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                    df2.hidden=1;
                    row.debit_in_account_currency = 0
                // En el campo debito, si el debito es = 0 y el credito es > 0
                }else if(row.debit_in_account_currency > 0 && (row.credit_in_account_currency == 0 || row.credit_in_account_currency == undefined)){
                    // Hacemos visible el campo inflow_component
                    let df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                    df.hidden=0;
        
                    // Y ocultamos el campo outflow_component
                    let df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                    df2.hidden=1;
                    row.credit_in_account_currency = 0
                } else if(row.debit_in_account_currency > 0 && row.credit_in_account_currency > 0){
                    // Si estamos en el campo de credit ocultamos el inflow
                    if (field == 'credit'){
                        let df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df.hidden=1;
                        let df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df2.hidden=0;
                        row.debit_in_account_currency = 0
                    // Si estamos en el campo de debit ocultamos el outflow
                    } else if(field == 'debit'){
                        let df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                        df.hidden=0;
                        let df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                        df2.hidden=1;
                        row.credit_in_account_currency = 0
                    }
                } else if((row.credit_in_account_currency == undefined) &&(row.debit_in_account_currency == undefined)) {
                    // Hacemos visible el campo inflow_component
                    let df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                    df.hidden=0;

                    // Y ocultamos el campo outflow_component
                    let df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                    df2.hidden=1;
                } else{
                    // Ocultamos los dos campos
                    let df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                    df.hidden=1;

                    let df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                    df2.hidden=1;
                }
                frm.refresh();
            } else {
                // Ocultamos el campo inflow_component
                let df=frappe.meta.get_docfield("Journal Entry Account", "inflow_component",frm.doc.name);
                df.hidden=1;

                // Ocultamos el campo direct_cash_flow_component
                let df2=frappe.meta.get_docfield("Journal Entry Account", "outflow_component",frm.doc.name);
                df2.hidden=1;

                row.inflow_component = ''
                row.outflow_component = ''
                frm.refresh_fields();
            }
        }
    });
}


// Validando customfield de Payment Entry
frappe.ui.form.on("Payment Entry", {
    setup: function(frm) {
        cur_frm.set_query("inflow_component", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "cash_effect":"Inflow"
                }
            };
        });
        cur_frm.set_query("outflow_component", function () {
            return {
                "filters": {
                    "is_group": 0,
                    "cash_effect":"Outflow"
                }
            };
        });
    },
    refresh :function(frm){
        // Validamos los campos al momento de que cargue el documento
        if(cur_frm.doc.payment_type == 'Pay'){
            // Al ser pago, habilitamos el campo salida de flujo "outflow"
            let df=frappe.meta.get_docfield("Payment Entry", "outflow_component",frm.doc.name);
            df.hidden = 0

            // Al ser pago, deshabilitamos el campo entra de flujo "inflow"
            let df2=frappe.meta.get_docfield("Payment Entry", "inflow_component",frm.doc.name);
            df2.hidden = 1
        } else if(cur_frm.doc.payment_type == 'Receive'){
            // Al ser pago, deshabilitamos el campo salida de flujo "outflow"
            let df=frappe.meta.get_docfield("Payment Entry", "outflow_component",frm.doc.name);
            df.hidden = 1

            // Al ser entrada, habilitamos el campo entra de flujo "inflow"
            let df2=frappe.meta.get_docfield("Payment Entry", "inflow_component",frm.doc.name);
            df2.hidden = 0
        } else {
            // Al ser transferencia, deshabilitamos los dos campos
            let df=frappe.meta.get_docfield("Payment Entry", "outflow_component",frm.doc.name);
            df.hidden = 1

            let df2=frappe.meta.get_docfield("Payment Entry", "inflow_component",frm.doc.name);
            df2.hidden = 1
        }
    },
    payment_type : function(frm){
        console.log(frm.doc.payment_type)
        if(cur_frm.doc.payment_type == 'Pay'){
            // Al ser pago, habilitamos el campo salida de flujo "outflow"
            let df=frappe.meta.get_docfield("Payment Entry", "outflow_component",frm.doc.name);
            df.hidden = 0

            // Al ser pago, deshabilitamos el campo entra de flujo "inflow"
            let df2=frappe.meta.get_docfield("Payment Entry", "inflow_component",frm.doc.name);
            df2.hidden = 1
        } else if(cur_frm.doc.payment_type == 'Receive'){
            // Al ser pago, deshabilitamos el campo salida de flujo "outflow"
            let df=frappe.meta.get_docfield("Payment Entry", "outflow_component",frm.doc.name);
            df.hidden = 1

            // Al ser entrada, habilitamos el campo entra de flujo "inflow"
            let df2=frappe.meta.get_docfield("Payment Entry", "inflow_component",frm.doc.name);
            df2.hidden = 0
            console.log('Es Una entrada')
        } else {
            // Al ser transferencia, deshabilitamos los dos campos
            let df=frappe.meta.get_docfield("Payment Entry", "outflow_component",frm.doc.name);
            df.hidden = 1

            let df2=frappe.meta.get_docfield("Payment Entry", "inflow_component",frm.doc.name);
            df2.hidden = 1

        }
    }
});
