frappe.pages['tabular-delivery-not'].on_page_load = function (wrapper) {
    function mario(value) {
        return `'Hola ${value}'`
    }

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
        // align: 'left',
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
        width: 114,
        format: (value) => {
            return `'Hola ${value}'`
        }
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

    var countries = ["Afghanistan", "Albania", "Algeria",
        "Andorra", "Angola", "Anguilla", "Antigua & Barbuda",
        "Argentina", "Armenia", "Aruba", "Australia", "Austria",
        "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados",
        "Belarus", "Belgium", "Belize", "Benin", "Bermuda", "Bhutan",
        "Bolivia", "Bosnia & Herzegovina", "Botswana", "Brazil",
        "British Virgin Islands", "Brunei", "Bulgaria", "Burkina Faso",
        "Burundi", "Cambodia", "Cameroon", "Canada", "Cape Verde",
        "Cayman Islands", "Central Arfrican Republic", "Chad", "Chile",
        "China", "Colombia", "Congo", "Cook Islands", "Costa Rica", "Cote D Ivoire", "Croatia", "Cuba", "Curacao", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Falkland Islands", "Faroe Islands", "Fiji", "Finland", "France", "French Polynesia", "French West Indies", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Gibraltar", "Greece", "Greenland", "Grenada", "Guam", "Guatemala", "Guernsey", "Guinea", "Guinea Bissau", "Guyana", "Haiti", "Honduras", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Isle of Man", "Israel", "Italy", "Jamaica", "Japan", "Jersey", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Macau", "Macedonia", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Montserrat", "Morocco", "Mozambique", "Myanmar", "Namibia", "Nauro", "Nepal", "Netherlands", "Netherlands Antilles", "New Caledonia", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland", "Portugal", "Puerto Rico", "Qatar", "Reunion", "Romania", "Russia", "Rwanda", "Saint Pierre & Miquelon", "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain", "Sri Lanka", "St Kitts & Nevis", "St Lucia", "St Vincent", "Sudan", "Suriname", "Swaziland", "Sweden", "Switzerland", "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor L'Este", "Togo", "Tonga", "Trinidad & Tobago", "Tunisia", "Turkey", "Turkmenistan", "Turks & Caicos", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States of America", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Virgin Islands (US)", "Yemen", "Zambia", "Zimbabwe"
    ];

    frappe.db.get_list('Customer', {
        fields: ['name'],
        filters: {
            disabled: false
        }
    }).then(records => {
        // console.log(records);
        array_cli = [];

        for (let index = 0; index < records.length; index++) {
            array_cli.push(records[index].name);
        }
        console.log(array_cli);

        frappe.db.get_list('Item', {
            fields: ['item_code'],
            filters: {
                disabled: false
            }
        }).then(records => {
            // console.log(records);
            array_itms = [];

            for (let index = 0; index < records.length; index++) {
                array_itms.push(records[index].item_code);
            }
            console.log(array_itms);

            load_dependencies(array_cli, array_itms);
        });
    });

    // Carga las dependencias necesarias para DATATABLE, para luego ser renderizado
    function load_dependencies(cliente_arr, items_arr) {
        frappe.require(["/assets/frappe/css/frappe-datatable.css",
            "/assets/frappe/js/lib/clusterize.min.js",
            "/assets/frappe/js/lib/Sortable.min.js",
            "/assets/frappe/js/lib/frappe-datatable.js",
            "/assets/revelare/css/mario_style.css"
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

                getEditor(colIndex, rowIndex, value, parent) {
                    // editing obj only for date field
                    // if ((colIndex != 5) || (colIndex != 7)) return;

                    if (colIndex == 5) {
                        const $input = document.createElement('input');
                        $input.type = 'data';
                        parent.appendChild($input);


                        return {
                            initValue(value) {
                                $input.focus();
                                console.log(colIndex);

                                autocompletar($input, cliente_arr);

                                // $input.value = value;
                            },
                            setValue(value) {
                                $input.value = value;
                            },
                            getValue() {
                                return ($input.value);
                                // autocompletar($input, countries);
                            }
                        }
                    } else if (colIndex == 7) {
                        const $input = document.createElement('input');
                        $input.type = 'data';
                        parent.appendChild($input);


                        return {
                            initValue(value) {
                                $input.focus();
                                console.log(colIndex);

                                autocompletar($input, items_arr);

                                // $input.value = value;
                            },
                            setValue(value) {
                                $input.value = value;
                            },
                            getValue() {
                                return ($input.value);
                                // autocompletar($input, countries);
                            }
                        }
                    } else {
                        return
                    }

                }
            }

            const data_datatable = new DataTable(container, options);

        });
    }

    // Ejecucion serialmente
    // frappe.run_serially([
    //     () => load_dependencies(),
    //     () => mi_prueba()
    // ]);

    // Agrega un boton al menu de la pagina
    page.add_menu_item(__("OK"), function (e) {
        // Array contendra la data de las 25 filas y 9 columnas
        var ary = [];

        $(function () {

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
                method: "revelare.api.procesar_data",
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

    // function mi_prueba() {
    //     frappe.db.get_list('Customer', {
    //         fields: ['name'],
    //         filters: {
    //             disabled: false
    //         }
    //     }).then(records => {
    //         arra = [];

    //         for (let index = 0; index < records.length; index++) {
    //             arra.push(records[index].name);
    //         }
    //         console.log(arra);
    //     });
    // }
};

// frappe.pages['tabular-delivery-not'].onclick = function (wrapper) {
//     console.log('worked!');
// }

function autocompletar(inp, arr) {
    /*la función de autocompletar toma dos argumentos,
     el elemento del campo de texto y un array de posibles
     valores autocompletados:*/
    var currentFocus;

    /*Ejecuta la funcion cuando alguie escribe en el campo de texto:*/
    inp.addEventListener("input", function (e) {
        var a, b, i, val = this.value;

        /*Cierra cualquier lista de valores ya completados, osea cuando se
          escribe correctamente una palabra*/
        closeAllLists();
        if (!val) {
            return false;
        }
        currentFocus = -1;

        /*Crear un elemento DIV que contendra los itesm(valores)*/
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");

        /*Agrega un elemento como hijo al contenedor de autocompletado */
        this.parentNode.appendChild(a);

        /*por cada item en el array de posibles valores...*/
        for (i = 0; i < arr.length; i++) {
            /*Verifica si el item empieza con las mismas letras como el valor del campo*/
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {

                /*crea un elemento DIV para cada elemento de correspondencia:*/
                b = document.createElement("DIV");

                /*hace que las letras coincidentes aparezcan en negrita:*/
                b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].substr(val.length);

                /*insertar un campo de entrada que contenga el valor del elemento de array actual:*/
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";

                /*ejecuta una función cuando alguien hace clic en el valor de posición (DIV element):*/
                b.addEventListener("click", function (e) {
                    /*inserta el valor para el campo de texto de autocompletar:*/
                    inp.value = this.getElementsByTagName("input")[0].value;
                    /*cierra la lista de valores autocompletados,
                    (o cualquier otra lista abierta de valores autocompletados:)*/
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });
    /*Ejecuta una función cuando alguien presiona una tecla del teclado:*/
    inp.addEventListener("keydown", function (e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {

            /*Si se pulsa la tecla de flecha HACIA ABAJO,
            aumenta la variable currentFocus:*/
            currentFocus++;

            /*Y hace que el elemento actual sea mas visible*/
            addActive(x);
        } else if (e.keyCode == 38) { //up - arriba
            /*Si la tecla arriba es precionada,
            disminuye el vaor de la variable currentFocus:*/
            currentFocus--;
            /*y hace que el item actual sea mas visible:*/
            addActive(x);
        } else if (e.keyCode == 13) {
            /*si se preciona la tecla ENTER evita que el formulario se valide y envie*/
            e.preventDefault();
            if (currentFocus > -1) {
                /*y simula un click sobre el elemento activo*/
                if (x) x[currentFocus].click();
            }
        }
    });

    function addActive(x) {
        /** una funcion para clasificar un item como activo */
        if (!x) return false;

        /**Empieza por remover la clase activa sobre todos los elementos */
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);

        /*agrega la clase "autocomplete-active":*/
        x[currentFocus].classList.add("autocomplete-active");
    }

    function removeActive(x) {

        /**Funcion para remover la clase "active" de todos los item autocompletados */
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }

    function closeAllLists(elmnt) {
        /*cierra todas las listas de autocompletar del documento,
        excepto la que pasó como argumento:
        */
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    /**Se ejecuta cuando alguien hace click sobre el documento */
    document.addEventListener("click", function (e) {
        closeAllLists(e.target);
    });
}