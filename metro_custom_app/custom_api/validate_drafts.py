import frappe
from frappe import _

def validate_sales_invoice(doc, method):
    items_with_insufficient_stock = []
    for item in doc.items:
        maintain_stock = frappe.get_value("Item", item.item_code, "is_stock_item")
        if item.qty > item.actual_qty and maintain_stock:
            item_doc = frappe.get_doc("Item", item.item_code)
            items_with_insufficient_stock.append({
                "item_code": item.item_code,
                "item_name": item_doc.item_name,
                "warehouse": item.warehouse,
                "qty_needed": item.qty - item.actual_qty
            })

    if items_with_insufficient_stock:
        error_message = ""
        for item in items_with_insufficient_stock:
            error_message += f"Item Code: <b>{item['item_code']}</b><br>Warehouse: <b>{item['warehouse']}</b><br>Qty Needed: {item['qty_needed']}<br>"

        frappe.msgprint(_(f"Insufficient Stock For: <br>{error_message}"), raise_exception=True)

# Enable HTML rendering in messages
frappe.local.flags.error_message_html = True
