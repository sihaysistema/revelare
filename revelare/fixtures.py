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
                    "Purchase Invoice-facelec_tax_retention_guatemala",
                    "Sales Invoice-facelec_tax_retention_guatemala"
                ]
            ]
        ]
    }

    translation = {
        "dt": "Translation", "filters": [
            [
                "source_name", "in", [
                    "Amount UOM"
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

    # NEW FUNCTIONALITY FOR EXPORTING
    # fixtures_fillup.append(custom_field)
    fixtures_fillup.append(translation)
    # fixtures_fillup.append(tax_category)
    # fixtures_fillup.append(id_doctype)

    return fixtures_fillup

# fixtures = fill_fixtures()
