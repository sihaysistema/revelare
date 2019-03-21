// frappe.treeview_settings["Category Cash Flow Group"] = {
//     ignore_fields: ["parent"]
// }

frappe.provide("frappe.treeview_settings")

frappe.treeview_settings["Category Cash Flow Group"] = {
    ignore_fields: ["parent"],
    get_tree_nodes: 'revelare.revelare.doctype.category_cash_flow_group.category_cash_flow_group.get_children',
    add_tree_node: 'revelare.revelare.doctype.category_cash_flow_group.category_cash_flow_group.add_node',
    filters: [
        {
            fieldname: "category_cash_flow_group_name",
            fieldtype: "Link",
            options: "Category Cash Flow Group",
            label: __("Category Cash Flow Group"),
            get_query: function () {
                return {
                    filters: [["Category Cash Flow Group", "is_group", "=", 1]]
                };
            }
        },
    ],
    breadcrumb: "Category Cash Flow Group",
    // root_label: "All Categories Cash Flow",
    // get_tree_root: true,
    menu_items: [
        {
            label: __("New Category"),
            action: function () {
                frappe.new_doc("Category Cash Flow Group", true);
            },
            condition: 'frappe.boot.user.can_create.indexOf("Category Cash Flow Group") !== -1'
        }
    ],
    onload: function (treeview) {
        treeview.make_tree();
    }
};