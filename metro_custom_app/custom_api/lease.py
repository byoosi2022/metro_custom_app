import frappe
from frappe import _

import frappe
from frappe import _

@frappe.whitelist()
def create_sales_invoice_from_lease(lease_name):
    # Fetch the Lease document
    lease = frappe.get_doc("Lease", lease_name)
   
    # Create Sales Invoice
    sales_invoice = frappe.new_doc("Sales Invoice")
    sales_invoice.due_date = lease.get("end_date")
    sales_invoice.posting_date = lease.get("lease_date")
    
    # Fetch custom items from Lease Invoice Schedule
    for schedule in lease.get("lease_invoice_schedule"):
        customer = frappe.get_value("Customer", {"name": schedule.get("paid_by")}, "custom_landlord_name")
        si_customer = frappe.get_value("Customer", {"name": schedule.get("paid_by")}, "name")
        if not customer:
            frappe.throw(_("Customer not found for paid_by: {}").format(schedule.get("paid_by")))

        sales_invoice.customer = si_customer
        sales_invoice.custom_land_name = customer
        sales_invoice.company = lease.company
        sales_invoice.append("items", {
            "item_code": schedule.get("lease_item_name"),
            "qty": schedule.get("qty"),
            "rate": schedule.get("rate"),
            "item_tax_template": lease.charge_type
        })
        
        # Update tax child table in the Sales Invoice
        item_tax_template = frappe.get_all(
            "Other Charges On Lease",
            filters={"parent": lease.name},
            fields=["item", "percentage", "amount"]
        )
        
        if item_tax_template:
            for tax_detail in item_tax_template:
                if tax_detail.percentage == 0:
                    charge_type = "Actual"
                else:
                    charge_type = "On Net Total"

                tax_row = sales_invoice.append("taxes", {})
                tax_row.charge_type = charge_type
                tax_row.account_head = tax_detail.item
                tax_row.description = tax_detail.item
                tax_row.tax_rate = tax_detail.percentage
                tax_row.tax_amount = tax_detail.amount

    # Save and submit the Sales Invoice
    sales_invoice.insert(ignore_permissions=True)
    # sales_invoice.submit()

    frappe.msgprint(_("Sales Invoice {} created successfully.").format(sales_invoice.name))

    # Update invoice_number field in Lease Invoice Schedule
    for schedule in lease.get("lease_invoice_schedule"):
        frappe.db.set_value("Lease Invoice Schedule", schedule.name, "invoice_number", sales_invoice.name)

    return sales_invoice.name
