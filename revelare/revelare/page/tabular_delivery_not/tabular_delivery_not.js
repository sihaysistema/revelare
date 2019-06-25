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
                data: data_content,
                // getEditor(colIndex, rowIndex, value, parent, column, row, data) {
                //     // colIndex, rowIndex of the cell being edited
                //     // value: value of cell before edit
                //     // parent: edit container (use this to append your own custom control)
                //     // column: the column object of editing cell
                //     // row: the row of editing cell
                //     // data: array of all rows

                //     const $input = document.createElement('input');
                //     // $input.type = 'data';
                //     parent.appendChild($input);

                //     return {
                //         // called when cell is being edited
                //         initValue(value) {
                //             $input.focus();
                //             $input.value = (value);
                //         },
                //         // called when cell value is set
                //         setValue(value) {
                //             $input.value = (value);
                //         },
                //         // value to show in cell
                //         getValue() {
                //             return ($input.value);
                //         }
                //     }
                // }
            }

            const data_datatable = new DataTable(container, options);
            console.log(data_datatable);
        });

    }

    frappe.run_serially([
        () => load_dependencies()
    ]);

    page.add_menu_item(__("OK"), function (e) {
        var ary = [];
        $(function () {
            var numero = 0;
            var seleccion = '';
            $('.data-table-body tr').each(function (a, b) {

                // seleccion = String('tr[data-row-index="' + a + '"] td[data-col-index="1"] .content');
                // var seleccion = 'tr[data-row-index="0"] td[data-col-index="1"] .content';
                // console.log(seleccion);

                // var fila = $(seleccion).text().trim();
                // console.log(fila);
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
            console.log(ary);
            // alert(JSON.stringify(ary));
        });
    });

};

frappe.pages['tabular-delivery-not'].onclick = function (wrapper) {
    console.log('worked!');
}