// Copyright (c) 2016, SHS and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Cash Flow Detail"] = {
  filters: [
    {
      fieldname: "company",
      label: __("Company"),
      fieldtype: "Link",
      options: "Company",
      default: frappe.defaults.get_user_default("Company"),
      reqd: 1,
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: get_start_date(),
      reqd: 1,
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: get_end_date(),
      reqd: 1,
    },
    {
      fieldname: "range",
      label: __("Range"),
      fieldtype: "Select",
      options: [
        { value: "Weekly", label: __("Weekly") },
        { value: "Monthly", label: __("Monthly") },
        { value: "Quarterly", label: __("Quarterly") },
        { value: "Yearly", label: __("Yearly") },
      ],
      default: "Monthly",
      reqd: 1,
      hidden: 1,
    },
    {
      fieldname: "category",
      label: __("Category"),
      fieldtype: "Link",
      options: "Direct Cash Flow Component",
      get_query: () => {
        return {
          filters: {
            is_group: 0,
          },
        };
      },
      default: "",
      //hidden:1
    },
  ],
};

function get_start_date() {
  var today_date = new Date(); // Obtiene la fecha actual
  // siempre asignara el 1 de enero, el unico que varia es el año
  var start = new Date(today_date.getFullYear(), 0, 1);
  return start;
}

function get_end_date() {
  var today_date = new Date(); // Obtiene la fecha actual
  // siempre asignara el 1 de enero, el unico que varia es el año
  var end = new Date(today_date.getFullYear(), 11, 31);
  return end;
}

// Función para Detail Cash Flow
function open_one_tab(name, type) {
  if (type === "journal_entry") {
    window.open(`/app/journal-entry/${name}`, "_blank");
  } else if (type === "payment_entry") {
    window.open(`/app/payment-entry/${name}`, "_blank");
  }
  return true;
}
