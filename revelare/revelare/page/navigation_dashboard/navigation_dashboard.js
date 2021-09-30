frappe.pages['navigation-dashboard'].on_page_load = function (wrapper) {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Navigation Dashboard',
    single_column: true
  });

  // let $btn = page.set_primary_action("Refresh", () => console.log("Refresh"));

  this.page.$main_page_navigator_dashboard = new frappe.revelare.NavigationDashboard(this.page);
}