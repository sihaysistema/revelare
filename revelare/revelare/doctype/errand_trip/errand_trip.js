// Copyright (c) 2021, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Errand Trip', {
  /*refresh: function (frm) {
    frm.get_field("get_data").$input.addClass("btn btn-primary");
  },*/
  get_data: function (frm) {
    // console.log('Vamos a obtener la data');
    frappe.call({
      method: 'revelare.revelare.doctype.errand_trip.errand_trip.get_data',
      args: {
        driver: frm.doc.driver || []
      },
      callback: function (r) {
        if (r.message.length > 0) {
          if (frm.doc.errand_trip_stop.length > 0) {

            // Revisar la signación de la tabla hija, no esta obteniendo todos los documentos y los esta revolviendo.
            frm.doc.errand_trip_stop.forEach((element, index) => {
              frm.get_field("errand_trip_stop").grid.grid_rows[index].remove();
            });
            frm.get_field("errand_trip_stop").grid.refresh();

          }
          //console.log('Items Removidos');
          // frm.get_field("errand_trip_stop").grid.grid_rows[unbooked_idx].remove()
          // frm.get_field("unbooked").grid.refresh()

          r.message.forEach(element => {
            // Por cada elemento de la lista vamos a agregar una fila a la child table errand_trip_stop
            frm.add_child('errand_trip_stop', {
              document_type: String(element.document_type),
              document: String(element.document),
              requested_time: String(element.requested_time)
            });
          });

          //console.log(r.message);
          frm.refresh_field("errand_trip_top");
          frm.save();
        }
      }
    });
  },
});

// Agregando direccion al campo de detalle y contacto
frappe.ui.form.on("Errand Trip Stop", {
  address: function (frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);

    frappe.call({
      method: 'revelare.revelare.doctype.errand_trip.errand_trip.fetch_address',
      args: {
        address: row.address || ''
      },
      callback: function (r) {
        //console.log(r.message);
        //console.log(typeof(r.message));
        let address_detail = r.message.string_address;
        let latitude = r.message.latitude;
        let longitude = r.message.longitude;

        row.address_details = address_detail;
        row.lat = latitude;
        row.lng = longitude;
        cur_frm.refresh_field('errand_trip_stop');
        frm.refresh();
      }
    });
  },
  contact: function (frm, cdt, cdn) {

    let row = frappe.get_doc(cdt, cdn);
    frappe.call({
      method: 'revelare.revelare.doctype.errand_trip.errand_trip.fetch_contact',
      args: {
        contact: row.contact || ''
      },
      callback: function (r) {
        // console.log(typeof(r.message));
        let contact_detail = r.message;

        row.contact_details = contact_detail;
        cur_frm.refresh_field('errand_trip_stop');
        frm.refresh();
      }
    });
  }
});


// frappe.ui.form.on('Errand Trip Stop', {

//   address: function (frm, cdt, cdn) {
//     let row = frappe.get_doc(cdt, cdn);

//     row.address_detail = 'Hola Estamos intentando \nagregar texto \n\tformateado';
//     cur_frm.refresh_field('errand_trip_stop');
//     frm.refresh();

//     frappe.call({
//       method: 'revelare.revelare.doctype.errand_trip.errand_trip.fetch_address',
//       args: {
//         address: row.address || ''
//       },
//       callback: function (r) {
//         console.log(r.message);
//       }
//     });


//     // console.log(cdn,'\n\n',cdt,'\n\nEvento Address');
//     let check = 0;
//     // Recorre los elementos de la tabla hija ubicandose exactamente en la fila en que
//     // estemos trabajando, esto para obtener datos exactos.
//     frm.doc.uoms.forEach((uom_row_i, index_i) => {
//       if (uom_row_i.name == cdn) {
//         (uom_row_i.revelare_default_uom_sales_analytics_2) ? frm.enable_save() : console.log('unckecked');
//         // FORMA 2! RECOMENDADA ES5 > :)
//         // Unicamente va permitir que exista un elemento seleccionado
//         frm.doc.uoms.forEach((uom_row, indice) => {
//           if (uom_row.revelare_default_uom_sales_analytics_2) {
//             check++;
//             if (check > 1) {
//               frappe.msgprint('Solamente debe haber un elemento seleccionado');
//               frm.doc.uoms[index_i].revelare_default_uom_sales_analytics_2 = 0;
//               refresh_field('uoms');
//               // console.log(uom_row_i.revelare_default_uom_sales_analytics_2)
//             }
//           }
//         });
//       }
//     });
//   },
//   contact: function (frm, cdt, cdn) {

//     let row = frappe.get_doc(cdt, cdn);
//     frappe.call({
//       method: 'revelare.revelare.doctype.errand_trip.errand_trip.fetch_contact',
//       args: {
//         contact: row.contact || ''
//       },
//       callback: function (r) {
//         console.log(r.message);

//         row.contact_detail = `Hola Estamos intentando \nagregar texto \n\tformateado`;
//         cur_frm.refresh_field('errand_trip_stop');
//         frm.refresh();
//         frm.save();
//       }
//     });
//   }
// });



// frappe.listview_settings['Errand Trip'] = {
//   //  add_fields: ["title", "start_date", "end_date"],
//   get_indicator: function (doc) {
//     const status_color = {
//       "Active": "#EAF5EE", // Draft
//       "Errand Trip Completed": "#D3E9FC", // Submitted
//       "Cancelled": "#FFF5F5", // Cancelled,
//     };

//     let condi = [__(doc.status), status_color[doc.status], "status,=," + doc.status];
//     console.log(condi);
//     return condi;
//   },
//   right_column: "naming_series"
// };
