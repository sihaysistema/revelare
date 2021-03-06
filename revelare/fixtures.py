# -*- coding: utf-8 -*-
#  Si Hay Sistema and Contributors 2020
from __future__ import unicode_literals
from . import __version__ as app_version

"""
en-US: Make sure all fields that are coming from another branch and the new fields you require are added to the fixtures
list.
es-GT: Asegurate que todos los fixtures que vengan de otra rama y los
nuevos fixtures que estes creando se agreguen al listado fixtures.

"""


def fill_fixtures():
    # We declare fixtures as an empty list.
    fixtures_fillup = []

    # Add the corresponding fields to the fixture objects
    # if the object does not exist, simply create it and copy accordingly.

    custom_field = {
        "dt": "Custom Field", "filters": [
            [
                "name", "in", [
                    "Item-availability_estimates",
                    "Item-include_in_estimations",
                    "Item-column_break_estimations",
                    "Item-estimation_uom",
                    "Item-estimation_name",
                    "Payment Entry-direct_cash_flow_component",
                    "Payment Entry-cash_flow",
                    "Journal Entry Account-inflow_component",
                    "Journal Entry Account-outflow_component"
                ]
            ]
        ]
    }

    translation = {
        "dt": "Translation", "filters": [
            [
                "source_name", "in", [
                    "Amount UOM",
                    "Estimated Items and Quantities Available",
                    "Estimated Available Items",
                    "Availability Estimates",
                    "Estimation Name",
                    "Item Availability Estimate Importer",
                    "Include in Estimations",
                    "Estimation UOM",
                    "REVELARE: Only for Items used as materials in Bill of Materials (BOM) or Items marked for sale If checked, Item will be included automatically in the Sales Item Availability Report.",
                    "REVELARE: Default Unit of Measure to be used in Item Availability Estimates. Applies only to Material Items, not for Sales Items.",
                    "REVELARE: Name to be displayed as a header for Sales Item groupings used in Sales Item Availability Report.",
                    "Sales Item Availability",
                    "Show sales adjustments",
                    "Obtain sales adjustments from",
                    "Item Availability Estimate",
                    "Valid from this date",
                    "Until this date",
                    "Estimate Validity Interval",
                    "Days",
                    "Interval duration in days",
                    "Code",
                    "Name",
                    "Possible",
                    "UOM",
                    "Sold",
                    "Available",
                    "Revelare Configuration",
                    "Configuration",
                    "Pound",
                    "Sales Estimates"
                ]
            ]
        ]
    }

    tax_category = {
        "dt": "Tax Category", "filters": [
            [
                "title", "in", [
                    "SAT: Entidad Publica",
                    "SAT: Exportador"
                ]
            ]
        ]
    }

    id_doctype = {
        "dt": "Identification Document Type", "filters": [
            [
                "identification_document_type", "in", [
                    "PAS"
                ]
            ]
        ]
    }

    dcf_component = {
        "dt": "Direct Cash Flow Component", "filters": [
            [
                "direct_cash_flow_component_name", "in", [
                    "Operations",
                    "Cash Payment for Operating Expenses",
                    "Bonus Payroll Payments",
                    "Bonus Payroll Payment",
                    "Standard Payroll Payments",
                    "Cash Payments for Taxes",
                    "Payments for Income Taxes",
                    "Payments for Payroll Taxes",
                    "Payments for Property Taxes",
                    "Payments for Sales Taxes",
                    "Cash Payments to Suppliers",
                    "Payments to Suppliers",
                    "Cash Receipts from Customers",
                    "Receipts from Customers",
                    "Cash Payments for Severance or Retirement",
                    "Payments for Retirement",
                    "Payments for Severance",
                    "Dividends Received",
                    "Dividends Received from Investment",
                    "Investment",
                    "Fixed Asset Cash Flows",
                    "Purchases of fixed assets (Property, Plant & Equipment)",
                    "Sale of fixed assets (Property, Plant & Equipment)",
                    "Long-term Securities Cash Flows",
                    "Investment in long-term securities (stocks or bonds) ",
                    "Sale of long-term securities (stocks or bonds)",
                    "Loans Given to Others",
                    "Money Lent to Individuals",
                    "Money Lent to Institutions",
                    "Cash Payments for Taxes Related to Investing",
                    "Cash Flows of Taxes Related to Investing Activities",
                    "Board Compensation Cash Flows",
                    "Board Compensation from Participation Interest",
                    "Uncategorized Inflows",
                    "Uncategorized Outflows",
                    "Interest Received from Investment",
                    "Financing",
                    "Loans Obtained from Others",
                    "Money Loaned from Individuals",
                    "Money Loaned from Institutions",
                    "Debt Service",
                    "Coupon Payments",
                    "Debt Repayment",
                    "Interest Expenses",
                    "Financial Institution Flows",
                    "Financial Institution Transaction Fees",
                    "Loans Obtained from Others",
                    "Money Loaned from Individuals",
                    "Money Loaned from Institutions",
                    "Stock",
                    "Dividend Payments",
                    "New Stock Issue",
                    "Stock Repurchases"
                ]
            ]
        ]
    }


    # NEW FUNCTIONALITY FOR EXPORTING
    fixtures_fillup.append(custom_field)
    fixtures_fillup.append(translation)
    fixtures_fillup.append(dcf_component)
    # fixtures_fillup.append(tax_category)
    # fixtures_fillup.append(id_doctype)

    return fixtures_fillup

# fixtures = fill_fixtures()
