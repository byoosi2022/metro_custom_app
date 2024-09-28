import json
import requests
import frappe
from metro_custom_app.utils import get_api_keys2

class PurchaseOrderItem:
    def __init__(self, item_code, custom_sales_price, uom):
        self.item_code = item_code
        self.custom_sales_price = custom_sales_price
        self.uom = uom

    def to_dict(self):
        return {
            "item_code": self.item_code,
            "custom_sales_price": self.custom_sales_price,
            "uom": self.uom,
        }

def ensure_item_exists(item_code, uom, headers, server):
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

def ensure_item_price(item_code, custom_sales_price, uom, headers, server):
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
                "price_list_rate": custom_sales_price
            }
            response = requests.put(f"{server}/Item Price/{item_price_name}", headers=headers, data=json.dumps(item_price_data))
        else:
            # Create a new item price
            item_price_data = {
                "doctype": "Item Price",
                "price_list": "Standard Selling",
                "item_code": item_code,
                "price_list_rate": custom_sales_price,
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
        api_keys = get_api_keys2()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        purchase_order = frappe.get_doc("Purchase Order", docname)

        # Convert items to a list of dictionaries
        items = [PurchaseOrderItem(item.item_code, item.custom_sales_price, item.uom).to_dict() for item in purchase_order.items]

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://168.253.118.177/api/resource"

        # Ensure each item exists
        for item in items:
            ensure_item_exists(item["item_code"], item["uom"], headers, server)
            ensure_item_price(item["item_code"], item["custom_sales_price"], item["uom"], headers, server)

        frappe.msgprint("Item Prices submitted/updated successfully to the server")

    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to fetch or process data: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to fetch or process data: {err}")
