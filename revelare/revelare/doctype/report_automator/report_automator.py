# -*- coding: utf-8 -*-
# Copyright (c) 2021, SHS and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import calendar
import json
from datetime import timedelta

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import (add_to_date, format_time, get_link_to_form,
                          get_url_to_report, global_date_format, now,
                          now_datetime, today, validate_email_address)
from frappe.utils.csvutils import to_csv
from frappe.utils.xlsxutils import make_xlsx

max_reports_per_user = frappe.local.conf.max_reports_per_user or 150


# Se encuentran en revelare/templates
REPORT_TEMPLATES = {
    "Basic Template": "basic_template.html",
    "Basic Colorized Template": "color_template.html"
}

class ReportAutomator(Document):
    def validate(self):
        self.validate_report_count()
        self.validate_emails()
        self.validate_report_format()
        self.validate_mandatory_fields()

    def validate_emails(self):
        '''Obtiene los correos destinatarios'''
        if ',' in self.email_to:
            self.email_to.replace(',', '\n')

        valid = []
        for email in self.email_to.split():
            if email:
                validate_email_address(email, True)
                valid.append(email)

        self.email_to = '\n'.join(valid)

    def validate_report_count(self):
        '''Validación para no exceder el numero de reportes automatizados por usuario'''
        count = frappe.db.sql('select count(*) from `tabReport Automator` where user=%s and enabled=1', self.user)[0][0]
        if count > max_reports_per_user + (-1 if self.flags.in_insert else 0):
            frappe.throw(_('Only {0} emailed reports are allowed per user').format(max_reports_per_user))

    def validate_report_format(self):
        """ Validacion formatos de reporte NOTA: XML NO DISPONIBLE AUN """
        valid_report_formats = ["HTML", "XLSX", "CSV"]
        if self.format not in valid_report_formats:
            frappe.throw(_("%s is not a valid report format. Report format should \
                one of the following %s"%(frappe.bold(self.format), frappe.bold(", ".join(valid_report_formats)))))

    def validate_mandatory_fields(self):
        # Check if all Mandatory Report Filters are filled by the User
        filters = frappe.parse_json(self.filters) if self.filters else {}
        filter_meta = frappe.parse_json(self.filter_meta) if self.filter_meta else {}
        throw_list = []
        for meta in filter_meta:
            if meta.get("reqd") and not filters.get(meta["fieldname"]):
                throw_list.append(meta['label'])
        if throw_list:
            frappe.throw(
                title= _('Missing Filters Required'),
                msg= _('Following Report Filters have missing values:') +
                    '<br><br><ul><li>' + ' <li>'.join(throw_list) + '</ul>',
            )

    def fields_to_child_table(self):
        """Obtiene las columnas que un reporte puede mostrar"""
        report = frappe.get_doc('Report', self.report)

        self.filters = frappe.parse_json(self.filters) if self.filters else {}

        if self.report_type=='Report Builder' and self.data_modified_till:
            self.filters['modified'] = ('>', now_datetime() - timedelta(hours=self.data_modified_till))

        if self.report_type != 'Report Builder' and self.dynamic_date_filters_set():
            self.prepare_dynamic_filters()

        columns, data = report.get_data(limit=self.no_of_rows or 100, user = self.user,
            filters = self.filters, as_dict=True, ignore_prepared_report=True)

        # Obtencion de cols
        columns_report_ref = self.get_cols_report(columns, data)

        return columns_report_ref

    def get_report_content(self):
        '''Retorna los datos formateados, para generar un HTML, XLSX, CSV'''
        
        # TODO: Validar que formatos quieren para hacerlos con xlsxwriter
        
        report = frappe.get_doc('Report', self.report)

        self.filters = frappe.parse_json(self.filters) if self.filters else {}

        if self.report_type=='Report Builder' and self.data_modified_till:
            self.filters['modified'] = ('>', now_datetime() - timedelta(hours=self.data_modified_till))

        if self.report_type != 'Report Builder' and self.dynamic_date_filters_set():
            self.prepare_dynamic_filters()

        columns, data = report.get_data(limit=self.no_of_rows or 100, user = self.user,
            filters = self.filters, as_dict=True, ignore_prepared_report=True)

         # filter data
        if self.columns_report:
            columns, data = filter_data_repo(self.columns_report, columns, data)

        # Usar para debug
        # with open('new-columnas.json', 'w')as f:
        #     f.write(json.dumps(columns, indent=2, default=str))

        # with open('new-data.json', 'w')as f:
        #     f.write(json.dumps(data, indent=2, default=str))

        # add serial numbers
        columns.insert(0, frappe._dict(fieldname='idx', label='', width='30px'))
        for i in range(len(data)):
            data[i]['idx'] = i+1

        if len(data)==0 and self.send_if_data:
            return None

        if self.format == 'HTML':
            columns, data = make_links(columns, data)
            columns = update_field_types(columns)
            return self.get_html_table(columns, data)

        elif self.format == 'XLSX':
            spreadsheet_data = self.get_spreadsheet_data(columns, data)
            xlsx_file = make_xlsx(spreadsheet_data, "Report Automator")
            return xlsx_file.getvalue()

        elif self.format == 'CSV':
            spreadsheet_data = self.get_spreadsheet_data(columns, data)
            return to_csv(spreadsheet_data)

        else:
            frappe.throw(_('Invalid Output Format'))

    def get_html_table(self, columns=None, data=None):
        """
        Genera la tabla con datos y columnas de X reporte

        Args:
            columns (list(dict)): Columnas reporte.
            data (list(dict)): Datos reporte.

        Returns:
            Template construido con datos de reporte
        """
        date_time = global_date_format(now()) + ' ' + format_time(now())
        report_doctype = frappe.db.get_value('Report', self.report, 'ref_doctype')

        props_report = {
            'title': self.report,
            'description': self.description,
            'date_time': date_time,
            'columns': columns,
            'data': data,
            'report_url': get_url_to_report(self.report, self.report_type, report_doctype),
            'report_name': self.report,
            'edit_report_settings': get_link_to_form('Report Automator', self.report)
        }

        return frappe.render_template(f'revelare/templates/{REPORT_TEMPLATES.get(self.template)}', props_report)

    @staticmethod
    def get_spreadsheet_data(columns, data):
        """Generador de excel"""
        out = [[_(df.label) for df in columns], ]
        for row in data:
            new_row = []
            out.append(new_row)
            for df in columns:
                if df.fieldname not in row: continue
                tester = frappe.format(row[df.fieldname], df, row)
                new_row.append(tester)
        return out

    @staticmethod
    def get_cols_report(columns, data):
        """Obtiene las columnas de x reporte"""
        out = [[_(df.fieldname) for df in columns], ]
        return out

    def get_file_name(self):
        """Retorna el nombre del archivo generado, para ser descargado desde el doctype"""
        return "{0}.{1}".format(self.report.replace(" ", "-").replace("/", "-"), self.format.lower())

    def prepare_dynamic_filters(self):
        """
        Por cada reporte que se genere, esta funcion generara dinamicamente los filtros en el frontend
        para que el usuario pueda ingresar los parametros del reporte.
        """
        self.filters = frappe.parse_json(self.filters)

        to_date = today()
        from_date_value = {
            'Daily': ('days', -1),
            'Weekly': ('weeks', -1),
            'Monthly': ('months', -1),
            'Quarterly': ('months', -3),
            'Half Yearly': ('months', -6),
            'Yearly': ('years', -1)
        }[self.dynamic_date_period]

        from_date = add_to_date(to_date, **{from_date_value[0]: from_date_value[1]})

        self.filters[self.from_date_field] = from_date
        self.filters[self.to_date_field] = to_date

    def send(self):
        """Envia por correo electronico el HTML/XLSX/CSV con los datos del reporte automatizado"""
        if self.filter_meta and not self.filters:
            frappe.throw(_("Please set filters value in Report Filter table."))

        data = self.get_report_content()
        if not data:
            return

        attachments = None
        if self.format == "HTML":
            message = data
        else:
            message = self.get_html_table()

        if not self.format=='HTML':
            attachments = [{
                'fname': self.get_file_name(),
                'fcontent': data
            }]

        frappe.sendmail(
            recipients = self.email_to.split(),
            subject = self.report,
            message = message,
            attachments = attachments,
            reference_doctype = self.doctype,
            reference_name = self.report
        )

    def dynamic_date_filters_set(self):
        return self.dynamic_date_period and self.from_date_field and self.to_date_field


@frappe.whitelist()
def download(name):
    """Descarga archivo"""
    auto_email_report = frappe.get_doc('Report Automator', name)
    auto_email_report.check_permission()
    data = auto_email_report.get_report_content()

    if not data:
        frappe.msgprint(_('No Data'))
        return

    frappe.local.response.filecontent = data
    frappe.local.response.type = "download"
    frappe.local.response.filename = auto_email_report.get_file_name()


@frappe.whitelist()
def send_now(name):
    """Enviar reporte"""
    auto_email_report = frappe.get_doc('Report Automator', name)
    auto_email_report.check_permission()
    auto_email_report.send()


def send_daily():
    """Funcion llamada desde hooks cada dia para chequear que reporte enviar"""

    current_day = calendar.day_name[now_datetime().weekday()]
    enabled_reports = frappe.get_all('Report Automator',
        filters={'enabled': 1, 'frequency': ('in', ('Daily', 'Weekdays', 'Weekly'))})

    for report in enabled_reports:
        auto_email_report = frappe.get_doc('Report Automator', report.name)

        # if not correct weekday, skip
        if auto_email_report.frequency == "Weekdays":
            if current_day in ("Saturday", "Sunday"):
                continue
        elif auto_email_report.frequency == 'Weekly':
            if auto_email_report.day_of_week != current_day:
                continue
        try:
            auto_email_report.send()
        except Exception as e:
            frappe.log_error(e, _('Failed to send {0} Report Automator').format(auto_email_report.name))


def send_monthly():
    """Funcion llamada desde hooks cada mes para chequear que reporte enviar"""
    for report in frappe.get_all('Report Automator', {'enabled': 1, 'frequency': 'Monthly'}):
        frappe.get_doc('Report Automator', report.name).send()


def make_links(columns, data):
    """Formatea cada columna de datos de X reporte con el tipo de dato que corresponda"""
    for row in data:
        for col in columns:
            if col.fieldtype == "Link" and col.options != "Currency":
                if col.options and row.get(col.fieldname):
                    row[col.fieldname] = get_link_to_form(col.options, row[col.fieldname])
            elif col.fieldtype == "Dynamic Link":
                if col.options and row.get(col.fieldname) and row.get(col.options):
                    row[col.fieldname] = get_link_to_form(row[col.options], row[col.fieldname])
            elif col.fieldtype == "Currency":
                row[col.fieldname] = frappe.format_value(row[col.fieldname], col)

    return columns, data

def update_field_types(columns):
    for col in columns:
        if col.fieldtype in  ("Link", "Dynamic Link", "Currency")  and col.options != "Currency":
            col.fieldtype = "Data"
            col.options = ""
    return columns


@frappe.whitelist()
def render_template_prev(opt, data_select={}):
    """
    Genera un template con data dummy para que el usuario puede seleccionar el que desee
    Args:
        opt (str): Template Name
        data_select (dict, optional): [description]. Defaults to {}.

    Returns:
        str: HTML
    """
    data_select = json.loads(data_select)
    props_report = {
        'title': data_select.get("name", ""),
        'description': data_select.get("description", ""),
        'date_time': data_select.get("date_time", ""),
        'columns': data_select.get("columns", ""),
        'data': data_select.get("data", ""),
        'report_url': data_select.get("report_url", ""),
        'report_name': data_select.get("report_name", ""),
        'edit_report_settings': data_select.get("edit_report_settings", "")
    }
    return frappe.render_template(f'revelare/templates/{REPORT_TEMPLATES.get(opt)}', props_report)


def filter_data_repo(columns_ref, cols, data):
    """
    Filtra la data original del reporte en funcion a los campos (columnas)
    fijados en la tabla hija `Columns Report`

    Args:
        columns_ref (list): Nombres de columnas a utilizar del reporte origin
        cols (list): Propiedades columnas origin report
        data (list): Datos reporte origen

    Returns:
        tuple: list, list
    """

    cols_ref = []
    [cols_ref.append(x.get("column_name")) for x in columns_ref]

    # De la data del reporte filtra solo aquellas columnas definidas en el doctype
    # siguiendo el orden por numero de fila
    new_cols = []
    for col_ref in cols_ref:
        for col_repo in cols:
            if col_ref in col_repo.get("fieldname"):
                new_cols.append((col_repo))

    # Filtra solo la data en funcion a las columnas definidas
    new_data = []
    # Recorre cada dict
    for key_dict_data in data:
        base_data = {}

        # Por cada valor en la lista
        for val_base in cols_ref:
            # Si el valor existe en el diccionario
            if val_base in key_dict_data:
                base_data.update({val_base: key_dict_data.get(val_base)})

        if base_data: new_data.append(base_data)

    return new_cols, new_data


@frappe.whitelist()
def colums_to_report(name):
    """Obtiene las columnas que conforman el reporte seleccionado, estos
    valores se cargaran a la tabla hija de custom columns"""
    auto_email_report = frappe.get_doc('Report Automator', name)
    auto_email_report.check_permission()
    data = list(auto_email_report.fields_to_child_table())

    return json.dumps(data)
