import json
import requests
import frappe
from datetime import datetime
from metro_custom_app.utils import get_api_keys  # Import the function to fetch API keys

class StockReconciliationItem:
    def __init__(self, item_code, qty, warehouse, valuation_rate):
        self.item_code = item_code
        self.qty = qty
        self.warehouse = warehouse
        self.valuation_rate = valuation_rate

    def to_dict(self):
        return {
            "item_code": self.item_code,
            "qty": self.qty,
            "warehouse": self.warehouse,
            "valuation_rate": self.valuation_rate
        }

@frappe.whitelist()
def post_stock_reconciliation(docname):
    try:
        api_keys = get_api_keys()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        stock_reconciliation = frappe.get_doc("Stock Reconciliation", docname)
        # Check if the Stock Entry has already been posted
        if stock_reconciliation.custom_voucher_no_server2:
            frappe.msgprint("Stock reconciliation has already been posted.")
            return

        # Convert date fields to strings
        stock_reconciliation.posting_date = datetime.strftime(stock_reconciliation.posting_date, "%Y-%m-%d")

        # Convert items to a list of dictionaries
        items = []
        for item in stock_reconciliation.items:
            item_dict = {
                "item_code": item.item_code,
                "qty": item.qty,
                "warehouse": item.warehouse,
                "valuation_rate": item.valuation_rate if hasattr(item, 'valuation_rate') else 0  # Use 0 if valuation_rate is not present
            }

            # Check if the item exists on the server and update if necessary
            if not check_and_update_item(api_keys, item_dict):
                create_item(api_keys, item_dict)
            
            items.append(item_dict)

        post_data = {
            "posting_date": stock_reconciliation.posting_date,
            "company": stock_reconciliation.company,
            "purpose": stock_reconciliation.purpose,
            "expense_account": stock_reconciliation.expense_account,
            "cost_center": stock_reconciliation.cost_center,
            "set_warehouse": stock_reconciliation.set_warehouse,
            "warehouse": stock_reconciliation.warehouse,
            "custom_voucher_no": docname,
            "docstatus": 1,
            "items": items
        }

        json_data = json.dumps(post_data)

        # Make the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://102.22.220.246/api/resource/Stock%20Reconciliation"
        post_response = requests.post(server, headers=headers, data=json_data)

        # Log the server response content
        if post_response.status_code != 200:
            frappe.log_error(post_response.text[:1000], "Server Response")  # Log only the first 1000 characters
            frappe.throw(f"Server responded with an error: {post_response.status_code}")

        # Check the response
        post_response.raise_for_status()
        posted_reconciliation = post_response.json().get("data", {}).get("name")

        # Update the document status
        if posted_reconciliation:
            frappe.db.set_value("Stock Reconciliation", docname, "custom_voucher_no_server2", posted_reconciliation)
            frappe.db.set_value("Stock Reconciliation", docname, "custom_post_status", "Reconciliation Posted")
            frappe.msgprint("Stock Reconciliation submitted successfully to the server")
        else:
            frappe.db.set_value("Stock Reconciliation", docname, "custom_post_status", "Reconciliation Not Posted")
            frappe.msgprint("Failed to post Stock Reconciliation")

    except requests.exceptions.HTTPError as e:
        frappe.log_error(f"HTTP error: {e.response.text[:1000]}")  # Log only the first 1000 characters
        frappe.throw(f"HTTP error: {e.response.text[:1000]}")  # Show only the first 1000 characters in the throw message
    except Exception as e:
        frappe.log_error(f"Failed to fetch or process data: {str(e)[:1000]}")  # Log only the first 1000 characters
        frappe.throw(f"Failed to fetch or process data: {str(e)[:1000]}")  # Show only the first 1000 characters in the throw message

def check_and_update_item(api_keys, item_dict):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
    }
    server = f"http://102.22.220.246/api/resource/Item/{item_dict['item_code']}"
    get_response = requests.get(server, headers=headers)

    # Check if the item exists
    if get_response.status_code == 200:
        item_data = get_response.json().get("data", {})
        if not item_data.get("valuation_rate") or item_data["valuation_rate"] != item_dict["valuation_rate"]:
            # Update the item with the correct valuation_rate
            update_data = {
                "valuation_rate": item_dict["valuation_rate"]
            }
            update_response = requests.put(server, headers=headers, data=json.dumps(update_data))
            update_response.raise_for_status()
        return True
    return False

def create_item(api_keys, item_dict):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
    }
    server = "http://102.22.220.246/api/resource/Item"
    post_response = requests.post(server, headers=headers, data=json.dumps(item_dict))
    post_response.raise_for_status()
