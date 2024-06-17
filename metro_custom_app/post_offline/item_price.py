import json
import requests
import frappe
from metro_custom_app.utils import get_api_keys

def ensure_item_exists(server, headers, item_code, uom):
    try:
        response = requests.get(f"{server}/Item/{item_code}", headers=headers)
        if response.status_code == 404:
            item_data = {
                "doctype": "Item",
                "item_code": item_code,
                "item_name": item_code,
                "item_group": "All Item Groups",
                "stock_uom": uom,
                "description": "Auto-created item"
            }
            response = requests.post(f"{server}/Item", headers=headers, data=json.dumps(item_data))
            response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise

def ensure_item_price(server, headers, item_code, uom, rate):
    try:
        # Check if the item price exists
        response = requests.get(f"{server}/Item Price", headers=headers, params={
            "filters": json.dumps([
                ["item_code", "=", item_code],
                ["uom", "=", uom],
                ["price_list", "=", "Standard Selling"]
            ])
        })

        item_prices = response.json().get('data', [])

        if item_prices:
            # Update the existing item price
            item_price_name = item_prices[0].get('name')
            item_price_data = {
                "price_list_rate": rate
            }
            response = requests.put(f"{server}/Item Price/{item_price_name}", headers=headers, data=json.dumps(item_price_data))
        else:
            # Create a new item price
            item_price_data = {
                "doctype": "Item Price",
                "price_list": "Standard Selling",
                "item_code": item_code,
                "price_list_rate": rate,
                "uom": uom
            }
            response = requests.post(f"{server}/Item Price", headers=headers, data=json.dumps(item_price_data))

        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise

@frappe.whitelist()
def post_item_price(docname):
    try:
        api_keys = get_api_keys()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        item_price = frappe.get_doc("Item Price", docname)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://102.22.220.246/api/resource"

        ensure_item_exists(server, headers, item_price.item_code, item_price.uom)
        ensure_item_price(server, headers, item_price.item_code, item_price.uom, item_price.price_list_rate)

        frappe.msgprint("Item Prices submitted/updated successfully to the server")

    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to fetch or process data: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to fetch or process data: {err}")
