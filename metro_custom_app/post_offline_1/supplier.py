import json
import requests
import frappe
from metro_custom_app.utils import get_api_keys1

def get_supplier(supplier_name, headers):
    try:
        response = requests.get(f"http://102.216.33.196/api/resource/Supplier/{supplier_name}", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        if http_err.response.status_code == 404:
            return None  # Supplier does not exist
        frappe.log_error(f"HTTP error occurred: {http_err}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise

@frappe.whitelist()
def create_or_update_supplier(docname):
    try:
        api_keys = get_api_keys1()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        supplier_doc = frappe.get_doc("Supplier", docname)

        post_data = {
            "supplier_name": supplier_doc.supplier_name,
            "supplier_type": supplier_doc.supplier_type,
            "custom_company": supplier_doc.custom_company,
            "country": supplier_doc.country,
            "supplier_group": supplier_doc.supplier_group
        }

        json_data = json.dumps(post_data)

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://102.216.33.196/api/resource"

        # Check if the supplier exists
        existing_supplier = get_supplier(supplier_doc.supplier_name, headers)

        if existing_supplier:
            # Supplier exists, update it
            put_response = requests.put(f"{server}/Supplier/{supplier_doc.supplier_name}", headers=headers, data=json_data)
            put_response.raise_for_status()
            frappe.msgprint(f"Supplier '{supplier_doc.supplier_name}' updated successfully.")
        else:
            # Supplier does not exist, create it
            post_response = requests.post(f"{server}/Supplier", headers=headers, data=json_data)
            post_response.raise_for_status()
            frappe.msgprint("Supplier created successfully")
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to fetch or process data: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to fetch or process data: {err}")
