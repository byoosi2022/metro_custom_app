import json
import requests
import frappe
from metro_custom_app.utils import get_api_keys1

def get_item_price(item_code, price_list, headers):
    try:
        response = requests.get(f"http://102.22.220.246/api/resource/Item Price/{item_code}?filters=[['price_list', '=', '{price_list}']]", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            return None  # Item price does not exist
        frappe.log_error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise

@frappe.whitelist()
def create_or_update_item_price(docname):
    try:
        api_keys = get_api_keys1()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        item_price_doc = frappe.get_doc("Item Price", docname)

        post_data = {
            "price_list": item_price_doc.price_list,
            "item_code": item_price_doc.item_code,
            "price_list_rate": item_price_doc.price_list_rate,
            "uom": item_price_doc.uom
        }

        json_data = json.dumps(post_data)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://102.216.33.196/api/resource"

        # Check if the item price exists
        existing_item_price = get_item_price(item_price_doc.item_code, item_price_doc.price_list, headers)

        if existing_item_price:
            # Item price exists, update it
            put_response = requests.put(f"{server}/Item Price/{existing_item_price[0]['name']}", headers=headers, data=json_data)
            put_response.raise_for_status()
            frappe.msgprint(f"Item Price for '{item_price_doc.item_code}' updated successfully.")
        else:
            # Item price does not exist, create it
            post_response = requests.post(f"{server}/Item Price", headers=headers, data=json_data)
            post_response.raise_for_status()
            frappe.msgprint("Item Price created successfully")
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to fetch or process data: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to fetch or process data: {err}")
