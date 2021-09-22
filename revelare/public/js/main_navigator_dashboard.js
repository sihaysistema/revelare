frappe.provide('frappe.revelare');   // create a namespace within the Frappe instance
frappe.provide('frappe');   // create a namespace within the Frappe instance
import MainNavigatorDashboard from './MainNavigatorDashboard.vue';

frappe.revelare.NavigationDashboard = class {   // create a glue class, wich will manage your Vue instance
  constructor({ parent }) {
    this.$parent = $(parent);
    this.page = parent.page;
    this.setup_header();
    this.make_body();
  }
  make_body() {
    this.$main_navigator_dashboard = this.$parent.find('.layout-main');   // bind the new Vue instance to the main <div> on the page
    this.vue = new Vue({
      el: this.$main_navigator_dashboard[0],
      data: {
        // timer: ''
      },
      render: h => h(MainNavigatorDashboard),

    });
  }
  setup_header() {
  }
};