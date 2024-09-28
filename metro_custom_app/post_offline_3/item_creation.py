import frappe
import requests
import json
from metro_custom_app.utils import get_api_keys2

@frappe.whitelist()
def create_item(docname):
    try:
        api_keys = get_api_keys2()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        item_doc = frappe.get_doc("Item", docname)

        post_data = {
            "item_code": item_doc.item_code,
            "item_name": item_doc.item_name,
            "description": item_doc.description,
            "item_group": item_doc.item_group,
            "is_stock_item": item_doc.is_stock_item,  # Set to 1 if the item is a stock item
            "stock_uom": item_doc.stock_uom,   # Set the stock unit of measure
            "custom_company": item_doc.custom_company, 
            "custom_item_group_code": item_doc.custom_item_group_code,
        }

        json_data = json.dumps(post_data)

        # Make the request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://168.253.118.177/api/resource"

        # Check if the item already exists
        if not exists(item_doc.item_code, headers, server):
            # Create the item if it doesn't exist
            post_response = requests.post(f"{server}/Item", headers=headers, data=json_data)
            post_response.raise_for_status()
            posted_item = post_response.json().get("data", {}).get("name")

            # Update the document status
            if posted_item:
                frappe.db.set_value("Item", docname, "custom_post_status1", "Receipt Posted To server 2")
                frappe.db.commit()
                frappe.msgprint("Item submitted successfully to the server")
            else:
                frappe.msgprint("Failed to post Purchase Receipt")
        else:
            # Update the item if it exists
            patch_response = requests.put(f"{server}/Item/{item_doc.item_code}", headers=headers, json=post_data)
            patch_response.raise_for_status()
            frappe.msgprint(f"Item '{item_doc.item_code}' updated successfully.")
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to fetch or process data: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to fetch or process data: {err}")

def exists(item_code, headers, server):
    try:
        # Check if the item exists
        response = requests.get(f"{server}/Item/{item_code}", headers=headers)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise
