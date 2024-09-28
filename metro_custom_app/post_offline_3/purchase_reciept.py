import json
import requests
import frappe
from datetime import datetime
from metro_custom_app.utils import get_api_keys2  # Import the function to fetch API keys

class PurchaseReceiptItem:
    def __init__(self, item_code, qty, expense_account, warehouse,rate):
        self.item_code = item_code
        self.qty = qty
        self.rate = rate
        self.expense_account = expense_account
        self.warehouse = warehouse

    def to_dict(self):
        return {
            "item_code": self.item_code,
            "qty": self.qty,
            "rate": self.rate,
            "expense_account": self.expense_account,
            "warehouse": self.warehouse,
        }

def ensure_supplier_exists(supplier, headers, server):
    try:
        response = requests.get(f"{server}/Supplier/{supplier}", headers=headers)
        if response.status_code == 404:
            supplier_data = {
                "doctype": "Supplier",
                "supplier_name": supplier,
                "supplier_type": "Company",  # Modify this as per your requirements
                "supplier_group": "All Supplier Groups"  # Example field
                
            }
            response = requests.post(f"{server}/Supplier", headers=headers, data=json.dumps(supplier_data))
            response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise

def ensure_item_exists(item_code, headers, server):
    try:
        response = requests.get(f"{server}/Item/{item_code}", headers=headers)
        if response.status_code == 404:
            item_data = {
                "doctype": "Item",
                "item_code": item_code,
                "item_name": item_code,  # Typically the same as item_code
                "item_group": "All Item Groups",  # Modify this as per your requirements
                "stock_uom": "Nos",  # Modify this as per your requirements
                "description": "Auto-created item"  # Example field
            }
            response = requests.post(f"{server}/Item", headers=headers, data=json.dumps(item_data))
            response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise

@frappe.whitelist()
def post_purchase_receipts(docname):
    try:
        api_keys = get_api_keys2()  
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        purchase_receipt = frappe.get_doc("Purchase Receipt", docname)
        # Check if the Purchase Receipt has already been posted
        if purchase_receipt.custom_voucher_no_3:
            frappe.msgprint("Purchase Receipt has already been posted.")
            return

        # Convert date fields to strings
        purchase_receipt.posting_date = datetime.strftime(purchase_receipt.posting_date, "%Y-%m-%d")

        # Convert items to a list of dictionaries
        items = []
        for item in purchase_receipt.items:
            item_dict = {
                "item_code": item.item_code,
                "qty": item.qty,
                "rate": item.rate,
                "expense_account": item.expense_account,
                "warehouse": item.warehouse
            }
            items.append(item_dict)

        post_data = {
            "supplier": purchase_receipt.supplier,
            "posting_date": purchase_receipt.posting_date,
            "posting_time": str(purchase_receipt.posting_time),
            "company": purchase_receipt.company,
            "set_warehouse": purchase_receipt.set_warehouse,
            "supplier_delivery_note": purchase_receipt.supplier_delivery_note,
            "docstatus": 1,
            "custom_voucher_no": docname,
            "items": items
        }

        json_data = json.dumps(post_data)

        # Make the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://168.253.118.177/api/resource"

        # Ensure the supplier exists
        ensure_supplier_exists(purchase_receipt.supplier, headers, server)

        # Ensure each item exists
        for item in items:
            ensure_item_exists(item["item_code"], headers, server)

        # Remove the 'Expect' header
        headers.pop('Expect', None)

        post_response = requests.post(f"{server}/Purchase%20Receipt", headers=headers, data=json_data)

        # Check the response
        post_response.raise_for_status()
        posted_receipt = post_response.json().get("data", {}).get("name")

        # Update the document status
        if posted_receipt:
            frappe.db.set_value("Purchase Receipt", docname, "custom_voucher_no_3", posted_receipt)
            # frappe.db.set_value("Purchase Receipt", docname, "custom_post_status", "Receipt Posted")
            frappe.msgprint("Purchase Receipt submitted successfully to the server")
        else:
            frappe.db.set_value("Purchase Receipt", docname, "custom_post_status", "Receipt Not Posted")
            frappe.msgprint("Failed to post Purchase Receipt")

    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to fetch or process data: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to fetch or process data: {err}")
