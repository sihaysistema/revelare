frappe.pages['plotly-test'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Our Cool Plotly Test',
		single_column: true
	});
}
console.log('Hello from plotly_test.js');

var imported_helper = undefined;
frappe.require('assets/revelare/js/plotly_start_tool.min.js', () => {
	test2
	//imported_helper = () => { test2 };
});

//imported_helper();
test2();