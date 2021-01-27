// Copyright (c) 2021, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Direct Cash Flow Component', {
    // refresh: function(frm) {

    // }
});


cur_frm.cscript.refresh = function(doc, cdt, cdn) {
    cur_frm.cscript.set_root_readonly(doc);
}

cur_frm.cscript.set_root_readonly = function(doc) {
    // read-only for root territory
    if(!doc.parent_direct_cash_flow_component && !doc.__islocal) {
        cur_frm.set_read_only();
        cur_frm.set_intro(__("This is a root Component and cannot be edited."));
    } else {
        cur_frm.set_intro(null);
    }
}

//get query select territory
/*
cur_frm.fields_dict['parent_component'].get_query = function(doc,cdt,cdn) {
    return{
        filters:[
            ['Direct Cash Flow Component', 'is_group', '=', 1],
            ['Direct Cash Flow Component', 'name', '!=', doc.component_name]
        ]
    }
}*/