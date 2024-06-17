import json
import requests
import frappe
from metro_custom_app.utils import get_api_keys1  # Import the function to fetch API keys


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
def post_stock_entry(docname):
    try:
        api_keys = get_api_keys1()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        stock_entry = frappe.get_doc("Stock Entry", docname)

        # Check if the Stock Entry has already been posted
        if stock_entry.custom_offline_voucher_no1:
            frappe.msgprint("Stock Entry has already been posted.")
            return

        # Extract necessary information from items
        items = []
        for item in stock_entry.items:
            item_dict = {
                "item_code": item.item_code,
                "cost_center": item.cost_center,
                "qty": item.qty,
                "expense_account": item.expense_account,
                "s_warehouse": item.s_warehouse,
                "t_warehouse": item.t_warehouse,
                "uom": item.uom,
                "conversion_factor": item.conversion_factor,
                "transfer_qty": item.transfer_qty,
                "basic_rate": item.basic_rate,
                "basic_amount": item.basic_amount,
                "amount": item.amount,
                "batch_no": item.batch_no,
                # Add more fields as needed
            }
            items.append(item_dict)

        post_data = {
            "posting_date": str(stock_entry.posting_date),
            "posting_time": str(stock_entry.posting_time),
            "company": stock_entry.company,
            "from_warehouse": stock_entry.from_warehouse,
            "to_warehouse": stock_entry.to_warehouse,
            "stock_entry_type": stock_entry.stock_entry_type,
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
        server = "http://102.216.33.196/api/resource"

        # Ensure each item exists
        for item in items:
            ensure_item_exists(item["item_code"], headers, server)

        # Remove the 'Expect' header
        headers.pop('Expect', None)

        post_response = requests.post(f"{server}/Stock%20Entry", headers=headers, data=json_data)

        # Check the response
        post_response.raise_for_status()
        posted_stock_entry = post_response.json().get("data", {}).get("name")

        # Update the document status
        if posted_stock_entry:
            frappe.db.set_value("Stock Entry", docname, "custom_offline_voucher_no1", posted_stock_entry)
            # frappe.db.set_value("Stock Entry", docname, "custom_post_status1", "Stock Entry Posted to server1")
            frappe.msgprint("Stock Entry submitted successfully to the server")
        else:
            frappe.db.set_value("Stock Entry", docname, "custom_post_status", "Stock Entry Not Posted")
            frappe.msgprint("Failed to post Stock Entry")

    except requests.exceptions.RequestException as e:
        frappe.log_error(f"HTTP error occurred: {e}")
        frappe.throw(f"HTTP error occurred: {e}")
    except Exception as e:
        frappe.log_error(f"Failed to fetch or process data: {e}")
        frappe.throw(f"Failed to fetch or process data: {e}")
