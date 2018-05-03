// Cuando carga, carga la pagina sales-analitycs-2 que a su vez recibe una funcion con parametro
// wrapper, esto quiere decri que podra hacer varias cosas al mismo tiempo
frappe.pages['sales-analytics-2'].on_page_load = function (wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Sales Analytics 2.0',
        single_column: true
    });

    // wrapper permite llamar multiples funciones
    new erpnext.SalesAnalytics2(wrapper);
    frappe.breadcrumbs.add("Revelare");
}

const obtenerData = function (datoItem) {

    frappe.call({
        method: "revelare.revelare.page.sales_analytics_2.sales_analytics_2.obtenerDatosItem",
        args: {
            codigoItem: datoItem
        },
        // El callback recibe como parametro el dato retornado por script python del lado del servidor
        callback: function (data) {
            console.log(data.message)
            // frappe.meta.get_docfield('Sales Analytics 2', 'UOM2', cur_frm.doc.name).options = r.message;
            // // en-US # Updates the current form field 'serie' with the previously obtained data
            // // es-GT # Actualiza el campo 'serie' del formulario actual, con la data obtenida anteriormente
            // cur_frm.refresh_field('UOM2');
        }
    });
}

// $(nn).on('click', '.active.selected', function () {
//     console.log('yeah')
// })


// La vista para Sales Analitycs2 hereda de TreeGridReport :TODO
erpnext.SalesAnalytics2 = frappe.views.TreeGridReport.extend({
    init: function (wrapper) {
        // Super Constructor: Aca se asignan las propiedades iniciales.
        this._super({
            title: __("Sales Analytics 2.0"),
            parent: $(wrapper).find('.layout-main'), // Es una clase CSS PUBLIC/CSS
            page: wrapper.page,
            doctypes: ["Item", "Item Group", "Customer", "Customer Group", "Company", "Territory",
                "Fiscal Year", "Sales Invoice", "Sales Invoice Item",
                "Sales Order", "Sales Order Item[Sales Analytics]",
                "Delivery Note", "Delivery Note Item[Sales Analytics]"
            ],
            tree_grid: {
                show: true
            }
        });

        this.tree_grids = {
            "Customer Group": {
                label: __("Customer Group / Customer"),
                show: true,
                item_key: "customer",
                parent_field: "parent_customer_group",
                formatter: function (item) {
                    return item.customer_name ? item.customer_name + " (" + item.name + ")" : item.name;
                }
            },
            "Customer": {
                label: __("Customer"),
                show: false,
                item_key: "customer",
                formatter: function (item) {
                    return item.customer_name ? item.customer_name + " (" + item.name + ")" : item.name;
                }
            },
            "Item Group": {
                label: __("Item"),
                show: true,
                parent_field: "parent_item_group",
                item_key: "item_code",
                formatter: function (item) {
                    return item.name;
                }
            },
            "Item": {
                label: __("Item"),
                show: true,
                item_key: "item_code",
                formatter: function (item) {
                    return item.name;
                    // return item.stock_uom // Muestra la unidad de medida default
                }
            },
            "Territory": {
                label: __("Territory / Customer"),
                show: true,
                item_key: "customer",
                parent_field: "parent_territory",
                formatter: function (item) {
                    return item.customer_name ? item.customer_name + " (" + item.name + ")" : item.name;
                }
            }
        }
    },
    // Configuracion Columnas
    setup_columns: function () {
        this.tree_grid = this.tree_grids[this.tree_type];

        var std_columns = [{
                id: "check",
                name: "Plot",
                field: "check",
                width: 30,
                formatter: this.check_formatter
            },
            {
                id: "name",
                name: this.tree_grid.label,
                field: "name",
                width: 300,
                formatter: this.tree_formatter
            },
            {
                id: "total",
                name: "Total",
                field: "total",
                plot: false,
                formatter: this.currency_formatter
            },
            // Agregando columna de UOM:
            // Name:  El nombre a mostrar en la columna del informe
            // ? ID:  Asumimos que es el identificador del objeto FIXME
            // Field: El campo que se desea mostrar 
            // Plot: Si se muestra o no en la gráfica
            // Width: El ancho en pixelas de la columna.
            // Formatter: Formater es el formato a mostrarse en la pantalla.
            {
                id: "UOM2",
                name: "UOM",
                field: "stock_uom",
                width: 105,
                plot: false,
                formatter: this.select // formatters.js public/js // muestra la unidad de medida default para cada item
            }
        ];

        this.make_date_range_columns();
        this.columns = std_columns.concat(this.columns);
    },
    // Especificacion de filtros
    filters: [{
            fieldtype: "Select",
            fieldname: "tree_type",
            label: __("Tree Type"),
            //options: ["Customer Group", "Customer",
            //    "Item Group", "Item", "Territory"
            //],
            options: ["Item Group", "Item", "Customer Group", "Customer", "Territory"],
            filter: function (val, item, opts, me) {
                return me.apply_zero_filter(val, item, opts, me);
            }
        },
        {
            fieldtype: "Select",
            fieldname: "based_on",
            label: __("Based On"),
            options: ["Sales Invoice",
                "Sales Order", "Delivery Note"
            ]
        },
        // Confiuracion para dejar cantidad como default y unico filtros
        {
            fieldtype: "Select",
            fieldname: "value_or_qty",
            label: __("Value or Qty"),
            options: [{
                // {
                //     label: __("Value"),
                //     value: "Value"
                // }, 
                label: __("Quantity"),
                value: "Quantity"
            }]
        },
        {
            fieldtype: "Date",
            fieldname: "from_date",
            label: __("From Date")
        },
        {
            fieldtype: "Label",
            fieldname: "to",
            label: __("To")
        },
        {
            fieldtype: "Date",
            fieldname: "to_date",
            label: __("To Date")
        },
        {
            fieldtype: "Select",
            fieldname: "company",
            label: __("Company"),
            link: "Company",
            default_value: __("Select Company...")
        },
        {
            fieldtype: "Select",
            label: __("Range"),
            fieldname: "range",
            options: [{
                    label: __("Daily"),
                    value: "Daily"
                }, {
                    label: __("Weekly"),
                    value: "Weekly"
                },
                {
                    label: __("Monthly"),
                    value: "Monthly"
                }, {
                    label: __("Quarterly"),
                    value: "Quarterly"
                },
                {
                    label: __("Yearly"),
                    value: "Yearly"
                }
            ]
        }
    ],
    // Configurando Filtros
    setup_filters: function () {
        var me = this; // Forma clasica para hacer refencia al contexto del scope actual
        this._super(); // SuperConstructor

        // Actualiza los datos cuando ocurren los trigger dentro del array
        this.trigger_refresh_on_change(["value_or_qty", "tree_type", "based_on", "company"]);

        this.show_zero_check();
        this.setup_chart_check();
    },
    // inicializando Filtros
    init_filter_values: function () {
        this._super();
        this.filter_inputs.range.val('Monthly');
    },
    // Preparando Data
    // TODO:
    prepare_data: function () {
        var me = this;
        if (!this.tl) {
            // add 'Not Set' Customer & Item
            // (Customer / Item are not mandatory!!)
            frappe.report_dump.data["Customer"].push({
                name: "Not Set",
                parent_customer_group: "All Customer Groups",
                parent_territory: "All Territories",
                id: "Not Set",
            });

            frappe.report_dump.data["Item"].push({
                name: "Not Set",
                parent_item_group: "All Item Groups",
                id: "Not Set",
            });
        }

        if (!this.tl || !this.tl[this.based_on]) {
            this.make_transaction_list(this.based_on, this.based_on + " Item");
        }

        if (!this.data || me.item_type != me.tree_type) {

            if (me.tree_type == 'Customer') {
                var items = frappe.report_dump.data["Customer"];
            }

            if (me.tree_type == 'Customer Group') {
                var items = this.prepare_tree("Customer", "Customer Group");
            } else if (me.tree_type == "Item Group") {
                var items = this.prepare_tree("Item", "Item Group");
            } else if (me.tree_type == "Item") {
                var items = frappe.report_dump.data["Item"];
            } else if (me.tree_type == "Territory") {
                var items = this.prepare_tree("Customer", "Territory");
            }

            me.item_type = me.tree_type
            me.parent_map = {};
            me.item_by_name = {};
            me.data = [];

            $.each(items, function (i, v) {
                var d = copy_dict(v);

                me.data.push(d);
                me.item_by_name[d.name] = d;
                if (d[me.tree_grid.parent_field]) {
                    me.parent_map[d.name] = d[me.tree_grid.parent_field];
                }
                me.reset_item_values(d);
            });

            this.set_indent();

        } else {
            // otherwise, only reset values
            $.each(this.data, function (i, d) {
                me.reset_item_values(d);
            });
        }

        this.prepare_balances();

        if (me.tree_grid.show) {
            this.set_totals(false);
            this.update_groups();
        } else {
            this.set_totals(true);
        }

    },
    // Preparar Balances
    // TODO:
    prepare_balances: function () {
        var me = this;
        var from_date = frappe.datetime.str_to_obj(this.from_date);
        var to_date = frappe.datetime.str_to_obj(this.to_date);
        var is_val = this.value_or_qty == 'Value';
        let arrayDatos = [];

        $.each(this.tl[this.based_on], function (i, tl) {
            if (me.is_default('company') ? true : tl.company === me.company) {
                var posting_date = frappe.datetime.str_to_obj(tl.posting_date);
                if (posting_date >= from_date && posting_date <= to_date) {
                    var item = me.item_by_name[tl[me.tree_grid.item_key]] || me.item_by_name['Not Set'];

                    // FIXME: Hacer que en una sola peticion se mande un paquete con toda la informacion que se necesite.
                    // if (arrayDatos.includes(tl.item_code)) {
                    //     console.log('Elemento ya incluido en array');
                    // } else {
                    //     arrayDatos.push(tl.item_code);
                    //     console.log(arrayDatos)
                    // }

                    if (item) {
                        // FIXME: REALIZAR AQUI OPERACIONES MATEMATICAS
                        item[me.column_map[tl.posting_date].field] += (is_val ? tl.base_net_amount : tl.qty); // FIXME: OPERACIONES DE PRUEBA

                        // TODO: Descomente la siguiente linea para ver response y request de datos para cada ITEM
                        // console.log(obtenerData(tl.item_code));
                    }
                }
            }
        });

        // NOTA: TOMAR EN CUENTA EL FUNCIONAMIENTO CUANDO SE EJECUTE EL FILTRO DE CLIENTE, CATEGORIA CLIENTE, TERRITORIO
        // obtiene un htmlcollection
        let classUOMItem = document.getElementsByClassName("slick-cell l3 r3 active selected");
        let opt_1 = [' ', 'Disco Duro', 'Memoria Ram', 'GPU'];
        // cuando se haga un doble click sobre la columna UOM y sobre un elemento en especifico
        // ejecuta una funcion anonima y en ella se agrega un HTML simple para crear un dropdown
        // este HTML se sobreescribe en el DOM donde la clase sea "slick-cell l3 r3 active selected"
        $("div").dblclick(function () {
            $(classUOMItem).html(`
            <style>
            .miEstilo {
                position: center;
                min-width: 90px;
                border: 0;
            }
            </style>

            <form name="formulario1" action="#">
                <select class="miEstilo" id="cosa" name="opt">
                    <option value="0"> </option>
                    <option value="1">w</option>
                </select>
            </form>
            `);

            $(".miEstilo").click(function () {
                // let valr = document.getElementById("cosa").value;
                // console.log(valr)

                // // Se calcula el numero de cosas
                // let numUOM = opt_1.length;
                // document.formulario1.opt.length = numUOM;
                // // Para cada opcion del array lo pongo en el selector
                // for (let i = 0; i < numUOM; i++) {
                //     document.formulario1.opt.options[i].value = opt_1[i];
                //     document.formulario1.opt.options[i].text = opt_1[i];
                // }
                // console.log(document.getElementsByClassName("ui-widget-content slick-row odd active"));

                // Array.from(filaItems).forEach(function (filaItem) {
                //     console.log(filaItem.textContent)
                // });

                // let fila2Items = document.getElementsByClassName("ui-widget-content slick-row even active"); // retuna htmlcollections
                let filaItems = document.querySelector('.ui-widget-content.slick-row.active div.slick-cell.l1.r1');
                console.log(filaItems.textContent)
                // console.log(fila2Items)
                // Array.from(filaItems).forEach(function (fila) {
                //     console.log(fila.textContent)
                // });
            });
        });

        // function cambioUOM() {
        //     let = document.getElementById("cosa").value;
        //     // document.getElementById("demo").innerHTML = "You selected: " + x;
        //     console.log(x)
        // }

        // OPCIONES?
        // $(".slick-cell.l3.r3.active.selected").click(function () {
        //     alert('Hizo primer click');
        // });
        // $(document).ready(function () {
        //     $("div.slick-cell.l3.r3.active.selected").click(function () {
        //         alert('YEAH')
        //     });
        // });
    },
    // Actualizar Grupos
    // TODO:
    update_groups: function () {
        var me = this;

        $.each(this.data, function (i, item) {
            var parent = me.parent_map[item.name];
            while (parent) {
                var parent_group = me.item_by_name[parent];

                $.each(me.columns, function (c, col) {
                    if (col.formatter == me.currency_formatter) {
                        parent_group[col.field] =
                            flt(parent_group[col.field]) +
                            flt(item[col.field]);
                    }
                });
                parent = me.parent_map[parent];
            }
        });
    },
    // Totalizar
    // TODO:
    set_totals: function (sort) {
        var me = this;
        var checked = false;

        $.each(this.data, function (i, d) {
            d.total = 0.0;

            $.each(me.columns, function (i, col) {
                if (col.formatter == me.currency_formatter && !col.hidden && col.field != "total")
                    d.total += d[col.field];
                if (d.checked) {
                    checked = true;
                };
            })

        });

        if (sort) this.data = this.data.sort(function (a, b) {
            return a.total < b.total;
        });

        if (!this.checked) {
            this.data[0].checked = true;
        }
    }
});

// let verificacion = function () {

//     let nn = document.getElementsByClassName("slick-cell l3 r3");

//     for (let i = 0; i < nn.length; i++) {
//         nn[i].addEventListener('click', function () {
//             console.log('EXITO')
//         }, false);
//     }
//     console.log(nn)

// }