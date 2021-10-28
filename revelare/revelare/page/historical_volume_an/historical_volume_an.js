frappe.pages['historical-volume-an'].on_page_load = function (wrapper) {
  var page = frappe.ui.make_app_page({
    parent: wrapper,
    title: 'Historical Volume Analysis',
    single_column: true
  });

  this.page.$main_historical_volume_an = new frappe.revelare.HistoricalVolumeAn(this.page);
}