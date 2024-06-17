import frappe
from frappe import throw, msgprint, _

@frappe.whitelist(allow_guest=True)
def login(usr, pwd):
    try:
        login_manager = frappe.auth.LoginManager()
        login_manager.authenticate(user=usr, pwd=pwd)
        login_manager.post_login()
    except frappe.exceptions.AuthenticationError:
        frappe.clear_messages()
        frappe.local.response["message"] = {
            "success_key": 0,
            "message": "Authentication Failed"
        }
        return

    user = frappe.get_doc('User', frappe.session.user)

    # Generate a new API secret key for the user
    new_api_secret = user.custom_secret

    frappe.response["message"] = {
        "sid": frappe.session.sid,
        "user": user.name,
        "api_key": user.api_key,
        "api_secret": new_api_secret
    }
    return

def generate_api_secret(user):
    api_secret = frappe.generate_hash(length=15)
    return api_secret

