frappe.pages['tabular-delivery-not'].on_page_load = function (wrapper) {

    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Delivery Note Tabular Entry',
        single_column: true
    });

    // Adding breadcrumbs back to the module / app
    frappe.breadcrumbs.add("Revelare");
    page.add_menu_item('Delivery Note', () => frappe.set_route('List', 'Delivery Note'))

    const column1 = {
        content: "Serie",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: true,
        focusable: true,
        width: 100
    }
    const column2 = {
        content: "Numero",
        id: 'numero',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 150
    }
    const column3 = {
        content: "Factura",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 150
    }
    const column4 = {
        content: "Total Factura",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 150
    }
    const column5 = {
        content: "Cliente",
        id: 'serie',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 150
    }
    const column6 = {
        content: "Monto del Vale",
        id: 'monto_del_vale',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 150
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
        width: 150
    }
    const column9 = {
        content: "Cantidad",
        id: 'cantidad',
        editable: true,
        resizable: true,
        sortable: false,
        focusable: true,
        dropdown: false,
        width: 150
    }

    function load_dependencies() {
        frappe.require(["/assets/frappe/css/frappe-datatable.css",
            "/assets/frappe/js/lib/clusterize.min.js",
            "/assets/frappe/js/lib/Sortable.min.js",
            "/assets/frappe/js/lib/frappe-datatable.js"
        ], function () {
            // create a container that will render the datatable.
            var rows = 25;
            var data_content = [];
            var data_template = [{
                content: '',
                // disable editing just for this cell
                editable: true,

            }, {
                content: '',
                // disable editing just for this cell
                editable: true,

            }, {
                content: 'MARIO',
                // disable editing just for this cell
                editable: true,

            }, {
                content: '',
                // disable editing just for this cell
                editable: true,

            }, {
                content: '',
                // disable editing just for this cell
                editable: true,

            }, {
                content: '',
                // disable editing just for this cell
                editable: true,

            }, {
                content: '',
                // disable editing just for this cell
                editable: true,

            }, {
                content: '',
                // disable editing just for this cell
                editable: true,

            }, {
                content: '',
                // disable editing just for this cell
                editable: true,

            }];

            for (row = 0; row < rows; row++) {
                // Runs 22 times, with values of step 0 through 4.
                data_content.push(data_template);
                //console.log('Se agrego una fila' + row);
            }

            // var data = data_content

            const container = document.querySelector('.layout-main-section');
            const options = {
                columns: [column1, column2, column3, column4, column5, column6, column7, column8, column9],
                data: data_content
            }
            const data = new DataTable(container, options);
            console.log(data)
        });


    }

    frappe.run_serially([
        () => load_dependencies(),
        // () => render_page()
    ]);

};

frappe.pages['tabular-delivery-not'].onclick = function (wrapper) {
    console.log('worked!');
}