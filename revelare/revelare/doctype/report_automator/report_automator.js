// Copyright (c) 2021, SHS and contributors
// For license information, please see license.txt

frappe.ui.form.on('Report Automator', {
    onload: function (frm) {
        render_prev(frm);
    },
    refresh: function (frm) {
        if (frm.doc.report_type !== 'Report Builder') {
            if (frm.script_setup_for !== frm.doc.report && !frm.doc.__islocal) {
                frappe.call({
                    method: "frappe.desk.query_report.get_script",
                    args: {
                        report_name: frm.doc.report
                    },
                    callback: function (r) {
                        frappe.dom.eval(r.message.script || "");
                        frm.script_setup_for = frm.doc.report;
                        frm.trigger('show_filters');
                    }
                });
            } else {
                frm.trigger('show_filters');
            }
        }
        if (!frm.is_new()) {
            frm.add_custom_button(__('Download'), function () {
                var w = window.open(
                    frappe.urllib.get_full_url(
                        "/api/method/revelare.revelare.doctype.report_automator.report_automator.download?"
                        + "name=" + encodeURIComponent(frm.doc.name)));
                if (!w) {
                    frappe.msgprint(__("Please enable pop-ups")); return;
                }
            });
            frm.add_custom_button(__('Send Now'), function () {
                frappe.call({
                    method: 'revelare.revelare.doctype.report_automator.report_automator.send_now',
                    args: { name: frm.doc.name },
                    callback: function () {
                        frappe.msgprint(__('Scheduled to send'));
                    }
                });
            });
        } else {
            if (!frm.doc.user) {
                frm.set_value('user', frappe.session.user);
            }
            if (!frm.doc.email_to) {
                frm.set_value('email_to', frappe.session.user);
            }
        }
    },
    report: function (frm) {
        frm.set_value('filters', '');
    },
    show_filters: function (frm) {
        var wrapper = $(frm.get_field('filters_display').wrapper);
        wrapper.empty();

        if (frm.doc.report_type === 'Custom Report' || (frm.doc.report_type !== 'Report Builder'
            && frappe.query_reports[frm.doc.report]
            && frappe.query_reports[frm.doc.report].filters)) {

            // make a table to show filters
            var table = $('<table class="table table-bordered" style="cursor:pointer; margin:0px;"><thead>\
				<tr><th style="width: 50%">'+ __('Filter') + '</th><th>' + __('Value') + '</th></tr>\
				</thead><tbody></tbody></table>').appendTo(wrapper);
            $('<p class="text-muted small">' + __("Click table to edit") + '</p>').appendTo(wrapper);

            var filters = JSON.parse(frm.doc.filters || '{}');

            let report_filters, report_name;

            if (frm.doc.report_type === 'Custom Report'
                && frappe.query_reports[frm.doc.reference_report]
                && frappe.query_reports[frm.doc.reference_report].filters) {
                report_filters = frappe.query_reports[frm.doc.reference_report].filters;
                report_name = frm.doc.reference_report;
            } else {
                report_filters = frappe.query_reports[frm.doc.report].filters;
                report_name = frm.doc.report;
            }

            if (report_filters && report_filters.length > 0) {
                frm.set_value('filter_meta', JSON.stringify(report_filters));
                if (frm.is_dirty()) {
                    frm.save();
                }
            }

            var report_filters_list = []
            $.each(report_filters, function (key, val) {
                // Remove break fieldtype from the filters
                if (val.fieldtype != 'Break') {
                    report_filters_list.push(val)
                }
            })
            report_filters = report_filters_list;

            const mandatory_css = {
                "background-color": "#fffdf4",
                "font-weight": "bold"
            };

            report_filters.forEach(f => {
                const css = f.reqd ? mandatory_css : {};
                const row = $("<tr></tr>").appendTo(table.find("tbody"));
                $("<td>" + f.label + "</td>").appendTo(row);
                $("<td>" + frappe.format(filters[f.fieldname], f) + "</td>")
                    .css(css)
                    .appendTo(row);
            });

            table.on('click', function () {
                var dialog = new frappe.ui.Dialog({
                    fields: report_filters,
                    primary_action: function () {
                        var values = this.get_values();
                        if (values) {
                            this.hide();
                            frm.set_value('filters', JSON.stringify(values));
                            frm.trigger('show_filters');
                        }
                    }
                });
                dialog.show();

                //Set query report object so that it can be used while fetching filter values in the report
                frappe.query_report = new frappe.views.QueryReport({ 'filters': dialog.fields_list });
                frappe.query_reports[report_name].onload && frappe.query_reports[report_name].onload(frappe.query_report);
                dialog.set_values(filters);
            })

            // populate dynamic date field selection
            let date_fields = report_filters
                .filter(df => df.fieldtype === 'Date')
                .map(df => ({ label: df.label, value: df.fieldname }));
            frm.set_df_property('from_date_field', 'options', date_fields);
            frm.set_df_property('to_date_field', 'options', date_fields);
            frm.toggle_display('dynamic_report_filters_section', date_fields.length > 0);
        }
    },
    template: function (frm) {
        render_prev(frm)
    }
});

const render_prev = (frm) => {
    let ref_data = JSON.parse(frm.doc.reference_data);
    var $log_wrapper = $(frm.fields_dict.preview_template.wrapper).empty();

    frappe.call({
        method: "revelare.revelare.doctype.report_automator.report_automator.render_template_prev",
        args: {
            opt: frm.doc.template,
            data_select: {
                title: frm.doc.name,
                description: "",
                date_time: "",
                columns: ref_data.cols,
                data: ref_data.data,
                report_url: "",
                report_name: frm.doc.name,
                edit_report_settings: ""
            }
        },
        callback: function (r) {
            $(r.message).appendTo($log_wrapper);
        }
    });
}
