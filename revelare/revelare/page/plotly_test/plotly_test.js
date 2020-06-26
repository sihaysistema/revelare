frappe.pages['plotly-test'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Our Cool Plotly Test',
		single_column: true
	});

	this.page.$export_tool = new frappe.revelare.ExportTool(this.page);

}