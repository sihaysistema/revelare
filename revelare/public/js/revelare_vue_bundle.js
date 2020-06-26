// Copyright (c) 2018, Si Hay Sistema (SHS) and contributors
// For license information, please see license.txt

/* THIS WORKS!!!!
console.log('Plotly startup tool basic');
*/

// works, with some errors, namely attaching some libraries to a document.
// import Plotly from '../node_modules/plotly.js/dist/plotly.js'
// import Plotly from '/assets/revelare/node_modules/plotly.js/dist/plotly.min.js'

import ToolRoot from '../vue/ToolRoot.vue';

frappe.provide('frappe.revelare');   // create a namespace within the Frappe instance

frappe.revelare.ExportTool = class {   // create a glue class, wich will manage your Vue instance
    constructor({ parent }) {
        this.$parent = $(parent);
        this.page = parent.page;
        this.setup_header();
        this.make_body();
    }
    make_body() {
        this.$export_tool_container = this.$parent.find('.layout-main');   // bind the new Vue instance to the main <div> on the page
        this.vue = new Vue({
            el: this.$export_tool_container[0],
            data: {
            },
            render: h => h(ToolRoot),
        });
    }
    setup_header() {
    }
};