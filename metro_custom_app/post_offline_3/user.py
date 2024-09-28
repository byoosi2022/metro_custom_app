import json
import requests
import frappe
from metro_custom_app.utils import get_api_keys2

def ensure_user_exists_or_update(server, headers, user_data):
    try:
        response = requests.get(f"{server}/User/{user_data['name']}", headers=headers)
        if response.status_code == 200:
            # Update existing user
            response = requests.put(f"{server}/User/{user_data['name']}", headers=headers, data=json.dumps(user_data))
        elif response.status_code == 404:
            # Create new user
            response = requests.post(f"{server}/User", headers=headers, data=json.dumps(user_data))
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err} - Response: {response.text}")
        raise
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        raise

@frappe.whitelist()
def post_users(docname):
    try:
        api_keys = get_api_keys2()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        user_doc = frappe.get_doc("User", docname)

        user_data = {
            "name": user_doc.name,
            "email": user_doc.email,
            "first_name": user_doc.first_name,
            "last_name": user_doc.last_name,
            "middle_name": user_doc.middle_name,
            "enabled": user_doc.enabled,
            "user_type": user_doc.user_type,
            "role_profile_name": user_doc.role_profile_name
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }
        server = "http://168.253.118.177/api/resource"

        ensure_user_exists_or_update(server, headers, user_data)

        frappe.msgprint("User submitted/updated successfully to the server")

    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to fetch or process data: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to fetch or process data: {err}")
