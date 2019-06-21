var rows = 25;
var data_content = [];
var data_template = ['', '', '', '', '', '', '', '', ''];
const column1 = {
	name: "Serie",
	id: 'serie',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column2 = {
	name: "Numero",
	id: 'numero',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column3 = {
	name: "Factura",
	id: 'serie',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column4 = {
	name: "Total Factura",
	id: 'serie',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column5 = {
	name: "Cliente",
	id: 'serie',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column6 = {
	name: "Monto del Vale",
	id: 'monto_del_vale',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column7 = {
	name: "Producto",
	id: 'producto',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column8 = {
	name: "Precio",
	id: 'precio',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
const column9 = {
	name: "Cantidad",
	id: 'cantidad',
	editable: true,
	resizable: true,
	sortable: false,
	focusable: true,
	dropdown: false,
	width: 80
}
var column_content = ['Serie', 'Numero', 'Factura', 'Total Factura', 'Cliente', 'Monto del Vale', 'Producto', 'Precio', 'Cantidad' ]
//var column_content = [column1, column2, column3, column4, column5, column6, column7, column8, column9]

for (row = 0; row < rows; row++) {
  // Runs 22 times, with values of step 0 through 4.
	data_content.push(data_template);
	//console.log('Se agrego una fila' + row);
}
var data = data_content

frappe.pages['tabular-delivery-not'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Delivery Note Tabular Entry',
		single_column: true
	});
	// Adding breadcrumbs back to the module / app
	frappe.breadcrumbs.add("Revelare");
	page.add_menu_item('Delivery Note', () => frappe.set_route('List', 'Delivery Note'))
	
	// create a container that will render the datatable.
	const container = '.layout-main-section';
	
	function prepare_configuration(){
	
	}
	
	function load_dependencies() {
		frappe.require(["/assets/frappe/css/frappe-datatable.css",
			"/assets/frappe/js/lib/clusterize.min.js",
			"/assets/frappe/js/lib/Sortable.min.js",
		"/assets/frappe/js/lib/frappe-datatable.js"], function(){

				const options = {
					columns: column_content,
					data: data_content
				}
				let dt = new DataTable('.layout-main-section', options);
			});
	}

	function render_page() {

	}

	frappe.run_serially([
		//() => prepare_configuration(),
		() => load_dependencies(),
		//() => render_page()
	]);
	
};