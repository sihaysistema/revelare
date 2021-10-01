frappe.listview_settings['Errand Trip'] = {
  // onload: function (me) {
  //   me.page.set_title(__("Notes"));
  // },
  // add_fields: ["title", "public"],
  get_indicator: function (doc) {
    if (doc.status_doctype == 'Active') {
      return [__("Active"), "green"];
    } else if (doc.status_doctype == 'Errand Trip Completed') {
      return [__("Errand Trip Completed"), "gray"];
    } else if (doc.status_doctype == 'Cancelled') {
      return [__("Cancelled"), "red"];
    }
  }
}
