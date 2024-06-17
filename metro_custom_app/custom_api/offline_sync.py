# import requests
# import frappe
# from frappe.utils.background_jobs import enqueue
# from datetime import timedelta
# import json

# def mark_invoices_as_paid():
#     invoices = frappe.db.sql("""
#         SELECT name, grand_total, paid_amount,outstanding_amount
#         FROM `tabSales Invoice`
#         WHERE docstatus = 1
#     """, as_dict=True)

#     for invoice in invoices:
#         if invoice['grand_total'] == invoice['paid_amount']:
#             frappe.db.set_value('Sales Invoice', invoice['name'], 'status', 'Paid')
#             print(f"Sales Invoice {invoice['name']} status updated to Paid")

#     frappe.db.commit()
#     enqueue("offline_posting.custom_api.sales_invoice.mark_invoices_as_paid", queue='long')

# def check_internet():
#     try:
#         requests.get("http://www.google.com", timeout=5)
#         frappe.db.set_value("System Settings", None, "custom_internet_available", 1)
#         frappe.db.commit()
#         mark_invoices_as_paid()
#     except requests.RequestException:
#         frappe.db.set_value("System Settings", None, "custom_internet_available", 0)
#         frappe.db.commit()
# # Schedule check_internet function to run every 10 seconds
# enqueue("offline_posting.custom_api.sales_invoice.check_internet", queue='long')

# check_internet()  # Start the check_internet loop

