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
                    "Payment Entry-cash_flow",
                    "Journal Entry Account-inflow_component",
                    "Journal Entry Account-outflow_component",
                    "Payment Entry-inflow_component",
                    "Payment Entry-outflow_component",
                    "Address-shs_longitude", "Address-shs_latitude", "Address-geo_location",
                    "Address-leaflet_map", "Address-address_geo_location",
                    "Address-waze_permalink", "Address-waze_lat", "Address-waze_lon",
                    "Address-waze_map",
                    # "Address-waze_map_iframe"
                ]
            ]
        ]
    }

    translation = {
        "dt": "Translation", "filters": [
            [
                "source_text", "in", [
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
                    "Sales Estimates",
                    "Target Warehouse",
                    "Allocated",
                    "Outstanding",
                    "Cash Effect",
                    "1 - Company",
                    "A - Operations",
                    "A.1 - Cash Payment for Operating Expenses",
                    "A.1.1 - Cash Payments to Employees",
                    "A.1.1.1 - Standard Payroll Payments",
                    "A.1.1.2 - Bonus Payroll Payments",
                    "A.1.2 - Cash Payments for Severance or Retirement",
                    "A.1.2.1 - Payments for Retirement",
                    "A.1.2.2 - Payments for Severance",
                    "A.1.3 - Cash Payments for Taxes",
                    "A.1.3.1 - Payments for Sales Taxes",
                    "A.1.3.2 - Payments for Payroll Taxes",
                    "A.1.3.3 - Payments for Property Taxes",
                    "A.1.3.4 - Payments for Other Taxes",
                    "A.1.3.5 - Payments for Income Taxes",
                    "A.1.4 - Cash Payments to Suppliers",
                    "A.1.4.1 - Merchandise or Raw Material payments to Suppliers",
                    "A.1.4.2 - Operating Expense payments to Suppliers",
                    "A.1.5 - Cash Receipts from Customers",
                    "A.1.5.1 - Receipts from sales of goods and services",
                    "A.1.6 - Interest and Dividends Received",
                    "A.1.6.2 - Coupons Received from Bonds",
                    "A.1.6.3 - Interest Received from Investment",
                    "B - Investment",
                    "B.1 - Board Compensation Cash Flows",
                    "B.1.1 - Board Compensation from Participation Interest",
                    "B.2 - Cash Flows of Taxes Related to Investing Activities",
                    "B.2.1 - Cash Payments for Taxes Related to Investing",
                    "B.3 - Fixed Asset Cash Flows",
                    "B.3.1 - Purchases of fixed assets (Property, Plant & Equipment)",
                    "B.3.2 - Sale of fixed assets (Property, Plant & Equipment)",
                    "B.3.3 - Net Investment (CAPEX)",
                    "B.4 - Loans Given to Others",
                    "B.4.1 - Money Lent to Individuals",
                    "B.4.2 - Money Lent to Institutions",
                    "B.5 - Long-term Securities Cash Flows",
                    "B.5.1 - Investment in long-term securities (stocks or bonds)",
                    "B.5.2 - Sale of long-term securities (stocks or bonds)",
                    "C - Financing",
                    "C.1 - Debt Service",
                    "C.1.1 - Coupon Payments",
                    "C.1.1.1 - Interest Expenses",
                    "C.1.1.2 - Coupon or Interest Receipts",
                    "C.1.1.3 - Coupon Amortization",
                    "C.1.2 - Financial Insitutions Flows",
                    "C.1.2.1 - Financial Insitutions Transaction Fees",
                    "C.1.3 - Loans Obtained from Others",
                    "C.1.3.1 - Money Loaned from Individuals",
                    "C.1.3.2 - Money Loaned from Institutions",
                    "C.1.3.3 - Receipts from Issue of Bonds",
                    "C.1.3.4 - Debt Repayment for Individuals",
                    "C.1.3.5 - Debt Repayment for Institutions",
                    "C.1.3.6 - Payments for Bond Cancellations",
                    "C.1.4 - Shares (Stock)",
                    "C.1.4.1 - Dividend Payments",
                    "C.1.4.2 - New Stock Issue",
                    "C.1.4.3 - Capital Increase",
                    "C.1.4.4 - Stock Repurchases",
                    "C.1.5 - Other Financial Flows",
                    "Direct Cash Flow Component",
                    "Component Name",
                    "Parent Component",
                    "Cash Effect",
                    "Inflow Component",
                    "Inflow",
                    "Outflow",
                    "Outflow Component"
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
        "dt": "Direct Cash Flow Component"
    }


    # NEW FUNCTIONALITY FOR EXPORTING
    fixtures_fillup.append(custom_field)
    fixtures_fillup.append(translation)
    fixtures_fillup.append(dcf_component)

    # fixtures_fillup.append(tax_category)
    # fixtures_fillup.append(id_doctype)

    return fixtures_fillup

# fixtures = fill_fixtures()
