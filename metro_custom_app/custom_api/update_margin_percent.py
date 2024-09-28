import frappe # type: ignore
from frappe import _ # type: ignore

@frappe.whitelist()
def profit_margin_percentage(doc, method):
    try:
        for item in doc.get("items"):
            item_code = item.get("item_code")
            custom_sales_price = item.get("custom_sales_price")
            profit_margin_percentage = item.get("custom_profit_margin")

            # Update custom_profit_margin for the item
            frappe.db.set_value("Item", item_code, {
                "custom_profit_margin": profit_margin_percentage,
                "custom_sales_price":custom_sales_price
            })
            frappe.db.commit()

        # frappe.msgprint(_("Profit margins updated successfully."))

    except Exception as e:
        frappe.log_error(f"Failed to update profit margins: {e}")
        frappe.throw(_("Failed to update profit margins. Please try again."))

@frappe.whitelist()
def get_custom_profit_margin(item_code):
    item = frappe.get_doc("Item", item_code)
    if item:
        return {"margin":item.custom_profit_margin, "sales_price":item.custom_sales_price}
    return None, None



