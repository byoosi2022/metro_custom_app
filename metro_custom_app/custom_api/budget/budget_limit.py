import frappe

def validate_budget(doc, method):
    if doc.doctype in ["Purchase Order", "Purchase Invoice", "Expense Claim"]:
        validate_document_budget(doc)

def validate_document_budget(doc):
    expense_accounts = get_expense_accounts(doc)
    total_spent = get_total_spent(doc.cost_center, doc.doctype, expense_accounts)

    if doc.doctype in ["Purchase Order", "Purchase Invoice"]:
        for item in doc.items:
            item_code = item.get('item_code')
            if item_code:
                expense_account = frappe.db.get_value('Item Default', 
                                                       {'parent': item_code, 'company': doc.company}, 
                                                       'expense_account')
                if not expense_account:
                    frappe.throw(f"Expense account not found for item '{item_code}' in company '{doc.company}'. Budget validation cannot proceed.")
                
                budget_limit = get_budget_limit(doc.cost_center, expense_account)
                
                # Skip validation if no budget is set (budget_limit == 0)
                if budget_limit == 0:
                    continue  # No budget, so skip this item
                
                # Calculate item total for validation
                item_total = item.get('amount')  # Assuming you have an 'amount' field in your item
                if (total_spent + item_total) > budget_limit:
                    currency = frappe.get_cached_value('Company', doc.company, 'default_currency')
                    formatted_total = "{:,.2f} {}".format(total_spent + item_total, currency)
                    formatted_budget_limit = "{:,.2f} {}".format(budget_limit, currency)

                    frappe.throw(f"Budget exceeded! Total amount {formatted_total} exceeds {formatted_budget_limit} available budget for item code '{item_code}' on account '{expense_account}'.")

    elif doc.doctype == "Expense Claim":
        expense_details = frappe.get_all('Expense Claim Detail',
                                         filters={'parent': doc.name},
                                         fields=['expense_type', 'sanctioned_amount', 'cost_center'])
        for detail in doc.expenses:
            expense_type = detail.get('expense_type')
            amount = detail.get('sanctioned_amount')
            claimdetail_cost_center = detail.get('cost_center')  # Child cost center
        
            expense_account = frappe.db.get_value('Expense Claim Account', {'parent': expense_type}, 'default_account')
            if not expense_account:
                frappe.throw(f"Default account not found for expense type '{expense_type}'. Budget validation cannot proceed.")

            budget_limit = get_budget_limit(claimdetail_cost_center, expense_account)

            # Skip validation if no budget is set
            if budget_limit == 0:
                continue  # No budget, so skip this expense

            total_spent_claims = get_total_spent(claimdetail_cost_center, doc.doctype, [expense_account], claimdetail_cost_center)

            current_total_spent = total_spent_claims + amount

            if current_total_spent > budget_limit:
                currency = frappe.get_cached_value('Company', doc.company, 'default_currency')
                formatted_total = "{:,.2f} {}".format(current_total_spent, currency)
                formatted_budget_limit = "{:,.2f} {}".format(budget_limit, currency)

                frappe.throw(f"Budget exceeded! Total amount {formatted_total} exceeds {formatted_budget_limit} available budget for Expense Claim Type '{expense_type}' on account '{expense_account}'.")

def get_expense_accounts(doc):
    expense_accounts = []
    
    if doc.doctype in ["Purchase Order", "Purchase Invoice"]:
        for item in doc.items:
            item_code = item.get('item_code')
            if item_code:
                expense_account = frappe.db.get_value('Item Default', 
                                                       {'parent': item_code, 'company': doc.company}, 
                                                       'expense_account')
                if expense_account and expense_account not in expense_accounts:
                    expense_accounts.append(expense_account)
    
    elif doc.doctype == "Expense Claim":
        # Get the expense claim type from the child table
        expense_claim_type = frappe.get_all('Expense Claim Detail',
                                              filters={'parent': doc.name},
                                              fields=['expense_type'])

        if expense_claim_type:
            expense_claim_accounts = frappe.get_all('Expense Claim Account',
                                                    filters={'parent': expense_claim_type[0].get('expense_type')},
                                                    fields=['default_account'])

            # Collect unique default accounts
            expense_accounts = list(set([acc.get('default_account') for acc in expense_claim_accounts if acc.get('default_account')]))

    return expense_accounts  # Return unique expense accounts

def get_budget_limit(cost_center, expense_account):
    budget_amount = frappe.db.sql(""" 
        SELECT SUM(ba.budget_amount)
        FROM `tabBudget` b
        JOIN `tabBudget Account` ba ON ba.parent = b.name
        WHERE b.cost_center = %s AND ba.account = %s
    """, (cost_center, expense_account))

    return budget_amount[0][0] if budget_amount and budget_amount[0][0] else 0

def get_total_spent(cost_center, doctype, expense_accounts, detail_cost_center=None):
    total_spent = 0

    if not expense_accounts:
        return total_spent
    
    # Create a string with the correct number of placeholders for the expense accounts
    placeholders = ', '.join(['%s'] * len(expense_accounts))
    
    if doctype == "Purchase Order":
        # Calculate total spent per item in Purchase Orders
        total_spent = frappe.db.sql(f"""
            SELECT COALESCE(SUM(poi.amount), 0)
            FROM `tabPurchase Order` po
            JOIN `tabPurchase Order Item` poi ON poi.parent = po.name
            WHERE po.cost_center = %s AND po.docstatus = 1
            AND poi.expense_account IN ({placeholders})
        """, (cost_center, *expense_accounts))[0][0]

    elif doctype == "Purchase Invoice":
        # Calculate total spent per item in Purchase Invoices
        total_spent = frappe.db.sql(f"""
            SELECT COALESCE(SUM(pii.amount), 0)
            FROM `tabPurchase Invoice` pi
            JOIN `tabPurchase Invoice Item` pii ON pii.parent = pi.name
            WHERE pi.cost_center = %s AND pi.docstatus = 1
            AND pii.expense_account IN ({placeholders})
        """, (cost_center, *expense_accounts))[0][0]

    elif doctype == "Expense Claim":
        # Calculate total spent for each expense type in Expense Claims
        total_spent = frappe.db.sql(f"""
            SELECT COALESCE(SUM(scd.sanctioned_amount), 0) AS total_amount
            FROM `tabExpense Claim Detail` scd
            JOIN `tabExpense Claim Account` scc ON scc.parent = scd.expense_type
            JOIN `tabExpense Claim` ec ON ec.name = scd.parent
            WHERE ec.cost_center = %s AND ec.docstatus = 1
            AND scc.default_account IN ({placeholders})
        """, (cost_center, *expense_accounts))

        # Format the result as a single value
        total_spent = total_spent[0][0] if total_spent else 0

    return total_spent
