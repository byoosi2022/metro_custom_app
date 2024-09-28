import frappe
from frappe.utils import get_url_to_form

def create_purchase_invoice(doc, method):
    if doc.sales_partner:
        try:
            # Create a new Purchase Invoice document
            purchase_invoice = frappe.new_doc('Purchase Invoice')
            
            # Set fields for the Purchase Invoice
            purchase_invoice.supplier = doc.sales_partner
            purchase_invoice.custom_sales_partner = doc.sales_partner
            purchase_invoice.custom_court = doc.custom_court
            purchase_invoice.custom_commission_rate = doc.commission_rate
            purchase_invoice.company = doc.company  # Set the company
            purchase_invoice.custom_invoice_grand_total = doc.grand_total
            
            # Set Sales Invoice ID or Sales Order ID based on the document type
            if doc.doctype == "Sales Invoice":
                purchase_invoice.custom_sales_invoice_id = doc.name
            elif doc.doctype == "Sales Order":
                purchase_invoice.custom_sales_order_id = doc.name

            # Append commission item to the Purchase Invoice
            purchase_invoice.append('items', {
                'item_code': 'Commission',
                'rate': doc.total_commission,
                'qty': 1
            })
            
            # Save the Purchase Invoice
            purchase_invoice.save()
            
            # Optionally, submit the Purchase Invoice
            # purchase_invoice.submit()
            
            # Get the URL to the newly created Purchase Invoice
            purchase_invoice_url = get_url_to_form('Purchase Invoice', purchase_invoice.name)
            
            # Show a message with a link to view the Purchase Invoice
            frappe.msgprint(f"Purchase Invoice {purchase_invoice.name} created. <a href='{purchase_invoice_url}'>View Purchase Invoice</a>", alert=True)

        except Exception as e:
            # Show an error message if something goes wrong
            frappe.msgprint(f"Error creating Purchase Invoice: {str(e)}", alert=True)
            # Optionally log the error for debugging
            frappe.log_error(f"Error creating Purchase Invoice: {str(e)}", "Purchase Invoice Creation Error")

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
        purchase_invoice.custom_invoice_grand_total = doc.grand_total
        purchase_invoice.custom_customer_name = doc.customer

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
    
import frappe
from frappe.utils import nowdate
@frappe.whitelist()
def create_payment_entry(purchase_invoice, amount_paid, amount_approved, lease_invoice, source_exchange_rate=1.0):
    # Get account and currency from Purchase Invoice
    supplier = frappe.db.get_value("Purchase Invoice", purchase_invoice, "supplier")
    paid_to = frappe.db.get_value("Purchase Invoice", purchase_invoice, "credit_to")
    project = frappe.db.get_value("Purchase Invoice", purchase_invoice, "project")
    co = frappe.db.get_value("Purchase Invoice", purchase_invoice, "company")
    cost_center = frappe.db.get_value("Purchase Invoice", purchase_invoice, "cost_center")
    paid_from_account_currency = frappe.db.get_value("Account", paid_to, "account_currency")

    # Calculate total outstanding amount for the supplier
    total_outstanding_amount = get_supplier_outstanding_amount(supplier)

    # Create Payment Entry
    payment_entry = frappe.get_doc({
        "doctype": "Payment Entry",
        "payment_type": "Pay",
        "company": co,
        "custom_requisition_id": lease_invoice,
        "posting_date": nowdate(),
        "party_type": "Supplier",
        "party": supplier,
        "paid_amount": amount_approved,
        "received_amount": amount_approved,
        "paid_to": paid_to,
        "paid_from_account_currency": paid_from_account_currency,
        "paid_from": "11110 - Cash - MACL",
        "exchange_rate": source_exchange_rate,
        "source_exchange_rate": source_exchange_rate,
        "project": project,
        "cost_center": cost_center,
        "total_allocated_amount":amount_approved,
        "party_balance": -1 * total_outstanding_amount  # Update Party Balance as negative
    })

    # Save Payment Entry
    payment_entry.insert()
   
    # Create Payment Entry Reference
    payment_reference = frappe.get_doc({
        "doctype": "Payment Entry Reference",
        "parenttype": "Payment Entry",
        "parentfield": "references",
        "parent": payment_entry.name,
        "reference_doctype": "Purchase Invoice",
        "reference_name": purchase_invoice,
        "total_amount": amount_paid,
        "outstanding_amount": amount_paid,
        "allocated_amount": amount_approved,
        "exchange_rate": 1.0
    })
    payment_reference.insert()

    frappe.db.commit()

    return payment_entry.name

def get_supplier_outstanding_amount(supplier):
    outstanding_invoices = frappe.get_all(
        "Purchase Invoice",
        filters={"supplier": supplier, "docstatus": 1},
        fields=["outstanding_amount"],
    )
    total_outstanding = sum(
        [float(d.get("outstanding_amount", 0)) for d in outstanding_invoices]
    )
    return total_outstanding


@frappe.whitelist()
def get_all_customers():
    try:
        customers = frappe.db.get_all("Customer", fields=["name", "customer_name", "customer_type", "customer_group", "territory"])
        frappe.msgprint("Customers fetched successfully")
        return {
            "message": "Customers fetched successfully",
            "data": customers
        }
    except Exception as e:
        frappe.log_error(f"Failed to fetch customers: {e}")
        frappe.msgprint(f"Failed to fetch customers: {e}")
        return {
            "message": f"Failed to fetch customers: {e}",
            "data": None
        }
        
@frappe.whitelist()
def get_all_suppliers():
    try:
        suppliers = frappe.db.get_all("Supplier", fields=["name", "supplier_name","custom_company", "supplier_type", "supplier_group", "country"])
        frappe.msgprint("Suppliers fetched successfully")
        return {
            "message": "Suppliers fetched successfully",
            "data": suppliers
        }
    except Exception as e:
        frappe.log_error(f"Failed to fetch suppliers: {e}")
        frappe.msgprint(f"Failed to fetch suppliers: {e}")
        return {
            "message": f"Failed to fetch suppliers: {e}",
            "data": None
        }
        
@frappe.whitelist()
def get_all_customers_filters(name=None):
    try:
        filters = {}
        if name:
            filters["name"] = name

        customers = frappe.get_list("Customer", filters=filters, fields=["name", "customer_name", "customer_type", "customer_group", "territory"])
        frappe.msgprint("Customers fetched successfully")
        return {
            "message": "Customers fetched successfully",
            "data": customers
        }
    except Exception as e:
        frappe.log_error(f"Failed to fetch customers: {e}")
        frappe.msgprint(f"Failed to fetch customers: {e}")
        return {
            "message": f"Failed to fetch customers: {e}",
            "data": None
        }
        
@frappe.whitelist()
def get_all_users():
    try:
        users = frappe.db.get_all("User", fields=["name", "email", "full_name"])
        frappe.msgprint("Users fetched successfully")
        return {
            "message": "Users fetched successfully",
            "data": users
        }
    except Exception as e:
        frappe.log_error(f"Failed to fetch users: {e}")
        frappe.msgprint(f"Failed to fetch users: {e}")
        return {
            "message": f"Failed to fetch users: {e}",
            "data": None
        }

@frappe.whitelist()
def get_all_items_filters(item_code=None):
    try:
        filters = {}
        if item_code:
            filters["item_code"] = item_code

        items = frappe.get_list("Item", filters=filters, fields=["name", "item_name","item_code", "item_group"])
        frappe.msgprint("Items fetched successfully")
        return {
            "message": "Items fetched successfully",
            "data": items
        }
    except Exception as e:
        frappe.log_error(f"Failed to fetch items: {e}")
        frappe.msgprint(f"Failed to fetch items: {e}")
        return {
            "message": f"Failed to fetch items: {e}",
            "data": None
        }






