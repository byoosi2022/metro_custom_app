import frappe
from frappe.utils import get_link_to_form

@frappe.whitelist()
def make_payment_for_invoice(invoice_id, amount):
    # Check if the invoice exists
    if not frappe.db.exists("Purchase Invoice", invoice_id):
        return f"Purchase Invoice {invoice_id} not found"

    # Get supplier and account details
    invoice = frappe.get_doc("Purchase Invoice", invoice_id)
    supplier = invoice.supplier
    paid_to = invoice.credit_to
    co = invoice.company
    paid_from_account_currency = frappe.db.get_value("Account", paid_to, "account_currency")

    # Create a new payment entry
    payment_entry_data = {
        "doctype": "Payment Entry",
        "company": co,
        "payment_type": "Pay",
        "mode_of_payment": "Cash",  # Assuming payment is made in cash
        "posting_date": frappe.utils.nowdate(),
        "party_type": "Supplier",
        "party": supplier,
        "paid_amount": amount,
        "received_amount": amount,
        "paid_from": "11110 - Cash - MACL",  # Update with your cash account
        "paid_to": paid_to,
    }

    # Create the payment entry
    payment_entry = frappe.get_doc(payment_entry_data)
    payment_entry.insert()
    frappe.db.commit()

    # Create Payment Entry Reference
    payment_reference = frappe.get_doc({
        "doctype": "Payment Entry Reference",
        "parenttype": "Payment Entry",
        "parentfield": "references",
        "parent": payment_entry.name,
        "reference_doctype": "Purchase Invoice",
        "reference_name": invoice_id,
        "reference_date": invoice.posting_date,
        "total_amount": invoice.grand_total,
        "outstanding_amount": invoice.outstanding_amount,
        "allocated_amount": amount,
        "currency": paid_from_account_currency,
        "exchange_rate": 1.0
    })
    payment_reference.insert()
    frappe.db.commit()

    # Get the link to the payment entry
    # payment_entry_link = get_link_to_form("Payment Entry", payment_entry.name)
    
    # Display a message with the link
    # frappe.msgprint(f"Payment of {amount} Naira made for invoice {invoice_id}. Payment Entry: {payment_entry_link}")

    return payment_entry.name
