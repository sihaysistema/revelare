vat_payable_data = frappe.db.sql(f"""
 SELECT posting_date AS trans_date, voucher_type AS doc_type, voucher_no AS doc_id,
 debit_in_account_currency AS vat_debit, credit_in_account_currency AS vat_credit, account_currency AS currency
 FROM `tabGL Entry` WHERE company='{filters.company}'
 AND account='{vat_acct_payable}'
 AND MONTH(posting_date) = '{MONTHS_MAP.get(filters.month)}' AND YEAR(posting_date) = '{filters.year}'
 """, as_dict=1)

return vat_payable_data