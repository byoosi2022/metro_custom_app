import json
import requests
import frappe
from datetime import datetime
from metro_custom_app.utils import get_api_keys2  # Import the function to fetch API keys

class StockReconciliationItem:
    def __init__(self, item_code, qty,warehouse):
        self.item_code = item_code
        self.qty = qty
        self.warehouse = warehouse
 
    def to_dict(self):
        return {
            "item_code": self.item_code,
            "qty": self.qty,
            "warehouse": self.warehouse,
        }

@frappe.whitelist()
def post_stock_reconciliation(docname):
    try:
        api_keys = get_api_keys2()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        stock_reconciliation = frappe.get_doc("Stock Reconciliation", docname)
        
        # Check if the Stock Entry has already been posted
        if stock_reconciliation.custom_voucher_no_server3:
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
                "warehouse": item.warehouse
              
            }
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
            "docstatus":1,
            "items": items
        }

        json_data = json.dumps(post_data)

        # Make the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://168.253.118.177/api/resource/Stock%20Reconciliation"
        post_response = requests.post(server, headers=headers, data=json_data)

        # Check the response
        post_response.raise_for_status()
        posted_reconciliation = post_response.json().get("data", {}).get("name")

        # Update the document status
        if posted_reconciliation:
            frappe.db.set_value("Stock Reconciliation", docname, "custom_voucher_no_server3", posted_reconciliation)
            # frappe.db.set_value("Stock Reconciliation", docname, "custom_post_status", "Reconciliation Posted")
            frappe.msgprint("Stock Reconciliation submitted successfully to the server")
        else:
            frappe.db.set_value("Stock Reconciliation", docname, "custom_post_status", "Reconciliation Not Posted")
            frappe.msgprint("Failed to post Stock Reconciliation")

    except Exception as e:
        frappe.log_error(f"Failed to fetch or process data: {e}")
        frappe.throw(f"Failed to fetch or process data: {e}")
