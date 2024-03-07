import frappe
from frappe.utils import get_url_to_form

def create_purchase_invoice(doc, method):
    if doc.sales_partner:
        purchase_invoice = frappe.new_doc('Purchase Invoice')
        purchase_invoice.supplier = doc.sales_partner
        purchase_invoice.company = doc.company  # Set the company
        purchase_invoice.append('items', {
            'item_code': 'Commission',
            'rate': doc.total_commission,
            'qty': 1
        })
        purchase_invoice.save()
        # purchase_invoice.submit()
        
        # Get the URL to the Purchase Invoice form
        purchase_invoice_url = get_url_to_form('Purchase Invoice', purchase_invoice.name)
        
        # Show message with Purchase Invoice ID and link at the bottom
        frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created. <a href='{purchase_invoice_url}'>View Purchase Invoice</a>", alert=True)

import json
@frappe.whitelist()
def populate_other_charges_lease(doc):
    if isinstance(doc, str):
        doc = json.loads(doc)
    item_tax_templates = frappe.get_all(
        "Item Tax Template Detail",
        filters={"parent": doc['charge_type']},
        fields=["tax_type", "tax_rate"]
    )

    return item_tax_templates

def create_purchase_invoice_landlord(doc, method):
    if doc.custom_land_name:
        purchase_invoice = frappe.new_doc('Purchase Invoice')
        purchase_invoice.supplier = doc.custom_land_name
        purchase_invoice.company = doc.company  # Set the company

        # Fetch custom items from Sales Invoice Item
        lease = frappe.get_doc("Sales Invoice", doc.name)
        for item in lease.get("items"):
            if item.item_code == "Rent Fee":
                purchase_invoice.append('items', {
                    'item_code': item.item_code,
                    'rate': item.rate,
                    'qty': 1
                })
        
        purchase_invoice.save()
        # purchase_invoice.submit()  # Uncomment if you want to submit the invoice automatically

        # Get the URL to the Purchase Invoice form
        purchase_invoice_url = get_url_to_form('Purchase Invoice', purchase_invoice.name)

        # Show message with Purchase Invoice ID and link at the bottom
        frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created for landlord. <a href='{purchase_invoice_url}'>View Purchase Invoice</a>", alert=True)

@frappe.whitelist()
def populate_lease_invoice_schedule(lease_name):
    lease = frappe.get_doc("Lease", lease_name)
    for lease_item in lease.lease_item:
        existing_schedule = frappe.db.exists(
            "Lease Invoice Schedule",
            {
                "parent": lease_name,
                "parentfield": "lease_invoice_schedule",
                "lease_item": lease_item.lease_item
            }
        )
        if existing_schedule:
            frappe.msgprint(f"Skipping {lease_item.lease_item} as it already exists in the Lease Invoice Schedule")
            continue

        lease_invoice_schedule = frappe.new_doc("Lease Invoice Schedule")
        lease_invoice_schedule.parent = lease_name
        lease_invoice_schedule.parenttype = "Lease"
        lease_invoice_schedule.parentfield = "lease_invoice_schedule"
        lease_invoice_schedule.date_to_invoice = lease.lease_date
        lease_invoice_schedule.lease_item = lease_item.lease_item
        lease_invoice_schedule.document_type = "Sales Invoice"
        lease_invoice_schedule.qty = 1
        lease_invoice_schedule.lease_item_name = lease_item.lease_item
        lease_invoice_schedule.rate = lease_item.amount
        lease_invoice_schedule.paid_by = lease_item.paid_by 
        lease_invoice_schedule.insert()

    frappe.msgprint("Lease Invoice Schedule updated successfully")







