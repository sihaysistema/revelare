frappe.pages['historical-volume-an'].on_page_load = function (wrapper) {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Historical Volume Analysis',
    single_column: true
  });

  let field = page.add_field({
    label: 'Status',
    fieldtype: 'Select',
    fieldname: 'status',
    options: [
      'Open',
      'Closed',
      'Cancelled'
    ],
    change() {
      console.log(field.get_value());
    }
  });

  this.page.$main_historical_volume_an = new frappe.revelare.HistoricalVolumeAn(this.page);
}