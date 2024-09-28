import frappe
from frappe.model.document import Document

def update_custom_status(doc, method):
    try:
        # Check if custom_status field is not set or different from status
        if doc.custom_status != doc.status:
            # Update the custom_status field with the status value
            doc.custom_status = doc.status
            doc.save()
            frappe.db.commit()
            # frappe.msgprint(f"Custom status updated to {doc.status}")
    except Exception as e:
        # Log the error instead of throwing it
        frappe.log_error(f"Error updating custom status: {str(e)}", "Custom Status Update Error")

        



