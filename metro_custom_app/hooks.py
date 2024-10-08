app_name = "metro_custom_app"
app_title = "Metro Custom App"
app_publisher = "mututa paul"
app_description = "all the customizations here"
app_email = "mututapaul02@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/metro_custom_app/css/metro_custom_app.css"
# app_include_js = "/assets/metro_custom_app/js/metro_custom_app.js"
app_include_js = "/assets/metro_custom_app/js/custom/button.js"

# include js, css files in header of web template
# web_include_css = "/assets/metro_custom_app/css/metro_custom_app.css"
# web_include_js = "/assets/metro_custom_app/js/metro_custom_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "metro_custom_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "metro_custom_app.utils.jinja_methods",
# 	"filters": "metro_custom_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "metro_custom_app.install.before_install"
# after_install = "metro_custom_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "metro_custom_app.uninstall.before_uninstall"
# after_uninstall = "metro_custom_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "metro_custom_app.utils.before_app_install"
# after_app_install = "metro_custom_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "metro_custom_app.utils.before_app_uninstall"
# after_app_uninstall = "metro_custom_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "metro_custom_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events
doc_events = {
    'Purchase Order': {
        'before_save': "metro_custom_app.custom_api.budget.budget_limit.validate_budget",
        'on_submit': [
            "metro_custom_app.custom_api.purchase_order.update_item_price",
            "metro_custom_app.custom_api.update_margin_percent.profit_margin_percentage",
        ]
    },
    'Purchase Invoice': {
        'before_save': "metro_custom_app.custom_api.budget.budget_limit.validate_budget"
    },
    'Expense Claim': {
        'before_save': "metro_custom_app.custom_api.budget.budget_limit.validate_budget"
    },
    'Sales Order': {
        'on_submit': "metro_custom_app.api.create_purchase_invoice"
    },
    'Sales Invoice': {
        'on_submit': [
            "metro_custom_app.api.create_purchase_invoice",
            "metro_custom_app.api.create_purchase_invoice_landlord"
        ],
        'validate': "metro_custom_app.custom_api.validate_drafts.validate_sales_invoice"
    },
    'Payment Request': {
        'onload': "metro_custom_app.custom_api.update_status.update_custom_status"
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"metro_custom_app.tasks.all"
# 	],
# 	"daily": [
# 		"metro_custom_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"metro_custom_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"metro_custom_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"metro_custom_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "metro_custom_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "metro_custom_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "metro_custom_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["metro_custom_app.utils.before_request"]
# after_request = ["metro_custom_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["metro_custom_app.utils.before_job"]
# after_job = ["metro_custom_app.utils.after_job"]

# User Data Protection
# --------------------

fixtures = [
    {"dt": "Client Script", "filters": [["module", "=", "Metro Custom App"]]},
    {"dt": "Custom Field", "filters": [["module", "=", "Metro Custom App"]]}
]


# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"metro_custom_app.auth.validate"
# ]
