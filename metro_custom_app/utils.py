import json
import requests
import frappe

@frappe.whitelist()
def get_api_keys():
    username = frappe.session.user
    pwd = frappe.get_doc("User", username)
    password = pwd.get("custom_password")
    
    server = "http://102.22.220.246"
    
    url_login = f"{server}/api/method/offline_posting.custom_post.auth.login?usr={username}&pwd={password}"
    response_login = requests.get(url_login)
    result_login = response_login.json()
    api_key = result_login.get("message", {}).get("api_key")
    secret_key = result_login.get("message", {}).get("api_secret")
    
    if not api_key or not secret_key:
        frappe.msgprint(f"Failed to get API keys for {server}")
        return None, None
    
    return [(api_key, secret_key)]

@frappe.whitelist()
def get_api_keys1():
    username = frappe.session.user
    pwd = frappe.get_doc("User", username)
    password = pwd.get("custom_password")
    
    server = "http://102.216.33.196"
    
    url_login = f"{server}/api/method/offline_posting.custom_post.auth.login?usr={username}&pwd={password}"
    response_login = requests.get(url_login)
    result_login = response_login.json()
    api_key = result_login.get("message", {}).get("api_key")
    secret_key = result_login.get("message", {}).get("api_secret")
    
    if not api_key or not secret_key:
        frappe.msgprint(f"Failed to get API keys for {server}")
        return None, None
    
    return [(api_key, secret_key)]


# import json
# import requests
# import frappe

# @frappe.whitelist()
# def get_api_keys_servers():
#     username = frappe.session.user
#     pwd = frappe.get_doc("User", username)
#     password = pwd.get("custom_password")
    
#     servers = [
#         "http://102.22.220.246",
#         "http://102.216.33.196",
   
#     ]
    
#     api_keys = []
#     for server in servers:
#         url_login = f"{server}/api/method/offline_posting.custom_post.auth.login?usr={username}&pwd={password}"
#         response_login = requests.get(url_login)
#         result_login = response_login.json()
#         api_key = result_login.get("message", {}).get("api_key")
#         secret_key = result_login.get("message", {}).get("api_secret")
        
#         if not api_key or not secret_key:
#             frappe.msgprint(f"Failed to get API keys for {server}")
#             return None, None
        
#         api_keys.append((api_key, secret_key))
    
#     return api_keys
