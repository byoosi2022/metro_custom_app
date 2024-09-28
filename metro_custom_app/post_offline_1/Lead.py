import requests
import json
import frappe
from metro_custom_app.utils import get_api_keys1

@frappe.whitelist()
def create_lead():
    try:
        # Retrieve API keys
        api_keys = get_api_keys1()
        if not api_keys or not api_keys[0]:
            frappe.msgprint("Failed to get API keys for the server")
            return

        # Prepare Lead data
        lead_data = {
            "lead_name": "John Doe",
            "first_name": "John Doe",
            "company_name": "Example Company",
            "status": "Lead"
        }

        # Convert lead_data to JSON
        json_data = json.dumps(lead_data)

        # Define request headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_keys[0][0]}:{api_keys[0][1]}"
        }

        # API endpoint URL
        server_url = "http://102.216.33.196/api/resource/Lead"

        # Make POST request to create the Lead
        response = requests.post(server_url, headers=headers, data=json_data)

        # Check if request was successful
        response.raise_for_status()

        # Get response data
        response_data = response.json()

        # Print the ID or some identifier from the response
        frappe.msgprint(f"Lead created successfully with ID: {response_data.get('name')}")
    except requests.exceptions.HTTPError as http_err:
        frappe.log_error(f"HTTP error occurred: {http_err}")
        frappe.throw(f"Failed to create Lead: {http_err}")
    except Exception as err:
        frappe.log_error(f"Other error occurred: {err}")
        frappe.throw(f"Failed to create Lead: {err}")
