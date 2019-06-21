var rows = 25
var data_content = [];

for (row = 0; row < rows; row++) {
  // Runs 22 times, with values of step 0 through 4.
	data_content.push(['', '', '', '', '', '', '', '', '']);
  	console.log('Se agrego una fila' + row);
}

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
	
	function load_dependencies() {
		frappe.require(["/assets/frappe/css/frappe-datatable.css",
			"/assets/frappe/js/lib/clusterize.min.js",
			"/assets/frappe/js/lib/Sortable.min.js",
			"/assets/frappe/js/lib/frappe-datatable.js"], function(){
					const column1 = {
						name: 'Serie',
						id: 'serie',
						editable: true,
						resizable: true,
						sortable: false,
						focusable: true,
						dropdown: false,
						width: 80
					}
					const column2 = {
						name: 'Numero',
						id: 'serie',
						editable: true,
						resizable: true,
						sortable: false,
						focusable: true,
						dropdown: false,
						width: 80
					}
				const options = {
					columns: [column1, 'Numero', 'Factura', 'Total Factura', 'Cliente', 'Monto del Vale', 'Producto', 'Precio', 'Cantidad' ],
					data: data_content
				}
				let dt = new DataTable('.layout-main-section', options);
			});
	}
	
	function render_page() {

	}
	
	frappe.run_serially([
		() => load_dependencies(),
		() => render_page()
	]);
	
};