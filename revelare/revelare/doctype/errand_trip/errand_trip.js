// Copyright (c) 2021, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Errand Trip', {
    refresh: function(frm) {
        frm.get_field("get_data").$input.addClass("btn btn-primary");
    },
    get_data: function(frm){
        // console.log('Vamos a obtener la data');
        frappe.call({
            method:'revelare.revelare.doctype.errand_trip.errand_trip.get_data',
            args: {
                driver: frm.doc.driver || []
            },
            callback: function (r){
                if (r.message.length > 0){
                    // Revisar la signación de la tabla hija, no esta obteniendo todos los documentos y los esta revolviendo.
                    frm.doc.errand_trip_stop.forEach((element, index) => {
                        frm.get_field("errand_trip_stop").grid.grid_rows[index].remove();
                        frm.get_field("errand_trip_stop ").grid.refresh();
                    });
                    console.log('Items Removidos');
                    // frm.get_field("errand_trip_stop").grid.grid_rows[unbooked_idx].remove()
                    // frm.get_field("unbooked").grid.refresh()

                    r.message.forEach(element => {
                        // Por cada elemento de la lista vamos a agregar una fila a la child table errand_trip_stop
                        frm.add_child('errand_trip_stop',{
                            document_type: String(element.document_type),
                            document: String(element.document),
                            requested_time: String(element.requested_time)
                        });
                    });

                    frm.refresh_field("errand_trip_top");
                    frm.save();
                }
            }
        });
    },
});
