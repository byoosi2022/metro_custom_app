import json
import requests

def post_item(doc, method):
    if doc.custom_post:
        url = "https://reigns.byoosi.com/api/resource/Item"
        secret_key = "e78af8566a7d06b"
        api_key = "d0645525fb61106"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {api_key}:{secret_key}"
        }

        data = {
            "data": {
                "item_code": doc.item_code,
                "item_name": doc.item_name,
                "item_group": doc.item_group
            }
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            print("Item posted successfully in the other ERPNext system.")
        except Exception as e:
            print(f"Failed to post item: {e}")