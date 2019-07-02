frappe.pages['tabular-delivery-not'].on_page_load = function (wrapper) {

    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Delivery Note Tabular Entry',
        single_column: true
    });

    // Adding breadcrumbs back to the module / app
    frappe.breadcrumbs.add("Revelare");
    page.add_menu_item('Delivery Note', () => frappe.set_route('List', 'Delivery Note'));

    // page.add_button("Hello", () => {});

    // Declaracion constantes data para columnas
    const column1 = {
        content: "Serie",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: true,
        focusable: true,
        width: 100,
        format: (value) => {
            return value.bold();
        }
    }
    const column2 = {
        content: "Numero",
        id: 'numero',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 114
    }
    const column3 = {
        content: "Factura",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 121
    }
    const column4 = {
        content: "Total Factura",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 111
    }
    const column5 = {
        content: "Cliente",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 130
    }
    const column6 = {
        content: "Monto del Vale",
        id: 'monto_del_vale',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 127
    }
    const column7 = {
        content: "Producto",
        id: 'producto',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 150
    }
    const column8 = {
        content: "Precio",
        id: 'precio',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 121
    }
    const column9 = {
        content: "Cantidad",
        id: 'cantidad',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 121
    }

    // Carga las dependencias necesarias para DATATABLE, para luego ser renderizado
    function load_dependencies() {
        frappe.require(["/assets/frappe/css/frappe-datatable.css",
            "/assets/frappe/js/lib/clusterize.min.js",
            "/assets/frappe/js/lib/Sortable.min.js",
            "/assets/frappe/js/lib/frappe-datatable.js"
        ], () => {
            // create a container that will render the datatable.
            var rows = 25;
            var data_content = [];
            var data_template = ['', '', '', '', '', '', '', '', ''];

            for (row = 0; row < rows; row++) {
                // Runs 22 times, with values of step 0 through 4.
                data_content.push(data_template);
                //console.log('Se agrego una fila' + row);
            }

            // container sera el div donde se renderizara datatable
            const container = document.querySelector('.layout-main-section');
            const options = {
                columns: [column1, column2, column3, column4, column5, column6, column7, column8, column9],
                data: data_content
            }

            const data_datatable = new DataTable(container, options);

        });
    }

    // Ejecucion serialmente
    frappe.run_serially([
        () => load_dependencies()
    ]);

    // Agrega un boton al menu de la pagina
    page.add_menu_item(__("OK"), function (e) {
        // Array contendra la data de las 25 filas y 9 columnas
        var ary = [];

        $(function () {
            var numero = 0;
            var seleccion = '';

            // Selector jquery -> especificamente la seccion de datatable
            $('.data-table-body tr').each(function (a, b) {
                // Por cada fila, agregara info al array anteriormente declarado
                ary.push({
                    serie: $('tr[data-row-index="' + a + '"] td[data-col-index="1"] .content').text().trim(),
                    numero: $('tr[data-row-index="' + a + '"] td[data-col-index="2"] .content').text().trim(),
                    factura: $('tr[data-row-index="' + a + '"] td[data-col-index="3"] .content').text().trim(),
                    total_factura: $('tr[data-row-index="' + a + '"] td[data-col-index="4"] .content').text().trim(),
                    cliente: $('tr[data-row-index="' + a + '"] td[data-col-index="5"] .content').text().trim(),
                    monto_del_vale: $('tr[data-row-index="' + a + '"] td[data-col-index="6"] .content').text().trim(),
                    producto: $('tr[data-row-index="' + a + '"] td[data-col-index="7"] .content').text().trim(),
                    precio: $('tr[data-row-index="' + a + '"] td[data-col-index="8"] .content').text().trim(),
                    cantidad: $('tr[data-row-index="' + a + '"] td[data-col-index="9"] .content').text().trim(),
                });

            });

            // console.log(ary);
            // alert(JSON.stringify(ary));

            // Se ejecuta una peticion al servidor cuando se pulsa el boton 'OK'
            frappe.call({
                method: "revelare.api.convertir_data",
                args: {
                    data: ary
                },
                callback: function (r) {
                    // frm.reload_doc();
                    console.log(r.message);
                }
            });

        });
    });

};

// frappe.pages['tabular-delivery-not'].onclick = function (wrapper) {
//     console.log('worked!');
// }